# Начало работы и руководство по разработке

В этом руководстве описаны компиляция, запуск, тестирование и оптимизация кодовой базы **FerrumOS**.

---

## 🛠️ Предварительные требования

- **Тулчейн Rust:** Rust 1.80+ (MSVC в Windows / GCC в Linux / Clang в macOS).
- **Cargo:** Пакетный менеджер, входящий в состав Rust.

---

## 🚀 Локальный запуск (режим симуляции на хосте)

Чтобы запустить FerrumOS на компьютере с симулированными аппаратными драйверами и сервером Web UI:

```bash
cargo run
```

После запуска откройте веб-браузер по адресу:
`http://localhost:8080`

---

## 🧪 Запуск автоматических тестов

Чтобы запустить полный набор тестов (модульные тесты, изоляция супервизора, привязка шин, хранилище, Web API и тесты JS API):

```bash
cargo test
```

---

## 📦 Сборка оптимизированного по размеру release-бинарника (Хост)

Чтобы собрать release-бинарник, оптимизированный под минимальный размер и потребление памяти:

```bash
cargo build --release
```

Настройки сборки в `Cargo.toml`:
```toml
[profile.release]
opt-level = "z"     # Оптимизация под минимальный размер кода
lto = true          # Link-Time Optimization (LTO) для всех крейтов
codegen-units = 1   # Единый блок генерации кода для максимальной оптимизации
panic = "abort"     # Отключение таблиц размотки стека (landing pads)
strip = true        # Удаление отладочных символов
```

---

## ⚡ Нативная прошивка для ESP32-C6 и загрузка в устройство

Сборка и прошивка нативной bare-metal прошивки FerrumOS напрямую в микроконтроллер **ESP32-C6** по USB:

### 1. Сборка под таргет RISC-V
```powershell
cd crates/esp32c6-firmware
cargo build --release
```

### 2. Упаковка Flash-образа
```powershell
espflash save-image --chip esp32c6 --merge --skip-padding target/riscv32imac-unknown-none-elf/release/esp32c6-firmware ../../build_esp32c6/firmware-full.bin
```

### 3. Запись прошивки в ESP32-C6 через USB (`COM3`)
```powershell
python -m esptool --chip esp32c6 -p COM3 -b 460800 write-flash 0x0 build_esp32c6/firmware-full.bin
```

Подробные сведения, карту разделов и информацию об отладке см. в [Руководстве по нативной прошивке ESP32-C6](esp32c6_native_firmware.md).
