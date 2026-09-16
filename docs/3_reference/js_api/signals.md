# Reactive Signals & IPC API

`state.signal(topic, initialValue)` provides lock-free, zero-copy Inter-Process Communication (IPC) between concurrent scripts, hardware peripherals, distributed CAN networks, and Home Assistant.

<!-- snippet: id="signal_declare" category="Циклы и задержки" title="Реактивный сигнал (IPC)" icon="fa-bolt" desc="Создание общего реактивного сигнала для межскриптового взаимодействия." badges="['IPC', 'Zero-Copy']" -->
```javascript
// Declare a shared reactive state signal
const temp = state.signal("climate/temp", 20);

// Update signal value atomically (emits OP_SIGNAL_SET)
temp = 24.5;
```

---

## 📐 Method Chaining & Configuration

```javascript
// Signal with Home Assistant and CAN bus bindings
const alarm = state.signal("security/alarm", false)
    .exposeHA("binary_sensor", { name: "Security Alarm" })
    .can(42)
    .urgent();
```

---

## ⚙️ Reactive Watcher (`.watch()`)

The `.watch()` method pauses task execution until the signal value changes. Execution yields to the micro-kernel via the `OP_SIGNAL_WAIT` opcode, consuming zero CPU cycles while waiting.

<!-- snippet: id="signal_watch" category="Циклы и задержки" title="Подписчик сигнала (.watch)" icon="fa-eye" desc="Асинхронная подписка на изменение сигнала без нагрузки на CPU." badges="['Reactive', 'Sleep']" -->
```javascript
const waterTemp = state.signal("boiler/temp", 40);
const heater = GPIO.output(14).initial(false);

waterTemp.watch((val) => {
    // Wakes up only when temperature changes
    heater.write(val < 50);
});
```

---

## 📋 API Specification

### `state.signal(topic: string, initialValue?: number | boolean): Signal`
Registers or looks up an IPC slot in the kernel by its 16-bit FNV-1a topic hash.
- `topic`: Hierarchical channel path (e.g. `"living/temp"`, `"relay/state"`).
- `initialValue`: Optional initial integer, float, or boolean value.

### `.watch(callback: (value: any) => void): void`
Registers a reactive watcher. The enclosing loop yields until a new signal version is published.

### `.exposeHA(component: string, options: object): Signal`
Publishes MQTT Auto-Discovery metadata for Home Assistant:
- `component`: `"sensor"`, `"binary_sensor"`, `"switch"`, or `"number"`.
- `options`: Object containing `name`, `unit`, `icon`, or `device_class`.

### `.can(canId?: number): Signal`
Binds the signal to the hardware CAN / TWAI bus for distributed multi-node broadcast:
- `canId`: Optional 11-bit CAN frame identifier. If omitted, automatically derived from the topic hash.

### `.urgent(): Signal`
Marks the CAN frame with high-priority arbitration flags for instant sub-millisecond transmission.
