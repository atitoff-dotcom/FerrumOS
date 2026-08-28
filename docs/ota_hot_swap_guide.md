# ⚡ OTA Hot-Swap & JavaScript Compiler Guide in FerrumOS

This guide details the architecture, `.rhb` binary container specification, the `ferrum-cli` toolchain, and the **OTA Hot-Swap** workflow for compiled JavaScript scripts running on **ESP32-C6** microcontrollers over Wi-Fi.

---

## 🎯 Architecture & Advantages

In traditional embedded development, updating logic requires full flash rewrites, MCU reboots, and network downtime.

In **FerrumOS**:
1. 🖥️ **Host Compilation:** JavaScript source code is compiled on the development PC using `ferrum-compiler` into compact bytecode.
2. 📦 **Containerization & CRC16:** Bytecode is packaged into an `.rhb` container with a magic header `RHB\x01` and CRC16-CCITT checksum.
3. 📡 **Over-The-Air Delivery:** The lightweight binary container (**40–100 bytes**) is transmitted over Wi-Fi via `POST /api/bytecode`.
4. ⚡ **Zero-Downtime Hot-Swap:** The ESP32-C6 microkernel verifies the payload, updates its RAM script registry, and executes the new algorithm immediately without MCU reboot.

---

## 📦 `.rhb` Binary Layout Specification

| Offset (Bytes) | Size | Field | Description |
| :--- | :--- | :--- | :--- |
| `0..3` | 4 B | **Magic Header** | `b"RHB\x01"` — FerrumOS Bytecode container signature |
| `4..5` | 2 B | **CRC16-CCITT** | Checksum of payload (Little-Endian) |
| `6..7` | 2 B | **Length** | Bytecode payload length `N` (Little-Endian) |
| `8..(8+N)` | `N` B | **Payload** | Raw VM bytecode instructions |

---

## 🛠️ CLI Usage (`ferrum-cli`)

### 1. Compile JS to `.rhb`
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- compile scripts/wifi_blink.js
```

### 2. Local Simulation & PC Test
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- test scripts/wifi_blink.js
```

### 3. Compile & Deploy over Wi-Fi in One Step
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- run scripts/wifi_blink.js --ip 192.168.1.243
```

**Output:**
```text
[FerrumOS CLI] Compiling JS source to .rhb container...
[FerrumOS CLI] Uploading 57 bytes of bytecode to http://192.168.1.243:80/api/bytecode...
========================================================
  FerrumOS Hot-Swap SUCCESS! 🚀
  Device Response: {"status":"ok","action":"loaded"}
========================================================
```

### 4. Fetch Status over Wi-Fi
```powershell
cargo run --manifest-path crates/ferrum-cli/Cargo.toml -- status --ip 192.168.1.243
```

---

## 🌐 Deploy via `curl` / `PowerShell`

```bash
curl -X POST http://192.168.1.243/api/bytecode \
     -H "Content-Type: application/octet-stream" \
     --data-binary @scripts/wifi_blink.rhb
```
