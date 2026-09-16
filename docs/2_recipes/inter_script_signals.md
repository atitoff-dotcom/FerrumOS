# How-To: Inter-Script IPC & Reactive Signals

FerrumOS enables multiple lightweight JavaScript tasks to execute concurrently on the microcontroller. Instead of sharing global variables or dealing with locks, tasks communicate via lock-free, event-driven **Reactive Signals (`state.signal`)**.

---

## 🎯 Architectural Pattern: Decoupled Tasks

```
  ┌───────────────────────────┐         ┌───────────────────────────┐
  │ Task 1: Climate Sensor    │         │ Task 2: Relay Controller  │
  │ • Reads ADC or I2C sensor │         │ • Listens for changes     │
  │ • Updates temp signal     │         │ • Controls cooling/fan    │
  └─────────────┬─────────────┘         └─────────────▲─────────────┘
                │                                     │
                │ temp = 27.5                         │ .watch((val) => ...)
                ▼                                     │
  ═══════════════════════════════════════════════════════════════════
                   FerrumOS Real-Time IPC Signal Bus
  ═══════════════════════════════════════════════════════════════════
```

---

## 1. Producer Script: Sensor Telemetry (`sensor.js`)

The producer script acquires physical measurements and publishes them to the IPC bus:

```javascript
// Register or bind to the shared climate signal
const tempSignal = state.signal("room/temperature", 22.0)
    .exposeHA("sensor", { name: "Room Temperature", unit: "°C" });

// Analog sensor input on pin 4 with oversampling
const sensor = ADC.input(4)
    .attenuation(11)
    .samples(32);

while (true) {
    const rawMv = sensor.readMv();
    const tempC = (rawMv - 500) / 10.0; // TMP36 linear formula

    // Publish to the IPC bus (emits OP_SIGNAL_SET)
    tempSignal = tempC;

    // Suspend task for 5 seconds
    power.sleepMs(5000);
}
```

---

## 2. Consumer Script: Actuator Control (`actuator.js`)

The consumer script doesn't know anything about ADC registers or pins. It strictly watches the signal and reacts when thresholds are crossed:

```javascript
// Connect to the same signal topic
const tempSignal = state.signal("room/temperature");

// Configure the cooling fan relay
const fan = GPIO.output(15)
    .openDrain(false)
    .initial(false);

// Reactive watcher: zero CPU overhead until temperature changes
tempSignal.watch((val) => {
    if (val > 28.0) {
        fan.write(true);  // Turn fan ON
    } else if (val < 25.0) {
        fan.write(false); // Turn fan OFF
    }
});
```

---

## 3. Distributed Signals over CAN Bus

To share the same signal across multiple physical boards over a two-wire CAN bus:

```javascript
// Automatically broadcasts signal changes across the CAN bus
const sharedAlarm = state.signal("facility/alarm", false)
    .can(100)
    .urgent();
```

Any board on the CAN bus running a `.watch()` loop on `facility/alarm` will wake up and execute immediately upon packet arrival.
