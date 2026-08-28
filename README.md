# FerrumOS

> **The Next-Generation Real-Time Reactive Micro-OS & Live Hot-Swap Studio for RISC-V & ESP32 Microcontrollers.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Target: ESP32-C6](https://img.shields.io/badge/Target-ESP32--C6%20RISC--V-orange.svg)](#hardware-support)

FerrumOS is an ultra-fast, bare-metal reactive operating system and live development environment designed for IoT, robotics, and smart home edge devices.

Write pure **JavaScript/TypeScript**, deploy tasks to running hardware in **15 milliseconds over Wi-Fi without restarting the chip**, and monitor live pin matrices and digital twin states in real time.

## Key Features

- **Sub-20ms Hot-Swap Deployment**: Inject and update live tasks on running microcontrollers without reboots.
- **Pre-Flight Digital Twin Verification**: Pre-checks GPIO, I2C, SPI and memory collisions before deploy.
- **Reactive Event-Driven Core**: Async waiting (btn.wait(), ipc.wait(), mqtt.wait()) with near-zero idle power.
- **Modern Studio IDE**: Full-featured Web & Desktop IDE built with Svelte 5, Tailwind 4, and CodeMirror.
- **Open Driver Ecosystem**: Anyone can write and contribute sensor drivers in pure JavaScript in packages/.

## Quick Start (60 Seconds)

### 1. Flash FerrumOS Core to ESP32-C6
`ash
esptool.py --chip esp32c6 write_flash 0x0 firmware/releases/esp32c6/ferrumos-core-esp32c6-v0.4.0.bin
`

### 2. Launch FerrumOS Studio
`ash
cd studio
pip install fastapi uvicorn websockets paho-mqtt
python web.py
`
Open http://localhost:8000 in your browser.

## License
- **FerrumOS Studio, Compiler, Packages & SDK**: Apache 2.0 License.
- **FerrumOS Core Engine**: Free binary distribution.
