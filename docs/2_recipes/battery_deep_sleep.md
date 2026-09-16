# How-To: Battery Optimization & Deep Sleep

`Status: 🟢 Stable (v5.0)` • `Targets: ESP32-C6, ESP32-C3, BL702` • `Modes: PDS Sleep, Retention RAM`

This guide explains how to configure a FerrumOS node as an ultra-low-power battery sensor (Thread Sleepy End Device or standalone logger) that can operate for 2–5 years on a single CR2032 or 2×AAA batteries.

---

## 1. Power Topology & Hardware Design

For maximum efficiency:
1. **Direct Battery Connection (2.1V – 3.6V)**: Connect a 3V coin cell (CR2032, CR2450) or 2×AAA cells directly to the microcontroller VDD line without an LDO regulator to eliminate quiescent idle current.
2. **I2C/SPI Pin Isolation**: Ensure external sensor pull-ups do not leak current into grounded bus lines when sleeping.
3. **PDS Sleep Modes**: In RISC-V targets (like BL702 and ESP32-C6 in deep sleep), peripheral power domains are completely unpowered, leaving only the RTC timer and Retention RAM active (~1.5–2 µA).

---

## 2. Retention RAM & Instant Wake-Up

Rejoining a wireless network on every wake-up drains battery. FerrumOS stores network credentials, sequence counters, and parent router routes in **Retention RAM**:
- **Cold Boot Time**: ~250 ms (initial provisioning).
- **Warm Wake-up Time**: **< 15 ms** (wake up, read sensor, transmit single UDP/CoAP frame to parent, return to sleep).

---

## 3. Implementation in JavaScript

```javascript
// Read environmental sensor
const temp = I2C.bus(0).aht20().readTemperature();
const vbat = Power.batteryVoltage();

// Transmit telemetry via low-power Thread network
Thread.endpoint("coap://[fd00::1]/sensors/climate")
    .confirmable(false)
    .payload({ t: temp, v: vbat })
    .send();

// Enter deep sleep for 60 seconds, or wake early on door contact (GPIO 4)
Power.sleep()
    .after(60).seconds()
    .wakeOnPin(4).falling()
    .enter();
```

---

## 4. Key Energy Metrics

| Operating State | Current Draw | Typical Duration |
|---|---|---|
| **Deep Sleep (RTC Active)** | 1.8 µA | 59.98 seconds |
| **Sensor Measurement** | 1.2 mA | 5 ms |
| **Thread Radio Burst (0 dBm)** | 19 mA | 12 ms |
| **Average Current Consumption** | **~5.6 µA** | **Battery Life: ~4.5 Years on CR2450** |
