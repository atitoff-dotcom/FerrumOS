# FerrumOS

> **Reactive Micro-OS & Live Hot-Swap Studio for RISC-V & ESP32 Microcontrollers.**

[![Release: v0.6.0](https://img.shields.io/badge/Release-v0.6.0-blue.svg)](releases/v0.6.0/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Platform: Windows 10%2F11](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6.svg?logo=windows)](#downloads)
[![Target: RISC-V](https://img.shields.io/badge/Target-RISC--V%20(ESP32--C6%20%7C%20C3)-orange.svg)](#supported-hardware)

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

---

## 📐 Fluent Chaining JavaScript API

FerrumOS enforces an atomic **Fluent Chaining** standard for rock-solid hardware reliability without register glitches:

```javascript
// Atomic output configuration
const relay = GPIO.output(15)
    .openDrain(true)
    .pullUp()
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
- **Docs-Driven Snippets**: Toolbar code snippets are generated directly from the official documentation, complete with one-click `📖` links to full articles.
- **Built-in Diátaxis Knowledge Base**: 52 structured guide articles (Tutorials, How-To, Reference, Architecture) accessible directly inside Studio (`F1`).
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

## 📄 License

- **FerrumOS Studio & Tools**: Licensed under the [Apache 2.0 License](LICENSE).
- **FerrumOS Core Real-Time Engine**: Distributed as pre-compiled binary firmware.
