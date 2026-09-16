<p align="center">
  <img src="assets/logo.png" alt="FerrumOS Logo" width="130" height="130" style="border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);">
</p>

# FerrumOS

> **Reactive Micro-OS & Live Hot-Swap Studio for RISC-V & ESP32 Microcontrollers.**

[![Release: v0.6.0](https://img.shields.io/badge/Release-v0.6.0-blue.svg)](https://github.com/atitoff-dotcom/FerrumOS/releases)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://github.com/atitoff-dotcom/FerrumOS/blob/master/LICENSE)
[![Platform: Windows 10%2F11](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6.svg?logo=windows)](https://github.com/atitoff-dotcom/FerrumOS/releases)
[![Target: RISC-V](https://img.shields.io/badge/Target-RISC--V%20(ESP32--C6%20%7C%20C3)-orange.svg)](https://github.com/atitoff-dotcom/FerrumOS#supported-hardware)

---

FerrumOS is an ultra-fast, bare-metal reactive micro-operating system and live development environment for IoT edge devices, sensors, and smart home automation.

Write clean **Modern JavaScript**, deploy tasks to running hardware in **15 milliseconds over USB / Wi-Fi without restarting the chip**, and monitor live digital twins and pinout telemetry in real time.

---

## ⚡ Quick Action

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Quick Start Guide__

    ---

    Flash your board and deploy your first script in under 3 minutes.

    [:octicons-arrow-right-24: Start Tutorial](1_getting_started/01_quickstart.md)

-   :material-download:{ .lg .middle } __Download Studio__

    ---

    Standalone Windows Installer or Portable zero-dependency edition.

    [:octicons-arrow-right-24: Get v0.6.0](https://github.com/atitoff-dotcom/FerrumOS/releases)

-   :material-book-open-page-variant:{ .lg .middle } __Fluent JS API__

    ---

    Explore the complete atomic method chaining hardware reference.

    [:octicons-arrow-right-24: Browse API](3_reference/js_api/index.md)

-   :material-file-document-edit:{ .lg .middle } __RFC Registry__

    ---

    Inspect architectural proposals, protocols (CAN, BSB/OpenTherm), and specs.

    [:octicons-arrow-right-24: View RFCs](rfcs/index.md)

</div>

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
- **Pure Reactive Event Model**: CPU sleeps in ultra-low power state and wakes up instantly on hardware interrupt queues.
- **Live Digital Twin**: Real-time pin state, PWM duty cycle, and ADC voltage monitoring directly in Studio.
- **Home Assistant MQTT Auto-Discovery**: Automatic self-publishing entities for Home Assistant Lovelace dashboards.
- **Zero-Glitch Atomic I/O**: Eliminates voltage spikes and half-initialized states on sensitive relays and MOSFETs.

---

## 🔌 Supported Hardware

| Microcontroller / Board | Architecture | Radios | Primary Use-Cases |
|---|---|---|---|
| **ESP32-C6 SuperMini** | RISC-V (rv32imac, 160MHz) | Wi-Fi 6, 802.15.4 (Thread / Zigbee), BLE 5 | Thread Router / End-Device, Home Assistant Nodes |
| **ESP32-C3 DevKit** | RISC-V (rv32imc, 160MHz) | Wi-Fi 4, BLE 5 | Standalone Wi-Fi Sensors, Smart Relays |
| **BouffaloLab BL702** | RISC-V (rv32imac, 144MHz) | Zigbee, BLE 5 | Ultra-low-power battery tags, ESL displays |

---

## 🧭 Documentation Sections

- **[🚀 Getting Started](1_getting_started/01_quickstart.md)** — Step-by-step guides from unboxing to first automation.
- **[💡 Recipes & How-To](2_recipes/home_assistant_mqtt.md)** — Ready-to-copy solutions for Home Assistant, Deep Sleep, CAN bus, and E-Paper.
- **[📖 API Reference](3_reference/js_api/index.md)** — Comprehensive documentation of `GPIO`, `ADC`, `I2C`, `SPI`, `Power`, `CLI`.
- **[⚙️ Concepts](4_concepts/fluent_chaining.md)** — Core engineering ideas: Fluent Chaining, Hot-Swap, and Reactive execution.
- **[📐 RFCs & Roadmap](rfcs/index.md)** — Future protocols, community proposals, and development status.
