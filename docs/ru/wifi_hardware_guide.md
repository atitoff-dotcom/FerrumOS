# 📡 Руководство по настройке и сборке Wi-Fi на ESP32-C6 (Bare-Metal Rust)

Данный документ представляет собой исчерпывающее руководство и эталонную спецификацию по сборке, настройке и запуску **Wi-Fi** в режиме **`no_std` (Bare-Metal Rust)** на микроконтроллерах **ESP32-C6** (включая платы **ESP32-C6 SuperMini**, ревизия чипа `v0.2`).

---

## 🎯 Архитектурная справка

На ESP32-C6 радиомодуль Wi-Fi 6 (802.11ax/b/g/n) управляется низкоуровневыми блобами Espressif через крейт `esp-wifi` и сетевой стек `smoltcp`. 

Для стабильного функционирования (без зависаний, сбоев аутентификации и ошибок загрузчика) необходимо строго соблюдать **совместимость версий экосистемы `esp-hal`**, **правильные флаги линкера** и **наличие валидного дескриптора приложения**.

---

## 📦 1. Эталонная матрица зависимостей (`Cargo.toml`)

В файле `crates/esp32c6-firmware/Cargo.toml` используйте следующую проверенную комбинацию:

```toml
[dependencies]
# 1. Аппаратный HAL (с фичей "unstable" для поддержки встроенных драйверов)
esp-hal = { version = "1.0.0-rc.0", features = ["esp32c6", "unstable"] }

# 2. Обработка паник и консольный вывод
esp-backtrace = { version = "0.16.0", features = ["esp32c6", "panic-handler", "println"] }
esp-println = { version = "0.14.0", features = ["esp32c6", "log-04"] }

# 3. Wi-Fi драйвер с кооперативным планировщиком задач
esp-wifi = { version = "0.15.1", default-features = false, features = [
    "esp32c6",
    "wifi",
    "smoltcp",
    "esp-alloc",
    "builtin-scheduler",
    "log-04"
] }

# 4. Дескриптор приложения для совместимости с ESP-IDF Bootloader
esp-bootloader-esp-idf = { version = "0.4.0", features = ["esp32c6"] }

# 5. Управление памятью и статическими ячейками
static_cell = "2.1"
esp-alloc = "0.8.0"

# 6. Сетевой стек TCP/IP
smoltcp = { version = "0.12.0", default-features = false, features = [
    "medium-ethernet",
    "proto-ipv4",
    "proto-dhcpv4",
    "socket-tcp",
    "socket-dhcpv4"
] }

critical-section = "1.2.0"
```

> [!IMPORTANT]
> **Почему не `esp-wifi 0.12.0`?**
> В `esp-wifi` версий `<= 0.12.0` для чипов ESP32-C6 ревизии `v0.2` встроенные PHY-блобы калибровки частоты не могли корректно инициализировать радиоприемник в среде 2-й ступени загрузчика ESP-IDF (в логах было `Scan found 0 AP(s)` и `Connect failed: Disconnected`). Начиная с версии `0.15.1`, RF-калибровки работают стабильно.

---

## ⚙️ 2. Конфигурация линкера (`.cargo/config.toml`)

В файле `crates/esp32c6-firmware/.cargo/config.toml` скрипты компоновщика должны указывать на **`linkall.x`**:

```toml
[target.riscv32imac-unknown-none-elf]
runner = "espflash flash --monitor"

[build]
rustflags = [
  "-C", "link-arg=-Tlinkall.x",
]
target = "riscv32imac-unknown-none-elf"

[unstable]
build-std = ["core", "alloc"]
```

> [!WARNING]
> Не используйте устаревшие флаги `-Tlayout.x` или `-Trom_functions.x`. В `esp-hal 1.0` скрипт `linkall.x` автоматически агрегирует память DRAM, векторы прерываний `.trap` и таблицы функций ROM. Использование устаревших скриптов вызывает ошибку `rust-lld: undefined symbol: _dram_origin`.

---

## 🛡️ 3. Дескриптор приложения (`esp_app_desc!`)

ESP-IDF Bootloader (находящийся во флеш-памяти по адресу `0x00000000`) проверяет структуру заголовка бинарника по смещению `0x10000`.

В начале файла `src/main.rs` обязательно добавьте макрос:

```rust
use esp_backtrace as _;

// Генерация валидного заголовка ESP-IDF App Descriptor
esp_bootloader_esp_idf::esp_app_desc!();
```

Если макрос отсутствует, чип после прошивки будет циклически перезагружаться с ошибкой:
`E (76) esp_image: Failed to fetch app description header!`
`E (80) boot: Factory app partition is not bootable`

---

## 🚀 4. Эталонный код инициализации Wi-Fi и smoltcp

### Шаг 1: Выделение кучи и тактирование
```rust
#[esp_hal::main]
fn main() -> ! {
    esp_println::logger::init_logger(log::LevelFilter::Info);
    
    // Выделяем 160 КБ для аллокатора кучи (требуется для esp-wifi и VM)
    esp_alloc::heap_allocator!(size: 160 * 1024);

    let config = esp_hal::Config::default().with_cpu_clock(esp_hal::clock::CpuClock::max());
    let peripherals = esp_hal::init(config);
    let delay = Delay::new();
```

