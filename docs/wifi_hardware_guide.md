# 📡 ESP32-C6 Bare-Metal Rust Wi-Fi Guide & Setup

This document serves as the official specification and guide for configuring, building, and running **Wi-Fi** in **`no_std` (Bare-Metal Rust)** mode on **ESP32-C6** microcontrollers (including **ESP32-C6 SuperMini**, chip revision `v0.2`).

---

## 🎯 Architecture Summary

On ESP32-C6, the Wi-Fi 6 radio subsystem (802.11ax/b/g/n) is controlled via Espressif low-level blobs through `esp-wifi` and the `smoltcp` network stack.

To ensure stability (preventing RF hangs, authentication failures, and bootloader panic loops), it is critical to adhere to:
1. **Compatible `esp-hal` & `esp-wifi` crate version matrix**
2. **Correct linker script configuration (`-Tlinkall.x`)**
3. **Valid ESP-IDF App Descriptor (`esp_bootloader_esp_idf::esp_app_desc!()`)**

---

## 📦 1. Tested Dependency Matrix (`Cargo.toml`)

In `crates/esp32c6-firmware/Cargo.toml`:

```toml
[dependencies]
# 1. Hardware Abstraction Layer with 'unstable' feature for integrated drivers
esp-hal = { version = "1.0.0-rc.0", features = ["esp32c6", "unstable"] }

# 2. Panic handler & logging
esp-backtrace = { version = "0.16.0", features = ["esp32c6", "panic-handler", "println"] }
esp-println = { version = "0.14.0", features = ["esp32c6", "log-04"] }

# 3. Wi-Fi driver with built-in cooperative task scheduler
esp-wifi = { version = "0.15.1", default-features = false, features = [
    "esp32c6",
    "wifi",
    "smoltcp",
    "esp-alloc",
    "builtin-scheduler",
    "log-04"
] }

# 4. App descriptor for ESP-IDF 2nd-stage bootloader compatibility
esp-bootloader-esp-idf = { version = "0.4.0", features = ["esp32c6"] }

# 5. Memory allocator & static cells
static_cell = "2.1"
esp-alloc = "0.8.0"

# 6. Smoltcp TCP/IP stack
smoltcp = { version = "0.12.0", default-features = false, features = [
    "medium-ethernet",
    "proto-ipv4",
    "proto-dhcpv4",
    "socket-tcp",
    "socket-dhcpv4"
] }

critical-section = "1.2.0"
```

---

## ⚙️ 2. Linker Configuration (`.cargo/config.toml`)

In `crates/esp32c6-firmware/.cargo/config.toml`:

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
> Do NOT use `-Tlayout.x` or `-Trom_functions.x`. In `esp-hal 1.0`, `linkall.x` aggregates all DRAM layout, ROM symbols, and `.trap` exception tables. Using legacy scripts results in `rust-lld: undefined symbol: _dram_origin`.

---

## 🛡️ 3. App Descriptor Macro

At the top of `src/main.rs`:

```rust
use esp_backtrace as _;

// Generates ESP-IDF App Descriptor header at 0x10000
esp_bootloader_esp_idf::esp_app_desc!();
```

---

## 🔨 4. Build & Flash

### Compile:
```powershell
cd crates/esp32c6-firmware
cargo build --release
```

### Direct Flash & Monitor:
```powershell
espflash flash --monitor --port COM3 target/riscv32imac-unknown-none-elf/release/esp32c6-firmware --non-interactive
```

---

## 🔍 5. Verification via HTTP REST

When connected and DHCP assigns an IP (`192.168.1.243`):
```powershell
Invoke-RestMethod -Uri "http://192.168.1.243/api/status"
```
**Response:**
```json
{
  "device": "FerrumOS-ESP32C6",
  "status": "ok"
}
```
