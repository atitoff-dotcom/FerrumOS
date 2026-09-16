# Tutorial 2: First Climate Sensor (I2C)

`Status: 🟢 Stable (v5.0)` • `Targets: ESP32-C6, ESP32-C3` • `Bus: I2C Master`

In this tutorial, you will connect an I2C temperature and humidity sensor (AHT20 or SHT40) to your microcontroller and stream sensor telemetry to FerrumOS Studio.

---

## Hardware Wiring

Connect your sensor to the microcontroller using the I2C bus:

| Sensor Pin | ESP32-C6 / ESP32-C3 Pin | Description |
|---|---|---|
| **VCC** | 3.3V | Power Supply (3.3V) |
| **GND** | GND | Ground |
| **SDA** | GPIO 18 (C6) / GPIO 4 (C3) | I2C Serial Data |
| **SCL** | GPIO 19 (C6) / GPIO 5 (C3) | I2C Serial Clock |

---

## Writing the I2C Telemetry Script

Create a new script named `climate.js` in the FerrumOS Studio editor:

<!-- snippet: id="i2c_sensor_aht20" category="Шины данных (I2C / SPI)" title="Опрос I2C датчика (AHT20)" icon="fa-thermometer-half" desc="Считывание температуры и влажности с калиброванного цифрового датчика AHT20." badges="['I2C 400kHz', 'AHT20', 'Raw Data']" -->
```javascript
// Configure the I2C bus with fluent chaining
const bus = I2C.bus(0)
    .frequency(400000);

// Initialize sensor (AHT20 address: 0x38)
const AHT20_ADDR = 0x38;
bus.writeTo(AHT20_ADDR, [0xBE, 0x08, 0x00]);
delay(20);

// Main measurement loop
while (true) {
    // Trigger measurement: 0xAC, 0x33, 0x00
    bus.writeTo(AHT20_ADDR, [0xAC, 0x33, 0x00]);
    delay(80);

    // Read 6 bytes of raw data
    const raw = bus.readFrom(AHT20_ADDR, 6);
    
    // Calculate humidity (20-bit value)
    const rawH = ((raw[1] << 12) | (raw[2] << 4) | (raw[3] >> 4));
    const humidity = (rawH * 100) / 1048576;

    // Calculate temperature (20-bit value)
    const rawT = (((raw[3] & 0x0F) << 16) | (raw[4] << 8) | raw[5]);
    const tempC = ((rawT * 200) / 1048576) - 50;

    // Publish telemetry to FerrumOS Studio
    System.log(`Temp: ${tempC.toFixed(1)}°C, Humidity: ${humidity.toFixed(1)}%`);

    delay(2000);
}
```

---

## Observing Telemetry

1. Click **Run** (`Ctrl+Enter`).
2. Watch the live console in FerrumOS Studio. Every 2 seconds, calibrated environmental readings will arrive.
3. If an error occurs (such as an unconnected cable or NACK on the I2C bus), the FerrumOS hardware layer safely reports an error code without crashing the core operating system.

Continue to [Tutorial 3: Smart Button Gestures](03_smart_button.md).
