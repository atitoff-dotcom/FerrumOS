# Справочник API скриптов FerrumOS (JavaScript / Rhai)

**FerrumOS** предоставляет высокопроизводительный, удобный для разработчика **JavaScript-совместимый слой скриптинга**, работающий поверх движка Rhai в нативном `no_std` окружении микроконтроллера.

---

## ⚡ Модель выполнения: Zero-Cost Сопрограммы (Coroutines)

FerrumOS использует **кооперативную модель многозадачности на базе конечных автоматов (State Machine Coroutines)** без тяжелых потоков операционной системы (FreeRTOS):

* **Линейный и понятный JS-код:** Вы пишете простой синхронный код (`delay_ms(500);`, `let line = device.uart("GPS").read_line(1000);`) без callback hell и оверхеда на `async/await`.
* **Неблокирующее ядро:** При вызове `delay_ms()` или ожидании очередей/UART скрипт мгновенно делает `yield` и отдает процессорное время в главный цикл ядра.
* **Параллельная работа:** Сетевой стек Wi-Fi, HTTP REST сервер и соседние скрипты продолжают работать на полной скорости без задержек.

```javascript
// Простой линейный цикл — не блокирует ядро и другие задачи!
loop {
    device.gpio("StatusLED").write(true);
    delay_ms(200); // Мгновенный yield ядра
    device.gpio("StatusLED").write(false);
    delay_ms(800);
}
```

---

## 🖥️ Консоль и системное логирование

### `console.log(message)`
Выводит информационное сообщение в системный лог UART (115200 baud) и Web-консоль.

```javascript
console.log("FerrumOS: система успешно инициализирована");
console.log("Текущее значение температуры: " + temp + " °C");
```

### `console.error(message)`
Выводит сообщение об ошибке с повышенным приоритетом.

```javascript
console.error("Критический сбой чтения шины I2C!");
```

---

## 🧮 Математический объект (`Math`)

Стандартные математические операции над целыми и вещественными числами:

- `Math.round(x)` — Округление до ближайшего целого.
- `Math.floor(x)` — Округление вниз.
- `Math.ceil(x)` — Округление вверх.
- `Math.abs(x)` — Модуль числа (абсолютное значение).
- `Math.max(a, b)` — Максимум из двух чисел.
- `Math.min(a, b)` — Минимум из двух чисел.
- `Math.pow(base, exp)` — Возведение в степень base^exp.
- `Math.sqrt(x)` — Квадратный корень.

```javascript
let raw_val = 24.78;
let rounded = Math.round(raw_val); // 25
let peak = Math.max(rounded, 30);  // 30
```

---

## 📦 Сериализация JSON (`JSON`)

### `JSON.stringify(object)`
Преобразует объект, карту (map) или массив в строку формата JSON.

```javascript
let telemetry = #{
    device_id: "ESP32C6_01",
    temperature: 24.5,
    humidity: 58,
    relay_state: true
};
let payload = JSON.stringify(telemetry);
mqtt.publish("ferrumos/sensors", payload);
```

### `JSON.parse(string)`
Парсит строку JSON в структуру данных.

```javascript
let cmd = JSON.parse(incoming_json_str);
if cmd.action == "TOGGLE_RELAY" {
    device.gpio("Relay1").write(cmd.state);
}
```

---

## 🗄️ Межскриптовое взаимодействие (IPC) и Реактивный стейт (`ipc` & `state`)

Потокобезопасная шина межпроцессного взаимодействия ядра FerrumOS для обмена данными между изолированными скриптами:

### 1. Единая публикация (`ipc.publish`)
Атомарная операция: одновременно помещает событие в FIFO-очередь подписчиков **и** сохраняет последнее актуальное значение в глобальный регистр состояния:

```javascript
// Скрипт-поставщик (например, climate_producer.js)
let temp = 24;
ipc.publish("temp_stream", temp);
```

---

### 2. MPSC FIFO-очереди сообщений (`ipc.send`, `ipc.recv`, `ipc.available`, `ipc.wait`)
Очереди сообщений для событийной модели (Multi-Producer, Single-Consumer). Кольцевой буфер в ядре Rust защищает память RAM чипа:

```javascript
// Отправка в именованную очередь
ipc.send("temp_stream", 25);

// Реактивное событийно-ориентированное ожидание (0% CPU idle):
// Задача мгновенно засыпает в ядре и просыпается сразу при публикации сообщения (или таймауте)
let t = ipc.wait("temp_stream", 5000);

if (t != 0) {
    if (t < 22) {
        rgb.set(8, 0, 0, 255); // Синий (холодно)
    }
}
```

---

### 3. Разделяемое реактивное состояние (`state.set`, `state.get`)
Глобальный регистр последних значений (Pub/Sub):

```javascript
// Сохранение значения в стейт
state.set("target_temp", 22);

// Чтение актуального значения в любой момент времени
let target = state.get("target_temp");
```
    temp: 23.4,
    timestamp: 1724500000
});

