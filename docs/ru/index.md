<p align="center">
  <img src="../assets/logo.png" alt="FerrumOS Logo" width="130" height="130" style="border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);">
</p>

# FerrumOS

> **Реактивная микро-ОС и среда Live Hot-Swap для микроконтроллеров RISC-V и ESP32.**

[![Release: v0.6.0](https://img.shields.io/badge/Релиз-v0.6.0-blue.svg)](https://github.com/atitoff-dotcom/FerrumOS/releases)
[![Лицензия: Apache 2.0](https://img.shields.io/badge/Лицензия-Apache%202.0-green.svg)](https://github.com/atitoff-dotcom/FerrumOS/blob/master/LICENSE)
[![Платформа: Windows 10%2F11](https://img.shields.io/badge/Платформа-Windows%2010%2F11-0078D6.svg?logo=windows)](https://github.com/atitoff-dotcom/FerrumOS/releases)
[![Целевая архитектура: RISC-V](https://img.shields.io/badge/Архитектура-RISC--V%20(ESP32--C6%20%7C%20C3)-orange.svg)](https://github.com/atitoff-dotcom/FerrumOS#supported-hardware)

---

FerrumOS — это сверхбыстрая реактивная микро-операционная система прямого управления оборудованием (bare-metal) и среда живой разработки для устройств Интернета вещей (IoT), умного дома и сенсорных узлов.

Пишите на чистом **Modern JavaScript**, загружайте скрипты на работающий чип за **15 миллисекунд по USB или Wi-Fi без перезагрузки платы** и отслеживайте цифровой двойник периферии в реальном времени.

---

## ⚡ Быстрый переход

<div class="grid cards" markdown="1">

-   ### 🚀 Быстрый старт

    Прошивка платы и первый реактивный скрипт менее чем за 3 минуты.

    [**Начать обучение →**](1_getting_started/01_quickstart.md)

-   ### 📥 Скачать Studio

    Установщик для Windows или портативная версия без зависимостей.

    [**Скачать v0.6.0 →**](https://github.com/atitoff-dotcom/FerrumOS/releases)

-   ### 📖 Справочник JS API

    Полная спецификация атомарного цепочечного Fluent Chaining API.

    [**Открыть справочник →**](3_reference/js_api/index.md)

-   ### 📋 Реестр RFC

    Архитектурные предложения, новые протоколы (CAN, BSB/OpenTherm) и статусы.

    [**Смотреть RFC →**](rfcs/index.md)

</div>

---

## 📐 Fluent Chaining JavaScript API

FerrumOS строго следует стандарту **Fluent Chaining** для обеспечения абсолютной надежности и исключения аппаратных скачков напряжения (глитчей):

```javascript
// Атомарная инициализация выхода
const relay = GPIO.output(15)
    .openDrain(true)
    .pullUp()
    .invert(true)
    .initial(false);

// Аппаратный детектор жестов с нулевым расходом процессора
const btn = GPIO.input(9)
    .pullUp()
    .button()
    .clickMs(350)
    .doubleClickMs(250)
    .longPressMs(800);

// Реактивный цикл событий
while (true) {
    const gesture = btn.wait(); // Просыпается только при физическом нажатии

    if (gesture === Button.CLICK) {
        relay.write(!relay.read());
    }
}
```

---

## 🚀 Ключевые возможности

- **Мгновенный деплой Hot-Swap за 15 мс**: Обновление кода без перезагрузки платы, потери сетевых соединений или сброса калибровки датчиков.
- **Реактивный спящий процессор**: Процессор спит в глубоком энергосбережении и просыпается только по аппаратным очередям прерываний.
- **Цифровой двойник (Digital Twin)**: Наглядная схема пинов, уровней сигналов, коэффициентов заполнения ШИМ и напряжений АЦП в Studio.
- **Home Assistant MQTT Auto-Discovery**: Автоматическая публикация сенсоров и реле в Lovelace-дашборды без ручной правки YAML.
- **Атомарный I/O без глитчей**: Полная защита от дребезга и зависаний силовых ключей при реконфигурации.

---

## 🔌 Поддерживаемые платы

| Микроконтроллер / Плата | Архитектура ядра | Радиоинтерфейсы | Сценарии применения |
|---|---|---|---|
| **ESP32-C6 SuperMini** | RISC-V (rv32imac, 160 МГц) | Wi-Fi 6, 802.15.4 (Thread / Zigbee), BLE 5 | Thread роутер / конечное устройство, узлы Home Assistant |
| **ESP32-C3 DevKit** | RISC-V (rv32imc, 160 МГц) | Wi-Fi 4, BLE 5 | Автономные Wi-Fi сенсоры, умные реле |
| **BouffaloLab BL702** | RISC-V (rv32imac, 144 МГц) | Zigbee, BLE 5 | Батарейные BLE-метки, электронные ценники ESL |

---

## 🧭 Полный каталог документации

### 🚀 Начало работы
- [01. Быстрый старт](1_getting_started/01_quickstart.md) — Подключение платы и запуск первого реактивного скрипта.
- [02. Первый сенсор](1_getting_started/02_first_sensor.md) — Настройка шины I2C и чтение телеметрии климата.
- [03. Умная кнопка](1_getting_started/03_smart_button.md) — Аппаратный антидребезг и жесты (клики, удержание).
- [04. Решение проблем и FAQ](1_getting_started/04_troubleshooting.md) — USB-драйверы, доступ к COM-порту и прошивка.

### 💡 Рецепты и прикладные задачи
- [Интеграция с Home Assistant по MQTT](2_recipes/home_assistant_mqtt.md) — Zero-configuration MQTT Auto-Discovery.
- [Глубокий сон и батарейное питание](2_recipes/battery_deep_sleep.md) — Retention RAM, режим PDS и микроамперное потребление.
- [Межскриптовое взаимодействие (IPC)](2_recipes/inter_script_signals.md) — Неблокирующий обмен сигналами между задачами.
- [Сетевая шина CAN](2_recipes/can_networking.md) — Распределенный обмен сигналами между платами по TWAI.
- [Электронная бумага (E-Paper)](2_recipes/esl_display.md) — Дисплеи E-Ink с минимальным расходом памяти.
- [Беспроводное обновление (OTA)](2_recipes/ota_firmware_update.md) — Горячая замена байткода и отказоустойчивый A/B Dual-Boot.

### 📖 Справочник API
- [Обзор JavaScript Fluent API](3_reference/js_api/index.md) — Принципы атомарных цепочек методов.
- [Реактивные сигналы и IPC](3_reference/js_api/signals.md) — Межскриптовый обмен данными и подписчики `.watch()`.
- [GPIO (Цифровые пины)](3_reference/js_api/gpio.md) — Настройка входов, выходов, подтяжек и фильтров.
- [ADC (Аналоговые входы)](3_reference/js_api/adc.md) — Калибровка напряжений, аттенюация и оверсэмплинг.
- [Шина I2C](3_reference/js_api/i2c.md) — Транзакции Master, чтение и запись регистров сенсоров.
- [Шина SPI](3_reference/js_api/spi.md) — Скоростная передача данных для экранов и памяти.
- [PWM и WS2812](3_reference/js_api/pwm_ws2812.md) — Аппаратный ШИМ и адресные светодиодные ленты.
- [Питание и сон](3_reference/js_api/power_sleep.md) — Управление энергосбережением и источниками пробуждения.
- [Сеть Thread](3_reference/js_api/thread_network.md) — Mesh-сети 802.15.4 и протоколы CoAP/UDP.
- [UART и Modbus](3_reference/js_api/uart_modbus.md) — Последовательные порты и опрос устройств Modbus RTU.
- [Справочник Ferrum CLI](3_reference/cli.md) — Консольные команды сборки, прошивки и деплоя.

### ⚙️ Концепции и архитектура
- [Стандарт Fluent Chaining](4_concepts/fluent_chaining.md) — Почему цепочки исключают аппаратные глитчи на пинах.
- [Hot-Swap за 15 мс](4_concepts/hot_swap_15ms.md) — Как код обновляется на лету без перезагрузки чипа.
- [Реактивная модель событий](4_concepts/reactive_events.md) — Аппаратные прерывания вместо блокирующих `delay()`.
- [Реактивная шина сигналов](4_concepts/reactive_signals.md) — Архитектура IPC без блокировок и динамической памяти.
- [Цифровой двойник и телеметрия](4_concepts/digital_twin.md) — Живая интерактивная схема выводов платы в Studio.

### 📐 Архитектурные предложения и RFC
- [Реестр RFC и статусы](rfcs/index.md) — Матрица готовности будущих протоколов и спецификаций.
