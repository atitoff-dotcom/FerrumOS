<p align="center">
  <a href="https://atitoff-dotcom.github.io/FerrumOS/">
    <img src="assets/logo.png" alt="FerrumOS Logo" width="130" height="130" style="border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);">
  </a>
</p>

<h1 align="center">FerrumOS</h1>

<p align="center">
  <strong>Reactive Micro-OS & Live Hot-Swap Studio for RISC-V & ESP32 Microcontrollers.</strong>
</p>

<p align="center">
  <a href="https://atitoff-dotcom.github.io/FerrumOS/"><img src="https://img.shields.io/badge/Docs-atitoff--dotcom.github.io%2FFerrumOS-D35400.svg?logo=bookstack" alt="Documentation"></a>
  <a href="releases/v0.6.0/"><img src="https://img.shields.io/badge/Release-v0.6.0-blue.svg" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-green.svg" alt="License"></a>
  <a href="#downloads"><img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6.svg?logo=windows" alt="Platform"></a>
  <a href="#supported-hardware"><img src="https://img.shields.io/badge/Target-RISC--V%20(ESP32--C6%20%7C%20C3)-orange.svg" alt="Target"></a>
</p>

<p align="center">
  <a href="https://atitoff-dotcom.github.io/FerrumOS/">📖 <b>Read the Documentation</b></a> |
  <a href="https://atitoff-dotcom.github.io/FerrumOS/1_getting_started/01_quickstart/">🚀 <b>Quick Start (3 Mins)</b></a> |
  <a href="https://atitoff-dotcom.github.io/FerrumOS/3_reference/js_api/">📐 <b>Fluent JS API</b></a> |
  <a href="https://atitoff-dotcom.github.io/FerrumOS/rfcs/">📋 <b>RFC Registry</b></a> |
  <a href="#downloads">⬇️ <b>Downloads</b></a>
</p>

---

FerrumOS is an ultra-fast, bare-metal reactive micro-operating system and live development environment for IoT edge devices, sensors, and smart home automation.

Write clean **Modern JavaScript**, deploy tasks to running hardware in **15 milliseconds over USB / Wi-Fi without restarting the chip**, and monitor live digital twins and pinout telemetry in real time.

---

## 📥 Downloads (Windows Releases)

| Package | Version | Description | Download Link |
|---|---|---|---|
| **Windows Installer** *(Recommended)* | **v0.6.0** | Full setup wizard. Installs to `%LOCALAPPDATA%\Programs`, creates Start Menu and Desktop shortcuts, adds clean uninstaller. Preserves user data on update. | [⬇️ **Download Installer (.exe)**](releases/v0.6.0/FerrumOS-Studio-Setup-v0.6.0.exe) |
| **Portable Edition** | **v0.6.0** | Standalone executable. Runs without installation (ideal for flash drives). | [⬇️ **Download Portable (.exe)**](releases/v0.6.0/FerrumOS-Studio-v0.6.0-portable.exe) |

> [!NOTE]
> **Zero Dependencies**: FerrumOS Studio is completely self-contained. You **do not** need Python, Node.js, Git, or administrative privileges installed on your machine.

---

## ⚡ Quick Start (Under 3 Minutes)

1. **Download & Install**: Run `FerrumOS-Studio-Setup-v0.6.0.exe` and launch **FerrumOS Studio**.
2. **Connect Hardware**: Plug your ESP32-C6 or ESP32-C3 board into your PC via USB-C. Click **Connect** in the top navigation bar and select your COM port.
3. **1-Click Flash**: Open the **Flasher** tab, choose your board target, and click **Flash Firmware**. FerrumOS installs the bootloader, partition table, and kernel automatically.
4. **Deploy Script**: In the **IDE** tab, write your automation logic and press `Ctrl+Enter` (or click **Run**). Your code executes in 15 milliseconds without a reboot!

👉 **[Follow the Step-by-Step Guide with Screenshots](https://atitoff-dotcom.github.io/FerrumOS/1_getting_started/01_quickstart/)**

---

## 📐 Fluent Chaining JavaScript API

FerrumOS enforces an atomic **Fluent Chaining** standard for rock-solid hardware reliability without register glitches:

```javascript
// Atomic output configuration
const relay = GPIO.output(15)
    .openDrain(true)
    .pullUp()
    .invert(true)
    .initial(false);

// Hardware button detector with zero CPU idle overhead
const btn = GPIO.input(9)
    .pullUp()
    .button()
    .clickMs(350)
    .doubleClickMs(250)
    .longPressMs(800);

// Event-driven reactive loop
while (true) {
    const gesture = btn.wait(); // Wakes up only when event arrives

    if (gesture === Button.CLICK) {
        relay.write(!relay.read());
    }
}
```

---

## 🚀 Key Capabilities

- **Sub-20ms Hot-Swap Deployment**: Update running tasks on hardware in real time without dropping network connections or rebooting.
- **Pure Reactive Reactor**: Processor sleeps in deep low-power state and wakes up instantly on hardware interrupt queues.
- **Docs-Driven Snippets**: Toolbar code snippets are generated directly from the official documentation, complete with one-click `📖` links to full articles.
- **Live Digital Twin**: Real-time pin state, PWM duty cycle, and ADC voltage monitoring directly in Studio.
- **Persistent User Data**: Your automation scripts, node passports, and MQTT settings live safely in `%APPDATA%\FerrumOS\`. Updating Studio never overwrites your work.
- **Home Assistant MQTT Auto-Discovery**: Automatic self-publishing entities for Home Assistant Lovelace dashboards.
- **Deep Sleep & Micro-Amp Telemetry**: Native battery monitoring with PDS sleep and instant retention RAM wake-up.

---

## 🔌 Supported Hardware

| Microcontroller / Board | Architecture | Radios | Primary Use-Cases |
|---|---|---|---|
| **ESP32-C6 SuperMini** | RISC-V (rv32imac, 160MHz) | Wi-Fi 6, 802.15.4 (Thread / Zigbee), BLE 5 | Thread Router / End-Device, Home Assistant Nodes |
| **ESP32-C3 DevKit** | RISC-V (rv32imc, 160MHz) | Wi-Fi 4, BLE 5 | Standalone Wi-Fi Sensors, Smart Relays |
| **BouffaloLab BL702** | RISC-V (rv32imac, 144MHz) | Zigbee, BLE 5 | Ultra-low-power battery tags, ESL displays |

---

## 📋 Architectural Proposals & RFCs

FerrumOS uses formal **RFCs (Request for Comments)** to engineer protocols and hardware features before implementation.

Have a protocol request or want to see upcoming subsystems?
- **[RFC Registry & Statuses](https://atitoff-dotcom.github.io/FerrumOS/rfcs/)**
  - `RFC-0001`: Distributed CAN (TWAI) Bus
  - `RFC-0007`: Brokerless P2P Fabric (Thread / UDP Multicast)
  - `RFC-0010`: Unified Boiler Stack (BSB, OpenTherm, eBUS)
  - `RFC-0011`: Embedded WSRPC & Lightweight Crypto
  - `RFC-0012`: Network Time Synchronization & Events

---

## 📄 License

- **FerrumOS Studio & Tools**: Licensed under the [Apache 2.0 License](LICENSE).
- **FerrumOS Core Real-Time Engine**: Distributed as pre-compiled binary firmware.
