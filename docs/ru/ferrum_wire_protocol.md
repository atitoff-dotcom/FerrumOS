# ⚡ Спецификация бинарного протокола Ferrum Realtime Protocol (FRP v1)

**Ferrum Realtime Protocol (FRP)** — это сверхкомпактный, энергоэффективный бинарный протокол для взаимодействия микроконтроллеров **ESP32-C6** с хост-клиентами (`ferrum-cli`, шлюзами автоматизации и оркестратором парка).

Протокол заменяет тяжелый текстовый HTTP/JSON на прямой обмен компактными C/Rust структурами с нулевым оверхедом по памяти и процессору.

---

## 🎯 Преимущества бинарного протокола

1. **Экстремальная компактность:**
   - Полный пакет телеметрии занимает всего **48 байт** (вместо ~400 байт текстового HTTP/JSON).
   - Пакет подтверждения загрузки (ACK) занимает всего **8 байт**.
2. **Нулевая нагрузка на CPU и память (Zero-Copy):**
   - На микроконтроллере не требуется парсить строки и генерировать JSON.
   - Структура читается и отправляется напрямую из памяти `&[u8]`.
3. **Совместимость с радиоканалом Thread / IEEE 802.15.4:**
   - Размер пакета 48 байт с запасом укладывается в стандартный **MTU 802.15.4 (127 байт)** без фрагментации.
4. **Минимальная сетевая задержка:**
   - Время ответа чипа составляет менее **1 миллисекунды**.

---

## 📦 Формат пакетов (Frame Layout)

Все числовые поля передаются в формате **Little-Endian**.

### 1. Сигнатура протокола (Magic)
Каждый пакет RWP начинается с 4-байтовой сигнатуры:
`b"RWP\x01"` (`[0x52, 0x57, 0x50, 0x01]`).

### 2. Типы сообщений (Message Types)
| ID | Константа | Направление | Описание |
| :--- | :--- | :--- | :--- |
| `0x01` | `RWP_MSG_GET_STATUS` | Client -> MCU | Запрос телеметрии |
| `0x02` | `RWP_MSG_STATUS_RESP` | MCU -> Client | Ответ с полной телеметрией (48 B) |
| `0x03` | `RWP_MSG_UPLOAD_BYTECODE` | Client -> MCU | Загрузка байткода (`.rhb` контейнер) |
| `0x04` | `RWP_MSG_UPLOAD_RESP` | MCU -> Client | Подтверждение загрузки (ACK, 8 B) |
| `0x05` | `RWP_MSG_REBOOT` | Client -> MCU | Перезагрузка чипа |
| `0x06` | `RWP_MSG_LIST_TASKS` | Client -> MCU | Запрос списка всех запущенных в RAM задач |
| `0x07` | `RWP_MSG_LIST_RESP` | MCU -> Client | Ответ со списком задач (32 B Task ID, размер, статус, execs) |
| `0x08` | `RWP_MSG_DELETE_TASK` | Client -> MCU | Выгрузка задачи из оперативной памяти чипа |
| `0x09` | `RWP_MSG_DELETE_RESP` | MCU -> Client | Подтверждение выгрузки задачи (1 B статус) |
| `0x0A` | `RWP_MSG_FLASH_COMMIT` | Client -> MCU | Запись всех активных RAM задач во Flash (`0x300000`) для Auto-Boot |
| `0x0B` | `RWP_MSG_FLASH_COMMIT_RESP` | MCU -> Client | Ответ подтверждения сохранения во Flash (статус, кол-во задач) |
| `0x0C` | `RWP_MSG_FLASH_ERASE` | Client -> MCU | Стирание раздела Flash хранилища |
| `0x0D` | `RWP_MSG_FLASH_ERASE_RESP` | MCU -> Client | Ответ подтверждения очистки Flash |

---

## 📊 Структура пакета телеметрии `RwpStatusResponse` (48 байт)

```rust
#[repr(C)]
pub struct RwpStatusResponse {
    pub magic: [u8; 4],          // "RWP\x01"
    pub msg_type: u8,            // 0x02 (STATUS_RESP)
    pub cpu_usage_pct: u8,       // 0..100%
    pub load_10s_pct: u8,        // EWMA 10s (0..100%)
    pub load_1m_pct: u8,         // EWMA 1m (0..100%)
    pub load_5m_pct: u8,         // EWMA 5m (0..100%)
    pub wifi_rssi: i8,           // RSSI в dBm (например -65)
    pub wifi_channel: u8,        // Радиоканал (например 6)
    pub _reserved: u8,           // Выравнивание
    pub uptime_sec: u32,         // Время работы в секундах
    pub free_heap_kb: u16,       // Свободная память кучи (в КБ)
    pub used_heap_kb: u16,       // Занятая память кучи (в КБ)
    pub bytecode_size: u16,      // Размер активного байткода в байтах
    pub vm_errors_total: u16,    // Счетчик ошибок VM
    pub vm_steps_total: u32,     // Выполненные инструкции байткода
    pub msg_requests_total: u32, // Счетчик сетевых сообщений
    pub script_id: [u8; 16],     // Идентификатор активного скрипта (16 байт)
}
```

---

## 🚀 Структура подтверждения загрузки `RwpUploadResponse` (8 байт)

```rust
#[repr(C)]
pub struct RwpUploadResponse {
    pub magic: [u8; 4],          // "RWP\x01"
    pub msg_type: u8,            // 0x04 (UPLOAD_RESP)
    pub status: u8,              // 0 = Успех, 1 = Ошибка CRC, 2 = OOM
    pub loaded_bytes: u16,       // Количество загруженных байт
}
```

---

## 💻 Использование через `ferrum-cli`

### Запрос телеметрии:
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- status --ip 192.168.1.243
```

**Вывод:**
```text
========================================================
  🦀 FerrumOS ESP32-C6 Wire Protocol Dashboard (RWP v1)
========================================================
  🖥️  System    : FerrumOS-ESP32C6 (Uptime: 30s, Msg Reqs: 3)
  ⚡ CPU Load  : 2% | Load Avg (10s/1m/5m): [0.08, 0.04, 0.00]
  💾 Memory    : Free Heap: 112 KB | Used: 47 KB
  📡 Wi-Fi/RF  : RSSI: -65 dBm | Channel: 6 | Latency: 23.78 ms
  ⚙️  Script VM : 'main' (49 B bytecode, 221 instrs, 0 errs)
  📦 Wire Packet: Received 48 bytes (Direct Struct Unpack)
========================================================
```

### Горячая загрузка скрипта:
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- run scripts/wifi_blink.js --ip 192.168.1.243
```

**Вывод:**
```text
[FerrumOS CLI] Compiling JS source to .rhb container...
[FerrumOS CLI] Uploading 57 bytes of bytecode to 192.168.1.243:80 (via RWP Binary Socket)...
========================================================
  🚀 FerrumOS Binary Hot-Swap SUCCESS!
  Device ACK   : Loaded 49 bytes into RAM
  Transfer Time: 16.24 ms (Zero Downtime)
========================================================
```
