<p align="center">
  <a href="https://github.com/atitoff-dotcom/FerrumOS">
    <img src="assets/logo.png" alt="FerrumOS Logo" width="130" height="130" style="border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);">
  </a>
</p>

<h1 align="center">FerrumOS</h1>

<p align="center">
  <strong>Reactive Micro-OS & Live Hot-Swap Studio for RISC-V & ESP32 Microcontrollers.</strong>
</p>

<p align="center">
  <a href="releases/v0.6.0/"><img src="https://img.shields.io/badge/Release-v0.6.0-blue.svg" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-green.svg" alt="License"></a>
  <a href="#quick-install"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-0078D6.svg?logo=windows" alt="Platform"></a>
  <a href="#supported-hardware"><img src="https://img.shields.io/badge/Target-RISC--V%20(ESP32--C6%20%7C%20C3)-orange.svg" alt="Target"></a>
  <a href="rfcs/"><img src="https://img.shields.io/badge/Specs-RFCs-emerald.svg" alt="RFCs"></a>
</p>

<p align="center">
  <a href="#quick-install">🚀 <b>Quick Install</b></a> |
  <a href="#fluent-chaining-api">📐 <b>Fluent JS API</b></a> |
  <a href="rfcs/">📋 <b>RFC Specifications</b></a> |
  <a href="#supported-hardware">🔌 <b>Hardware</b></a>
</p>

---

FerrumOS is an ultra-fast, bare-metal reactive micro-operating system and live development environment for IoT edge devices, sensors, and smart home automation.

Write clean **Modern JavaScript**, deploy tasks to running hardware in **15 milliseconds over USB / Wi-Fi without restarting the chip**, and monitor live digital twins and pinout telemetry in real time.

All user documentation, code snippets, and interactive guides are built directly into **FerrumOS Studio**. Architectural blueprints and wire protocol standards are maintained in the [RFC Registry](rfcs/).

---

## 🚀 Quick Install (Zero Dependencies)

### Windows (PowerShell):
```powershell
irm https://raw.githubusercontent.com/atitoff-dotcom/FerrumOS/main/tools/install.ps1 | iex
```

### Linux / macOS (Bash):
```bash
curl -fsSL https://raw.githubusercontent.com/atitoff-dotcom/FerrumOS/main/tools/install.sh | bash
```

Once installed, launch the web studio with a single command:
```bash
ferrum studio
```
FerrumOS Studio will open in your default browser.

---

## 📐 Fluent Chaining API

FerrumOS uses strictly atomic fluent chaining for all hardware configuration:

```javascript
// Relay / Digital Output (Atomic Push-Pull initialization)
const relay = GPIO.output(15)
    .openDrain(false)
    .invert(false)
    .initial(false);

relay.high();
delay(100);
relay.low();

// Smart Button with hardware debounce and gesture detection
const btn = GPIO.button(9)
    .pullUp()
    .debounce(30);

btn.onClick(() => relay.toggle());
btn.onHold(() => relay.low());
```

---

## 🔌 Supported Hardware

* **ESP32-C6**: Primary target (RISC-V 160MHz, Wi-Fi 6, BLE 5.3, Thread/Zigbee 802.15.4, CAN/TWAI).
* **ESP32-C3**: Compact edge nodes (RISC-V 160MHz, Wi-Fi 4, BLE 5.0).
* **ESP32-S3**: Dual-core compute & camera nodes (Xtensa LX7).

---

## 📚 RFC Specifications (Single Source of Truth)

All architectural proposals, bytecode opcodes, protocols, and hardware specifications live in the [rfcs/](rfcs/) directory. Each RFC features two living sections:
* `## Реализовано` — exact wire protocols, opcodes, and verified snippets for Studio.
* `## Планируется` — future roadmap and planned features.

Check the [RFC Index](rfcs/README.md) for complete details.

---

## 📄 License

FerrumOS is open-source software licensed under the [Apache License 2.0](LICENSE).
