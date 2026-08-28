# System Architecture & Design Principles

**FerrumOS** is a high-performance, modular, fault-tolerant microkernel IoT platform written in **Rust** with support for dynamic execution of **JavaScript / Rhai** scripts and hot-loadable WASM AOT driver modules on microcontrollers like the **ESP32-C6** (RISC-V) and ARM Cortex-M.

---

## 🏗️ 4-Tier Memory & Partition Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. SYSTEM BASE TIER (Persistent ~800 KB)                               │
├────────────────────────────────────────────────────────────────────────┤
│ - Network & Radio Stack: ESP-IDF Bootloader, Wi-Fi 6 / Thread / BLE 5.0│
│ - Hardware HAL: esp-hal (GPIO, I2C, SPI, UART, TimerGroup, RNG)       │
│ - Network Sockets: smoltcp + esp-wifi (no_std TCP/IP, DHCP, DNS)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Direct Kernel Syscalls
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. FERRUMOS MICROKERNEL CORE TIER (OTA-updatable ~350–680 KB)            │
├────────────────────────────────────────────────────────────────────────┤
│ - Rhai / JS Scripting Engine (no_std, only_i32, zero-cost coroutines)  │
│ - Script Registry (ScriptRegistry: CRUD, hot-swapping, lifecycle state)│
│ - Embedded HTTP REST Server & Glassmorphism Web Dashboard (Port 80)    │
│ - Fault Isolation Supervisor (ScriptSupervisor)                        │
│ - Inter-Script Blackboard State Bus (state) & Message Queues (queue)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Dynamic WASM AOT Driver API (.aot)
┌───────────────────────────────────▼────────────────────────────────────┐
│ 3. DYNAMIC NATIVE WASM DRIVERS (OTA slots 15–30 KB .aot)               │
├───────────────────┬───────────────────┬────────────────────────────────┤
│  CAN_Bus_Drv.aot  │  Modbus_TCP.aot   │  EInk_Display_Drv.aot          │
│  (Hot Swap)       │  (Hot Swap)       │  (Hot Swap)                    │
└───────────────────┴───────────────────┴────────────────────────────────┘
                                    │ Safe functions exported to JS/Rhai
┌───────────────────────────────────▼────────────────────────────────────┐
│ 4. ISOLATED USER JS / RHAI SCRIPTS (Instant OTA in ~0.05s to RAM)      │
├───────────────────┬───────────────────┬────────────────────────────────┤
│  Climate_Ctrl.js  │ Security_Alarm.js │  Light_Automation.js           │
│  (Status: Active) │ (Status: Active)  │  (Status: Isolated Log)        │
└───────────────────┴───────────────────┴────────────────────────────────┘
```

---

## ⚡ 1. Zero-Cost State Machine Coroutines (Threadless Non-Blocking I/O)

The core architectural breakthrough in FerrumOS is the elimination of heavy FreeRTOS thread stacks in favor of **Rust cooperative state machine coroutines**:

### The Problem with Traditional RTOS:
* In standard RTOS platforms (FreeRTOS, Zephyr), each task thread requires a dedicated 4–8 KB RAM stack.
* Running 10 concurrent scripts consumes 80+ KB of RAM purely for task stacks.
* Heavy context switches incur CPU overhead.

### The FerrumOS Solution:
1. **Developer Experience (Linear JS DX):**
   Developers write clean, linear synchronous code:
   ```javascript
   let line = device.uart("GPS").read_line(1000);
   delay_ms(500);
   ```
2. **Rust Kernel State Machine (`enum ScriptExecutionState`):**
   ```rust
   pub enum ScriptExecutionState {
       Ready,
       WaitingTimer { wake_at: Instant },
       WaitingUart { timeout_at: Instant },
       WaitingQueue { channel: String, timeout_at: Instant },
       WaitingBus,
   }
   ```
3. **Instant Microsecond `yield`:**
   Calling `delay_ms()` or waiting for sensor/queue data suspends the script step and immediately returns execution to the main kernel loop.
4. **Background Hardware Ring Buffers:**
   Interrupt-driven hardware peripherals push bytes into lock-free `RingBuffer` queues in the background. As soon as data arrives, the kernel wakes the waiting script.
5. **Extreme RAM Efficiency:**
   10+ concurrently running scripts consume only **~4–8 KB RAM** in total instead of 80+ KB.

---

## 🗄️ 2. Inter-Script Communication (IPC Architecture)

FerrumOS brings microservices architecture to embedded microcontrollers:

```
┌──────────────────┐       queue.send("telemetry")      ┌────────────────────────┐
│  DS18B20 Sensor  │ ─────────────────────────────────► │  Thermostat Controller │
│ (Data Collector) │ ◄───────────────────────────────── │     (Control Logic)    │
└────────┬─────────┘       state.set("climate.temp")    └───────────┬────────────┘
         │                                                          │
         │ state.get("climate.temp")                                │ events.emit("alert")
         ▼                                                          ▼
