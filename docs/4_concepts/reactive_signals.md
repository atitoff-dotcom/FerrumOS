# Architecture of Reactive Signals

FerrumOS employs a **Zero-Copy Reactive IPC Signal Bus** for high-speed, thread-safe communication between concurrent user scripts, device drivers, and the network stack.

---

## ⚡ Why Traditional Multitasking Fails on MCUs

In traditional embedded platforms (FreeRTOS with C++, MicroPython, or Arduino):
1. **Mutex Contention & Deadlocks**: Sharing global state requires mutual exclusion locks. On microcontrollers with limited hardware debugging, priority inversions and deadlocks freeze the entire chip.
2. **Heap Thrashing**: Passing message payloads through dynamic queues causes memory fragmentation and out-of-memory panics.
3. **High CPU Polling Overhead**: Checking a state flag in a `while (flag == 0)` loop wastes valuable milliampere battery budget.

---

## 🛡️ The FerrumOS IPC Bus Architecture

FerrumOS eliminates locks and dynamic allocations by using a statically pre-allocated **IPC Signal Table** in RAM:

```
                  ┌────────────────────────────────────────┐
                  │          FerrumOS IPC Bus Table        │
                  │  Slot 0: [ Value | Version | Mask ]    │
                  │  Slot 1: [ Value | Version | Mask ]    │
                  │  ...                                   │
                  │  Slot 63:[ Value | Version | Mask ]    │
                  └───────────────────▲────────────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               │                                             │
      OP_SIGNAL_SET                                  OP_SIGNAL_WAIT
(Producer: Version increment)                 (Consumer: WFI Sleep until version !=)
               │                                             │
      ┌────────┴────────┐                           ┌────────┴────────┐
      │ Climate Sensor  │                           │ Relay Actuator  │
      │   (Script 1)    │                           │   (Script 2)    │
      └─────────────────┘                           └─────────────────┘
```

### 1. Static 64-Slot Array
All signals reside in a static, cache-aligned table of 64 slots. Topic strings (e.g. `"living/temp"`) are hashed to slot indices using the fast FNV-1a algorithm at compile time.

### 2. Version-Tracked Atomic Transitions
Each slot contains:
- `value: i32` (Integer, float, or boolean value representation);
- `version: u32` (Monotonically increasing modification counter);
- `subscribers_mask: u32` (Bitmask of waiting task IDs).

When a producer writes a new value via `OP_SIGNAL_SET`:
1. If the value is new, the version counter increments atomically within a hardware critical section.
2. The kernel checks the `subscribers_mask` and immediately shifts waiting tasks from `WaitingSignal` to `Runnable`.

### 3. Pure Reactive Yield (`OP_SIGNAL_WAIT`)
When a consumer calls `signal.watch()`, the VM executes `OP_SIGNAL_WAIT`. The task yields immediately, and the RISC-V CPU executes `WFI` (Wait For Interrupt). It draws near-zero current until the signal version increments.

---

## 🌐 One Signal, Three Worlds

The power of FerrumOS signals lies in their seamless transparency:

```javascript
const motion = state.signal("hall/motion", false)
    .can(15)                                            // World 1: CAN Bus (Automotive / Factory)
    .exposeHA("binary_sensor", { name: "Hall Motion" });// World 2: Smart Home (Home Assistant)
                                                        // World 3: Local Script (Direct GPIO)
```

1. **Local**: Scripts running on the same ESP32 react within microseconds.
2. **Distributed**: Connected boards on the CAN bus receive the packet via TWAI and update their local signal mirrors.
3. **Cloud & Edge**: Home Assistant receives the MQTT state update with zero manual YAML glue code.