### Шаг 2: Инициализация контроллера Wi-Fi
```rust
    let timg0 = TimerGroup::new(peripherals.TIMG0);
    let rng = Rng::new(peripherals.RNG);

    static INIT: StaticCell<esp_wifi::EspWifiController<'static>> = StaticCell::new();
    let init = &*INIT.init(esp_wifi::init(timg0.timer0, rng).unwrap());

    let (mut controller, interfaces) =
        esp_wifi::wifi::new(init, peripherals.WIFI).unwrap();
    let mut device = interfaces.sta;
```

### Шаг 3: Автопоиск сети и динамическая настройка
```rust
    let target_ssid = "TP-LINK_F17A52";
    let target_pass = "aLabamabh009";

    // Задаем базовую конфигурацию
    let client_config = Configuration::Client(ClientConfiguration {
        ssid: target_ssid.try_into().unwrap(),
        password: target_pass.try_into().unwrap(),
        auth_method: AuthMethod::WPA2Personal,
        ..Default::default()
    });
    controller.set_configuration(&client_config).unwrap();
    controller.start().unwrap();

    // Сканируем радиоэфир для точного определения канала и типа шифрования
    if let Ok(aps) = controller.scan_n(10) {
        for ap in aps.iter() {
            if ap.ssid == target_ssid {
                let cfg = Configuration::Client(ClientConfiguration {
                    ssid: target_ssid.try_into().unwrap(),
                    password: target_pass.try_into().unwrap(),
                    auth_method: ap.auth_method.unwrap_or(AuthMethod::WPA2Personal),
                    channel: Some(ap.channel),
                    ..Default::default()
                });
                let _ = controller.set_configuration(&cfg);
                break;
            }
        }
    }

    // Подключение к точке доступа
    controller.connect().unwrap();
    while !controller.is_connected().unwrap_or(false) {
        delay.delay_millis(200);
    }
    println!("*** [Wi-Fi] УСПЕШНО ПОДКЛЮЧЕНО К AP! ***");
```

### Шаг 4: Инициализация smoltcp и DHCP
```rust
    let mut iface = smoltcp::iface::Interface::new(
        smoltcp::iface::Config::new(smoltcp::wire::HardwareAddress::Ethernet(
            smoltcp::wire::EthernetAddress::from_bytes(&device.mac_address()),
        )),
        &mut device,
        now_instant(),
    );

    let mut socket_set_entries: [SocketStorage; 4] = Default::default();
    let mut sockets = SocketSet::new(&mut socket_set_entries[..]);

    let dhcp_socket = dhcpv4::Socket::new();
    let dhcp_handle = sockets.add(dhcp_socket);
```

---

## 🔨 5. Сборка и прошивка

### Команда сборки:
```powershell
cd crates/esp32c6-firmware
cargo build --release
```

### Команда прямой прошивки и запуска монитора:
```powershell
espflash flash --monitor --port COM3 target/riscv32imac-unknown-none-elf/release/esp32c6-firmware --non-interactive
```

---

## 🔍 6. Проверка сетевой активности

После того как плата выведет в консоль полученный IP-адрес:
```text
=========================================================
=== [FerrumOS Network] WI-FI CONNECTED & IP ASSIGNED!   ===
=== IP Address : 192.168.1.243/24
=== Gateway    : 192.168.1.1
=========================================================
```

Выполните HTTP-запрос с компьютера в той же локальной сети:
```powershell
Invoke-RestMethod -Uri "http://192.168.1.243/api/status"
```

Ожидаемый JSON-ответ:
```json
{
  "device": "FerrumOS-ESP32C6",
  "status": "ok"
}
```

---

## 🛠️ 7. Таблица решения типичных проблем (Troubleshooting)

| Симптом / Ошибка | Первопричина | Решение |
| :--- | :--- | :--- |
| `Scan found 0 AP(s)` или `Connect failed: Disconnected` | Устаревший крейт `esp-wifi <= 0.12.0` на ESP32-C6 rev v0.2. | Обновить `esp-wifi` до `>= 0.15.1` и `esp-hal` до `>= 1.0.0-rc.0`. |
| `rust-lld: undefined symbol: _dram_origin` | В `.cargo/config.toml` указан устаревший скрипт `-Tlayout.x`. | Заменить на `-C link-arg=-Tlinkall.x`. |
| `rust-lld: cannot find linker script rom_functions.x` | Лишний флаг линкера `-Trom_functions.x`. | Удалить флаг, оставить только `-Tlinkall.x`. |
| `E (76) esp_image: Failed to fetch app description header!` | В бинарнике нет заголовка дескриптора ESP-IDF. | Добавить `esp_bootloader_esp_idf::esp_app_desc!()` в `src/main.rs`. |
| `The unstable feature is required by a dependent crate` | `esp-hal` требует флаг `unstable`. | Добавить `features = ["esp32c6", "unstable"]` для `esp-hal` в `Cargo.toml`. |
| `WARN - esp_wifi_internal_tx 12290` | Пакеты smoltcp отправляются до того, как станция ассоциировалась с AP. | Опрашивать `iface.poll` только когда `wifi_state() == WifiState::StaConnected`. |
