# ⚡ Руководство по OTA Hot-Swap и компилятору JavaScript в FerrumOS

Данное руководство описывает архитектуру, формат бинарного контейнера `.rhb`, консольную утилиту `ferrum-cli` и процесс **горячей замены (OTA Hot-Swap)** скомпилированных JS-скриптов на микроконтроллерах **ESP32-C6** по сети Wi-Fi.

---

## 🎯 Концепция и преимущества OTA Hot-Swap

В традиционных embedded-платформах обновление логики требует полной перепрошивки Flash-памяти (перезапуск контроллера, разрыв сетевых соединений и простой оборудования).

В **FerrumOS**:
1. 🖥️ **Хост-компиляция на ПК:** Исходный код на JavaScript компилируется на рабочей станции с помощью легковесного Rust-компилятора `ferrum-compiler` в компактный бинарный байткод.
2. 📦 **Контейнеризация и CRC16:** Байткод упаковывается в защищенный контейнер `.rhb` с заголовком Magic `RHB\x01` и контрольной суммой CRC16-CCITT.
3. 📡 **Мгновенная доставка по Wi-Fi:** По сети отправляется компактный бинарный пакет (обычно всего **40–100 байт**) через HTTP `POST /api/bytecode`.
4. ⚡ **Zero-Downtime Hot-Swap:** Микроядро на ESP32-C6 проверяет целостность, атомарно обновляет реестр скриптов в RAM и сразу запускает новый алгоритм — **без перезагрузки микроконтроллера и без прерывания Wi-Fi сессий**.

---

## 📦 Спецификация формата контейнера `.rhb` (Binary Layout)

| Смещение (Bytes) | Размер | Поле | Описание |
| :--- | :--- | :--- | :--- |
| `0..3` | 4 B | **Magic Header** | `b"RHB\x01"` — сигнатура контейнера FerrumOS Bytecode v1 |
| `4..5` | 2 B | **CRC16-CCITT** | Контрольная сумма полезной нагрузки (Little-Endian) |
| `6..7` | 2 B | **Length** | Длина полезной нагрузки байткода `N` (Little-Endian) |
| `8..(8+N)` | `N` B | **Payload** | Инструкции байткода виртуальной машины |

---

## 🛠️ Консольная утилита `ferrum-cli`

Утилита командной строки `crates/ferrum-cli` предоставляет полный инструментарий для разработчика:

### 1. Компиляция JS-скрипта в `.rhb`
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- compile scripts/wifi_blink.js
```
*Генерирует бинарный файл `scripts/wifi_blink.rhb`.*

### 2. Локальная симуляция и отладка на ПК
Позволяет протестировать логику выполнения байткода на компьютере перед отправкой на физическое устройство:
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- test scripts/wifi_blink.js
```

**Вывод симулятора:**
```text
========================================================
  FerrumOS Host Simulator: Executing "scripts/wifi_blink.js" (49 bytes)...
========================================================
  [VM SIM Step 001] 💡 Dynamic GPIO 15 -> HIGH
  [VM SIM Step 002] ⏱️ delay(200 ms)
  [VM SIM Step 003] 💡 Dynamic GPIO 15 -> LOW
  [VM SIM Step 004] ⏱️ delay(300 ms)
```

### 3. Автоматическая компиляция и загрузка на чип по Wi-Fi (Run)
Одной командой компилирует JS и сразу загружает на плату:
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- run scripts/wifi_blink.js --ip 192.168.1.243
```

**Вывод CLI:**
```text
[FerrumOS CLI] Compiling JS source to .rhb container...
[FerrumOS CLI] Uploading 57 bytes of bytecode to http://192.168.1.243:80/api/bytecode...
========================================================
  FerrumOS Hot-Swap SUCCESS! 🚀
  Device Response: {"status":"ok","action":"loaded"}
========================================================
```

### 4. Проверка доступности и статуса платы
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- status --ip 192.168.1.243
```

---

## 🌐 Прямой деплой через `curl` / `PowerShell`

Если `.rhb` контейнер уже собран, его можно залить на плату без использования Rust:

### Через `curl`:
```bash
curl -X POST http://192.168.1.243/api/bytecode \
     -H "Content-Type: application/octet-stream" \
     --data-binary @scripts/wifi_blink.rhb
```

### Через `PowerShell`:
```powershell
$bytes = [System.IO.File]::ReadAllBytes("scripts/wifi_blink.rhb")
Invoke-RestMethod -Uri "http://192.168.1.243/api/bytecode" -Method Post -Body $bytes -ContentType "application/octet-stream"
```

---

## 🔍 Мониторинг логов чипа во время Hot-Swap

В момент получения нового байткода микроконтроллер выводит в Serial-порт:

```text
*********************************************************
*** [FerrumOS REST] HOT-SWAP: NEW BYTECODE LOADED (49 B) ***
*********************************************************
```

Состояние виртуальной машины сбрасывается (`vm.reset()`), и светодиод на плате мгновенно начинает моргать с новыми таймингами.