// Скрипт 2: Неблокирующее чтение с таймаутом (в миллисекундах)
let msg = queue.receive("telemetry_channel", 1000);
if msg != () {
    console.log("Получено сообщение от датчика: " + msg.temp);
}
```

### 2. Реактивная шина событий (`events`)
Архитектура Pub/Sub для широковещательных уведомлений:

```javascript
// Генерация события
events.emit("security/alarm", #{ zone: "warehouse", level: 2 });

// Подписка на событие
events.on("security/alarm", |data| {
    console.log("ВНИМАНИЕ! Сработала тревога в зоне: " + data.zone);
    device.gpio("SirenRelay").write(true);
});
```

---

---

## 🔌 Аппаратный API устройств (`gpio` & `device`)

### Конфигурация и управление цифровыми пинами (`gpio`)
FerrumOS поддерживает детальную настройку схемотехники выводов (Push-Pull / Open-Drain, подтяжки Pull-Up / Pull-Down, начальный уровень). Конфигурация компилируется в **1 байт** битовой маски:

```javascript
// 1. Полная объектная конфигурация выхода:
gpio.mode(15, {
    direction: "output",      // "output" | "input"
    type: "push_pull",        // "push_pull" | "open_drain"
    pull: "none",             // "none" | "up" | "down"
    initial: 0                // 0 (Low / 0V) | 1 (High / 3.3V)
});

// 2. Удобные шорткаты:
gpio.output(15);                                     // Обычный выход (Push-Pull, Low)
gpio.output(8, { type: "open_drain", pull: "up" });  // Открытый сток с подтяжкой к 3.3V
gpio.input(9, { pull: "up" });                       // Вход с подтяжкой к 3.3V

// 3. Управление уровнем:
gpio.write(15, 1);
gpio.high(15);
gpio.low(15);
```

### Управление именованными пинами (`device.gpio`)
```javascript
// Запись логического уровня (true = 3.3V, false = 0V)
device.gpio("StatusLED").write(true);
device.gpio("Relay1").write(false);

// Чтение логического уровня с кнопки или датчика
let button_pressed = device.gpio("UserButton").read();
```

### ШИМ и Сервоприводы (PWM / LEDC)
```javascript
// Управление скважностью яркости LED (0..255)
device.pwm("DimmerLED").set_duty(128); // 50% яркости

// Управление углом поворота сервопривода (0..180 градусов)
device.pwm("CameraServo").set_angle(90);
```

### 1-Wire Датчики температуры (Dallas DS18B20)
```javascript
// Чтение температуры с точностью до 0.0625 °C
let t = device.ds18b20("TempProbe").read();
console.log("Температура теплоносителя: " + t + " °C");
```

### Шина I2C
```javascript
// Чтение регистров I2C: read(i2c_addr, reg_addr, byte_count)
let data = device.i2c("I2C0").read(0x76, 0xD0, 2);

// Запись в регистр I2C: write(i2c_addr, reg_addr, data_array)
device.i2c("I2C0").write(0x68, 0x10, [0x20, 0x80]);
```

### Шина SPI (E-Paper, дисплеи, Flash)
```javascript
// Полнодуплексная передача массива байтов
let rx = device.spi("SPI0").transfer([0x06, 0x00, 0x00]);
```

### Последовательный порт UART (GPS, датчики CO2, модемы)
```javascript
// Запись строки или байт
device.uart("GPS").write("$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29\r\n");

// Неблокирующее построчное чтение NMEA с таймаутом (мс)
let nmea_line = device.uart("GPS").read_line(500);
if nmea_line != () {
    console.log("NMEA: " + nmea_line);
}
```

---

## 🛠️ Динамическая привязка оборудования (Dynamic Pin Binding)

Скрипты могут самостоятельно объявлять и привязывать аппаратные пины при старте:

```javascript
// Привязка GPIO
bind_gpio_output("StatusLED", 15);
bind_gpio_input("UserButton", 9);

// Привязка ШИМ (LEDC): alias, pin, частота в Гц
bind_pwm("DimmerLED", 4, 5000);

// Привязка шины 1-Wire
bind_onewire_bus("TempProbe", 8);

// Привязка I2C (SDA, SCL)
bind_i2c_bus("I2C0", 6, 7);

// Привязка UART (TX, RX, Baudrate)
bind_uart("GPS", 16, 17, 9600);
```

---

## 🏭 Промышленный протокол Modbus RTU / TCP (`modbus`)

```javascript
// Чтение Holding Registers: read_holding(host_or_port, unit_id, start_reg, count)
let regs = modbus.read_holding("UART_RS485", 1, 0x0000, 4);
let voltage = regs[0] / 10.0;
let current = regs[1] / 100.0;
let active_power = regs[2];

// Запись одиночного регистра: write_single(host_or_port, unit_id, reg, value)
modbus.write_single("UART_RS485", 1, 0x0010, 1);
```

---

## 🏛️ Протокол Matter Smart Home (`matter`)

FerrumOS предоставляет нативную привязку к Matter Data Model. Идентификаторы эндпоинтов выделяются ядром автоматически:

```javascript
// 1. Создание эндпоинтов Matter
let light = matter.endpoint(matter.types.ON_OFF_LIGHT);
let temp_sensor = matter.endpoint(matter.types.TEMPERATURE_SENSOR);

// 2. Обработка команд от Apple Home / Home Assistant / Google Home
light.on_command("OnOff", |cmd| {
    if cmd == "On" {
        device.gpio("StatusLED").write(true);
        light.set("OnOff", true);
    } else {
        device.gpio("StatusLED").write(false);
        light.set("OnOff", false);
    }
});

// 3. Передача текущих показаний датчиков
temp_sensor.set("MeasuredValue", 2350); // 23.50 °C в сотых долях
```

---

## 📡 Сетевая телеметрия MQTT (`mqtt`)

```javascript
// Публикация в системный MQTT брокер
let payload = JSON.stringify(#{
    status: "HEALTHY",
    uptime_sec: 3600,
    free_ram: 312000
});
mqtt.publish("ferrumos/node_01/health", payload);
```

---

## 🛡️ Локальная обработка исключений (`try / catch`)

Перехват ошибок предотвращает остановку скрипта супервизором:

```javascript
try {
    let raw = device.i2c("I2C0").read(0x76, 0x00, 2);
    console.log("Датчик прочитан: " + raw);
} catch (err) {
    console.error("Ошибка опроса I2C: " + err);
    device.gpio("FaultLED").write(true);
}
```
