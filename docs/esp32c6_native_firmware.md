# ESP32-C6 Native Firmware & Hardware Flashing Guide

В этом документе подробно описана архитектура, сборка, оптимизация размера и процесс автономной прошивки нативного ядра **FerrumOS** на физический микроконтроллер **ESP32-C6** (RISC-V).

---

## 🧭 Архитектурный обзор

Ядро `crates/esp32c6-firmware` работает в режиме **bare-metal** (`no_std`) напрямую на 32-битном RISC-V ядре ESP32-C6 (160 МГц) без тяжелых сторонних операционных систем.

### Ключевые компоненты:
1. **HAL (Hardware Abstraction Layer):** `esp-hal` v0.23.1 для управления периферией (GPIO, UART, системные таймеры).
2. **Динамический аллокатор памяти:** `esp-alloc` v0.6.0 с выделенным пулом кучи 128 КБ в SRAM.
3. **Скриптовый движок Rhai/JS:** Встроенный интерпретатор `rhai` v1.20+ в режиме `no_std`, `only_i32`, `no_optimize` для мгновенного выполнения пользовательских сценариев.
4. **Консоль отладки:** `esp-println` v0.13.1 с выводом логов через USB-Serial / UART0 на скорости 115200 бод.
5. **Совместимость с ESP-IDF Bootloader:** Дескриптор приложения `EspAppDesc` со структурой заголовка `0xABCD5432` в секции `.rodata_desc` для валидации 2-й ступенью загрузчика ESP-IDF.

---

## 📋 Карта Flash-памяти ESP32-C6

Стандартная таблица разделов для флеш-памяти 4 МБ:

| Адрес (Offset) | Размер | Назначение | Описание |
| :--- | :--- | :--- | :--- |
| `0x00000000` | 32 KB | **Bootloader** | ESP-IDF 2nd stage bootloader |
| `0x00008000` | 4 KB | **Partition Table** | Таблица разделов (`nvs`, `phy_init`, `factory`) |
| `0x00009000` | 24 KB | **NVS** | Энергонезависимое хранилище настроек и Wi-Fi данных |
| `0x0000F000` | 4 KB | **PHY Init** | Калибровочные RF-данные радиоканала |
| `0x00010000` | 4 MB (макс) | **Factory App** | Нативный бинарник ядра FerrumOS + встроенный скрипт |

---

## ⚡ Оптимизация размера прошивки

По умолчанию полный движок Rhai с генератором кода может превышать 1.4 МБ. Для минимального размера применены следующие флаги компилятора:

```toml
[profile.release]
opt-level = "z"     # Оптимизация под минимальный размер бинарного кода
lto = "fat"         # Глубокая межмодульная оптимизация на этапе линковки
codegen-units = 1   # Единый блок генерации кода
panic = "abort"     # Отключение тяжелых таблиц размотки стека (unwind tables)
strip = false       # Сохранение точки входа _start для корректного jump bootloader'а
```

**Результат:** Размер бинарного приложения factory partition составляет всего **~689 КБ** (менее 17% от Flash-памяти 4 МБ).

---

## 🔨 Сборка и генерация прошивки

### 1. Установка целевой архитектуры RISC-V
```powershell
rustup target add riscv32imac-unknown-none-elf
```

### 2. Сборка ELF-бинарника
```powershell
cd crates/esp32c6-firmware
cargo build --release
```

### 3. Генерация полного прошивочного образа (`firmware-full.bin`)
С помощью утилиты `espflash` собирается единый файл, включающий загрузчик, таблицу разделов и приложение:
```powershell
espflash save-image --chip esp32c6 --merge --skip-padding target/riscv32imac-unknown-none-elf/release/esp32c6-firmware ../../build_esp32c6/firmware-full.bin
```

---

## 🔌 Прошивка в микроконтроллер через USB

Для автономной прошивки через утилиту `esptool`:

```powershell
python -m esptool --chip esp32c6 -p COM3 -b 460800 write-flash 0x0 build_esp32c6/firmware-full.bin
```

---

## 💡 Выполнение JS-скриптов на ESP32-C6

Пример скрипта [`scripts/blink_led.js`](../scripts/blink_led.js):

```javascript
console.log("=== FerrumOS: Running JS Blink Script on ESP32-C6 ===");
bind_gpio_output("StatusLED", 15);

let tick = 1;
loop {
    console.log("[Tick " + tick + "] LED ON (HIGH)");
    device.gpio("StatusLED").write(true);
    delay_ms(500);

    console.log("[Tick " + tick + "] LED OFF (LOW)");
    device.gpio("StatusLED").write(false);
    delay_ms(500);

    tick += 1;
    if tick > 1000 {
        tick = 1;
    }
}
```

---

## 🖥️ Мониторинг UART / Serial консоли (115200 baud)

```powershell
python -c "import serial, time; s = serial.Serial('COM3', 115200, timeout=0.5); [print(s.readline().decode('utf-8', errors='replace').rstrip()) while True]"
```

**Живой вывод из консоли чипа:**
```text
I (220) boot: Loaded app from partition at offset 0x10000

=========================================================
=== FerrumOS ESP32-C6 Native Embedded Firmware Booting ===
=========================================================
[FerrumOS Kernel] Initializing Embedded Rhai/JS Engine...
[FerrumOS Kernel] Executing JS Script...
[JS:Console] === FerrumOS: Running JS Blink Script on ESP32-C6 ===
[FerrumOS Kernel] Binding GPIO pin 15 to alias 'StatusLED'
[JS:Console] [Tick 1] LED ON (HIGH)
[JS:Console] [Tick 1] LED OFF (LOW)
[JS:Console] [Tick 2] LED ON (HIGH)
[JS:Console] [Tick 2] LED OFF (LOW)
[JS:Console] [Tick 3] LED ON (HIGH)
...
```
