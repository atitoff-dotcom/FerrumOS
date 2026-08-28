# ⚡ Ferrum Realtime Protocol (FRP v1) Specification

**Ferrum Realtime Protocol (FRP)** is an ultra-compact, energy-efficient binary protocol for communication between **ESP32-C6** microcontrollers and host clients (`ferrum-cli`, gateways, and fleet orchestrators).

RWP replaces heavy text-based HTTP/JSON with direct binary C/Rust structures with zero memory and CPU overhead.

---

## 🎯 Protocol Advantages

1. **Extreme Compactness:**
   - Full status telemetry packet is only **48 bytes** (instead of ~400 bytes for HTTP/JSON).
   - Upload ACK packet is only **8 bytes**.
2. **Zero-Copy & Zero-Allocation:**
   - No string parsing or JSON serialization on the microcontroller.
   - Structs are written and read directly to/from wire slices.
3. **Thread / IEEE 802.15.4 Native:**
   - 48-byte packet easily fits into standard **802.15.4 MTU (127 bytes)** without fragmentation.
4. **Sub-Millisecond Latency:**
   - Device response time is under 1 millisecond.

---

## 📦 Packet Types & Layout

All integers are transmitted in **Little-Endian** format.

### Protocol Signature (Magic)
Every RWP packet begins with `b"RWP\x01"` (`[0x52, 0x57, 0x50, 0x01]`).

### Message Types
| ID | Constant | Direction | Description |
| :--- | :--- | :--- | :--- |
| `0x01` | `RWP_MSG_GET_STATUS` | Client -> MCU | Query telemetry |
| `0x02` | `RWP_MSG_STATUS_RESP` | MCU -> Client | Full telemetry response (48 B) |
| `0x03` | `RWP_MSG_UPLOAD_BYTECODE` | Client -> MCU | Upload bytecode (`.rhb` container) |
| `0x04` | `RWP_MSG_UPLOAD_RESP` | MCU -> Client | Upload ACK (8 B) |
| `0x05` | `RWP_MSG_REBOOT` | Client -> MCU | MCU Reboot |
| `0x06` | `RWP_MSG_LIST_TASKS` | Client -> MCU | Query full list of tasks running in RAM |
| `0x07` | `RWP_MSG_LIST_RESP` | MCU -> Client | Multi-task registry response (32 B Task ID, size, status, execs) |
| `0x08` | `RWP_MSG_DELETE_TASK` | Client -> MCU | Unload task from RAM registry |
| `0x09` | `RWP_MSG_DELETE_RESP` | MCU -> Client | Unload ACK (1 B status code) |

---

## 📊 Status Response Packet (`RwpStatusResponse`, 48 bytes)

```rust
#[repr(C)]
pub struct RwpStatusResponse {
    pub magic: [u8; 4],          // "RWP\x01"
    pub msg_type: u8,            // 0x02 (STATUS_RESP)
    pub cpu_usage_pct: u8,       // 0..100%
    pub load_10s_pct: u8,        // EWMA 10s (0..100%)
    pub load_1m_pct: u8,         // EWMA 1m (0..100%)
    pub load_5m_pct: u8,         // EWMA 5m (0..100%)
    pub wifi_rssi: i8,           // RSSI in dBm (e.g. -65)
    pub wifi_channel: u8,        // RF Channel (e.g. 6)
    pub _reserved: u8,           // Padding
    pub uptime_sec: u32,         // Uptime in seconds
    pub free_heap_kb: u16,       // Free heap RAM in KB
    pub used_heap_kb: u16,       // Used heap RAM in KB
    pub bytecode_size: u16,      // Active bytecode size in bytes
    pub vm_errors_total: u16,    // VM error counter
    pub vm_steps_total: u32,     // VM instruction counter
    pub msg_requests_total: u32, // Network message counter
    pub script_id: [u8; 16],     // Active script identifier
}
```

---

## 💻 CLI Usage (`ferrum-cli`)

### Fetch Telemetry:
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- status --ip 192.168.1.243
```

### Hot-Swap Deploy:
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- run scripts/wifi_blink.js --ip 192.168.1.243
```
