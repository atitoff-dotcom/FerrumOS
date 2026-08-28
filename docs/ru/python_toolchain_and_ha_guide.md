# 🐍 Руководство по Python-тулчейну FerrumOS и интеграции с Home Assistant

Данный документ описывает архитектуру и спецификацию хостового инструментария **FerrumOS Python Suite**, включающего в себя:
1. **Pre-Flight Validator:** статическая верификация синтаксиса, профилей плат, зависимостей драйверов и коллизий GPIO.
2. **Ferrum Realtime Protocol (FRP) (RWP Client):** прямая работа с микроконтроллерами ESP32-C6 через бинарные сокеты (`struct.pack` / `struct.unpack`).
3. **Fleet Manager:** инвентарь оборудования, версионирование скриптов и массовый деплой.
4. **Home Assistant MQTT Bridge:** автоматическое обнаружение (MQTT Auto-Discovery) сенсоров телеметрии и кнопок управления в Home Assistant.

---

## 🎯 Архитектура пакета `tools/ferrum/`

```text
tools/ferrum/
├── __init__.py          # Экспорт основных модулей
├── protocol.py          # Бинарный протокол RWP (48 байт статус, 8 байт ACK, упаковка .rhb)
├── validator.py         # 4-уровневый Pre-Flight валидатор железа и драйверов
├── discovery.py         # Автопоиск нод в локальной сети
├── fleet.py             # Менеджер парка устройств и версионирование
├── ha_bridge.py         # Мост интеграции с Home Assistant (MQTT Discovery)
└── cli.py               # Консольный интерфейс CLI
```

---

## 🛡️ 1. 4-Уровневый Pre-Flight Валидатор (`validator.py`)

Перед тем как скрипт упаковывается и отправляется по воздуху, валидатор проверяет безопасность:

### Уровень 1: Проверка профиля платы (Board Pinout Map)
* Защита от обращения к запрещенным выводам (Flash SPI, Strapping пины, Crystal).
* Проверка допустимого диапазона GPIO для целевого микроконтроллера (например, GPIO 0–23 для ESP32-C6 SuperMini).

### Уровень 2: Соответствие аппаратных драйверов (Driver Compliance)
* Сопоставление вызовов API с конфигурацией шин:
  * `ds18b20.read()` -> требуется предварительный `bind_onewire_bus(pin)`.
  * `i2c.read()` / `bme280` -> проверка пинов `SDA` и `SCL`.
  * `uart.read_line()` -> проверка пинов `TX` и `RX`.

### Уровень 3: Матрица коллизий пинов (Pin Collision Matrix)
* Исключение конфликтов между параллельно запущенными задачами.
* Запрет одновременного назначения одного пина на выход разными сервисами.

### Уровень 4: Безопасность циклов (Zero-Locking Check)
* Проверка наличия вызовов `delay(...)` в бесконечных циклах `while(true)` для защиты процессора от 100% блокировки.

---

## 📡 2. Модуль бинарного протокола (`protocol.py`)

Модуль реализует протокол RWP v1 с помощью стандартной библиотеки Python `struct`:

```python
# Распаковка 48-байтного пакета телеметрии
RWP_STATUS_FMT = "<4sBBBBBbBxIHHHHII16s"

# Сборка пакета загрузки байткода
def pack_upload_frame(rhb_bytes: bytes) -> bytes:
    return b"RWP\x01\x03" + rhb_bytes
```

---

## 🏡 3. Интеграция с Home Assistant (`ha_bridge.py`)

Мост автоматически генерирует топики **Home Assistant MQTT Discovery**:

### Автоматически создаваемые сущности:
1. `sensor.<node_id>_cpu_load` — загрузка процессора (%)
2. `sensor.<node_id>_free_heap` — свободная память кучи (КБ)
3. `sensor.<node_id>_wifi_rssi` — уровень сигнала Wi-Fi (dBm)
4. `sensor.<node_id>_active_script` — имя активного скрипта
5. `sensor.<node_id>_uptime` — аптайм в секундах
6. `button.<node_id>_restart` — кнопка перезапуска скрипта

---

## 💻 4. Команды консольной утилиты (`cli.py`)

```powershell
# 1. Запрос телеметрии с платы в терминал
python -m tools.ferrum.cli status --ip 192.168.1.243

# 2. Получение телеметрии в формате JSON
python -m tools.ferrum.cli status --ip 192.168.1.243 --json

# 3. Валидация скрипта и проверка пинов
python -m tools.ferrum.cli validate scripts/wifi_blink.js --target esp32c6_supermini

# 4. Проверка и горячий деплой скрипта на плату
python -m tools.ferrum.cli run scripts/wifi_blink.js --ip 192.168.1.243

# 5. Запуск фонового сервиса Home Assistant MQTT Bridge
python -m tools.ferrum.cli ha-bridge --mqtt-host 192.168.1.100
```
