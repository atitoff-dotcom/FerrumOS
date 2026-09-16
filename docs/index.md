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

<div class="grid cards" markdown="1">

-   ### 🚀 Quick Start Guide

    Flash your board and deploy your first script in under 3 minutes.

    [**Start Tutorial →**](1_getting_started/01_quickstart.md)

-   ### 📥 Download Studio

    Standalone Windows Installer or Portable zero-dependency edition.

    [**Get v0.6.0 →**](https://github.com/atitoff-dotcom/FerrumOS/releases)

-   ### 📖 Fluent JS API

    Explore the complete atomic method chaining hardware reference.

    [**Browse API →**](3_reference/js_api/index.md)

-   ### 📋 RFC Registry

    Inspect architectural proposals, protocols (CAN, BSB/OpenTherm), and specs.

    [**View RFCs →**](rfcs/index.md)

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

## 🧭 Complete Documentation Directory

### 🚀 Getting Started
- [01. Quickstart](1_getting_started/01_quickstart.md) — Connect your board and run your first reactive script.
- [02. First Sensor](1_getting_started/02_first_sensor.md) — I2C sensor bus configuration and telemetry.
- [03. Smart Button](1_getting_started/03_smart_button.md) — Offload debounce and click gestures to hardware.
- [04. Troubleshooting & FAQ](1_getting_started/04_troubleshooting.md) — USB drivers, COM port access, and flash recovery.

### 💡 Recipes & How-To Guides
- [Home Assistant & MQTT](2_recipes/home_assistant_mqtt.md) — Zero-configuration MQTT Auto-Discovery.
- [Battery Deep Sleep](2_recipes/battery_deep_sleep.md) — Retention RAM, PDS sleep, and micro-amp telemetry.
- [Inter-Script Signals (IPC)](2_recipes/inter_script_signals.md) — Lock-free task communication and decoupled architecture.
- [CAN Bus Networking](2_recipes/can_networking.md) — Multi-node distributed signals over TWAI.
- [Electronic Shelf Labels (E-Paper)](2_recipes/esl_display.md) — Ultra-low-power E-Ink displays.
- [OTA Firmware Updates](2_recipes/ota_firmware_update.md) — Hot-swap bytecode and A/B dual-boot recovery.

### 📖 API Reference
- [JavaScript Fluent API Overview](3_reference/js_api/index.md) — Atomic method chaining guidelines.
- [Reactive Signals & IPC](3_reference/js_api/signals.md) — Inter-script communication and watchers.
- [GPIO (Digital Pins)](3_reference/js_api/gpio.md) — Input/output pin configuration and gestures.
- [ADC (Analog Inputs)](3_reference/js_api/adc.md) — Voltage attenuation and multisampling.
- [I2C Bus](3_reference/js_api/i2c.md) — Master transactions and sensor reading.
- [SPI Bus](3_reference/js_api/spi.md) — High-speed display and flash memory access.
- [PWM & WS2812](3_reference/js_api/pwm_ws2812.md) — Hardware PWM and addressable LED control.
- [Power & Sleep](3_reference/js_api/power_sleep.md) — Energy management and wake triggers.
- [Thread Network](3_reference/js_api/thread_network.md) — 802.15.4 low-power mesh networking.
- [UART & Modbus](3_reference/js_api/uart_modbus.md) — Serial and Modbus RTU communications.
- [Ferrum CLI Reference](3_reference/cli.md) — Command-line build, flash, and pack tools.

### ⚙️ Architecture & Concepts
- [Fluent Chaining Standard](4_concepts/fluent_chaining.md) — Why method chaining prevents pin glitches.
- [Sub-20ms Live Hot-Swap](4_concepts/hot_swap_15ms.md) — How code updates without restarting the chip.
- [Reactive Event Reactor](4_concepts/reactive_events.md) — Event queues vs wasteful blocking delays.
- [Zero-Copy Signal Bus](4_concepts/reactive_signals.md) — IPC architecture and version-tracked transitions.
- [Digital Twin & Telemetry](4_concepts/digital_twin.md) — Live visual pin state mirroring in Studio.

### 📐 Architectural Proposals & RFCs
- [RFC Registry & Statuses](rfcs/index.md) — Status matrix for all upcoming protocols and subsystems.
