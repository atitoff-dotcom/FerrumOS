# Getting Started & Development Guide

This guide walks you through compiling, running, testing, and optimizing the **FerrumOS** codebase.

---

## 🛠️ Prerequisites

- **Rust Toolchain:** Rust 1.80+ (MSVC on Windows / GCC on Linux / Clang on macOS).
- **Cargo:** Package manager included with Rust.

---

## 🚀 Running Locally (Host Simulation Mode)

To launch FerrumOS on your host PC with simulated hardware drivers and the Web UI server:

```bash
cargo run
```

Once running, open your web browser to:
`http://localhost:8080`

---

## 🧪 Running Automated Tests

To execute the complete test suite (Unit tests, Supervisor isolation, Bus bindings, Storage, Web API, and JS API tests):

```bash
cargo test
```

---

## 📦 Building Size-Optimized Release Binaries (Host)

To build a release binary optimized for minimal binary size and memory footprint:

```bash
cargo build --release
```

Release settings configured in `Cargo.toml`:
```toml
[profile.release]
opt-level = "z"     # Optimize for minimum code size
lto = true          # Link-Time Optimization across all crates
codegen-units = 1   # Single codegen unit for maximum optimization
panic = "abort"     # Remove unwind landing pads
strip = true        # Strip symbols
```

---

## ⚡ ESP32-C6 Native Hardware Firmware & Flashing

To build and flash the native embedded bare-metal FerrumOS firmware directly to an **ESP32-C6** microcontroller over USB:

### 1. Build for RISC-V Target
```powershell
cd crates/esp32c6-firmware
cargo build --release
```

### 2. Package Flash Image
```powershell
espflash save-image --chip esp32c6 --merge --skip-padding target/riscv32imac-unknown-none-elf/release/esp32c6-firmware ../../build_esp32c6/firmware-full.bin
```

### 3. Flash to ESP32-C6 via USB (`COM3`)
```powershell
python -m esptool --chip esp32c6 -p COM3 -b 460800 write-flash 0x0 build_esp32c6/firmware-full.bin
```

For full details, partition maps, and debugging, see the [ESP32-C6 Native Firmware Guide](esp32c6_native_firmware.md).