┌────────────────────────┐                             ┌────────────────────────┐
│    MQTT Cloud Sync     │                             │  Security Siren Alarm  │
│  (Network Telemetry)   │                             │   (Event-Driven Bus)   │
└────────────────────────┘                             └────────────────────────┘
```

### IPC Building Blocks:
1. **Shared Blackboard State Bus (`state` - KV Store):**
   - Thread-safe `Mutex<BTreeMap<String, Dynamic>>`.
   - Atomic atomic get/set operations (`state.get`, `state.set`, `state.has`, `state.delete`).
   - Crash isolation: A failure in a producer script never destroys the global state.
2. **Message Queues (`queue` - FIFO Channels):**
   - Bounded ring buffer memory (16–32 messages per channel) protecting against memory overflow.
   - Non-blocking `queue.receive(channel, timeout_ms)` with automatic cooperative yielding.
3. **Event Bus (`events` - Pub/Sub):**
   - Reactive broadcast of discrete event triggers (`events.emit`, `events.on`).

---

## 🌐 3. Built-In Networking & Wi-Fi OTA Microkernel

The native firmware (`crates/esp32c6-firmware`) includes a standalone network stack:

1. **`esp-wifi` + `smoltcp` (no_std):**
   - Native Wi-Fi 802.11 b/g/n/ax STA mode.
   - Automatic IP allocation via integrated DHCP client.
   - Lightweight TCP/IP sockets without standard library dependencies.
2. **Embedded HTTP REST Server (`crates/esp32c6-firmware/src/http_server.rs`):**
   - Listens on standard port 80.
   - Serves built-in Glassmorphism Web Dashboard (`GET /`).
   - REST API for live script lifecycle control:
     - `GET /api/scripts` — List registered scripts, states, and execution counts.
     - `POST /api/scripts` — Upload and start new script dynamically.
     - `PUT /api/scripts/<id>` — Hot-swap script code in RAM.
     - `DELETE /api/scripts/<id>` — Delete script and stop execution.

---

## 🗂️ 4. Host Digital Twin & Contextual Pre-Flight Cross-Validation

To provide deterministic fleet orchestration without physical hardware pin conflicts, FerrumOS implements a local **Digital Twin** subsystem:

```
storage/nodes/<node_id>/
├── device.json          # Node passport (board, RAM, Flash, MAC, IP, constraints)
├── current/             # Live mirror of running tasks in microcontroller RAM
│   ├── state.json       # Manifest of active tasks and claimed pins/busses
│   ├── task.js          # JS Source code
│   └── task.rhb         # Compiled binary bytecode container
└── snapshots/           # Timestamped versioned archives with instant rollback
    └── snapshot_<ts>_<label>/
```

### Contextual Pre-Flight Cross-Validator (`validator.py`):
1. **Multi-Task Pin Collision Prevention:** Before flashing, candidate tasks are checked against all pins already in use by active tasks in RAM.
2. **Shared Busses vs. Exclusive Claims:**
   - Exclusive claims (Direct GPIO, RGB WS2812) cannot be shared across different tasks.
   - Shared Busses (I2C) permit shared SDA/SCL pins while validating sensor device address collisions.
3. **Safe Self-Update:** Tasks updating an existing task name (`task_id`) are permitted to reuse their existing pin claims without false conflicts.

---

## 📬 5. Inter-Script IPC & Unified Single-Line Publish

The firmware kernel includes a zero-overhead `IpcBus` broker (`crates/esp32c6-firmware/src/ipc.rs`):
- **MPSC FIFO Message Queues:** `ipc.send(topic, val)`, `ipc.recv(topic)`, `ipc.available(topic)`.
- **Shared Reactive State:** `state.set(key, val)`, `state.get(key)`.
- **Atomic Single-Line Publish:** `ipc.publish(topic, val)` (`OP_IPC_PUBLISH` 0x25) writes to FIFO subscriber queues **and** updates the latest shared state in one instruction.

---

## 📊 ESP32-C6 Memory Distribution (512 KB SRAM)

| Subsystem | SRAM Usage | Purpose |
|---|---|---|
| **Wi-Fi 6 + smoltcp** | ~60 KB | Radio driver, TCP sockets, packet buffers |
| **FerrumOS Kernel Core + RWP** | ~35 KB | Task registry, VM scheduler, IpcBus, RWP dispatcher |
| **esp-alloc Heap** | 160 KB | Dynamic memory for sandboxed VM execution |
| **Free SRAM Margin** | **> 250 KB** | Available for user data, buffers, and cache |
