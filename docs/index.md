# FerrumOS Documentation

Welcome to the official technical documentation for **FerrumOS** — a modular, fault-tolerant IoT microkernel operating system built with Rust and embedded JavaScript/Rhai scripting for ESP32-C6 and host simulators.

---

## 📚 Documentation Table of Contents

1. [Architecture Overview](architecture.md)
   - 4-Tier memory and partition layout (System Base, FerrumOS Core, WASM Drivers, JS/Rhai Scripts)
   - Zero-Cost State Machine Coroutines: Non-blocking I/O without heavy FreeRTOS thread stacks
   - Inter-Script Communication (IPC): Shared Blackboard `state`, FIFO `queue`, Pub/Sub `events`
   - Integrated networking: `esp-wifi` + `smoltcp` and embedded HTTP REST Server (Port 80)
   - WAMR AOT micro-runtime & offline compilation pipeline (`wamrc`)
   - Fault isolation supervisor (`ScriptSupervisor`)
   - ESP32-C6 memory budget and SRAM distribution

2. [Scripting API Reference (JavaScript & Rhai)](api_reference.md)
   - Zero-Cost Coroutines (`delay_ms`, non-blocking cooperative execution)
   - System logging (`console.log`, `console.error`)
   - Mathematical utilities (`Math.*`)
   - JSON serialization (`JSON.stringify`, `JSON.parse`)
   - Shared Blackboard Key-Value Store (`state.get`, `state.set`, `state.has`, `state.delete`)
   - Message Queues (`queue.send`, `queue.receive`) & Events (`events.emit`, `events.on`)
   - Hardware `device` API:
     - GPIO (`read`, `write`)
     - PWM / LEDC dimmers & servos (`set_duty`, `set_angle`)
     - 1-Wire DS18B20 temperature probes (`read`)
     - I2C, SPI, and UART (`read_line`, `write`)
   - Dynamic pin self-binding (`bind_gpio_output`, `bind_pwm`, `bind_onewire_bus`, `bind_i2c_bus`, `bind_uart`)
   - Industrial Modbus RTU / TCP (`modbus.read_holding`, `modbus.write_single`)
   - Matter Smart Home protocol (`matter.endpoint`, `on_command`, `set`)
   - Telemetry publishing (`mqtt.publish`)
   - Error handling (`try { ... } catch (err) { ... }`)

3. [Web UI Control Center & REST API Guide](web_ui_and_rest.md)
   - Embedded Glassmorphism Dashboard (`http://<device_ip>/` on ESP32-C6, `http://localhost:8080` on PC)
   - Instant OTA script deployment in <0.05 seconds directly from browser
   - REST API endpoints reference (`GET`, `POST`, `PUT`, `DELETE` at `/api/scripts`)

4. [Fleet Management & Pin Conflict Validation](fleet_management.md)
   - Python CLI orchestrator (`tools/fleet_manager.py`)
   - Pre-deployment hardware pin collision checker
   - Centralized fleet inventory (`tools/fleet.json`)
   - Status, deployment, and validation commands

5. [Electronic Shelf Labels (ESL) & Sub-1 µA Target](esl_electronic_shelf_label.md)
   - 10+ year battery lifespan on single CR2032 (3-hour sleep cycle)
   - $0.02 discrete power-latch circuit
   - E-Paper integration with BL702 / TLSR8258
   - JS/Rhai shelf label template script

6. [ESP32-C6 Native Firmware Guide](esp32c6_native_firmware.md)
   - RISC-V `no_std` architecture (`esp-hal`, `esp-alloc`, `esp-wifi`, `smoltcp`)
   - Flash partition layout and ESP-IDF app descriptor header
   - Binary size optimization (~689 KB)
   - Flashing via `esptool` and `espflash` over USB (`COM3`)
   - Real-time UART monitor

7. [Getting Started & Developer Guide](getting_started.md)
   - Building and testing (`cargo test`, `cargo run`)
   - Release profile tuning (`opt-level = "z"`, LTO, strip)

8. [Development Roadmap & Backlog](../ROADMAP.md)
   - Upcoming drivers: DS18B20 1-Wire, Modbus RTU RS485, PWM LEDC
   - Cross-platform support: BL602 (RISC-V), RP2040, STM32
