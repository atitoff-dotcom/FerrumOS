# I2C Bus Reference

The `I2C` module provides master interface control over hardware I2C peripherals.

---

## Initializing an I2C Bus: `I2C.bus(bus_id)`

```javascript
const bus = I2C.bus(0)
    .frequency(400000);
```

### Configuration Methods
- `.frequency(hz: number)` — Sets clock speed in Hertz (e.g. `100000` for Standard, `400000` for Fast mode).
- `.timeoutMs(ms: number)` — Transaction timeout in milliseconds.

### Data Transfer Methods
- `bus.writeTo(addr: number, bytes: number[]): void` — Writes an array of bytes to a 7-bit slave address.
- `bus.readFrom(addr: number, length: number): number[]` — Reads `length` bytes from a slave device.
- `bus.writeRead(addr: number, writeBytes: number[], readLength: number): number[]` — Performs atomic write followed by repeated start read.

---

## Example: Reading Temperature Register

<!-- snippet: id="i2c_bus" category="Шины данных (I2C / SPI)" title="Шина I2C (Чтение регистра)" icon="fa-microchip" desc="Инициализация шины I2C и чтение регистра данных датчика." badges="['I2C Master', '100kHz', 'Repeated Start']" -->
```javascript
const bus = I2C.bus(0)
    .frequency(100000);

// Read 2 bytes from register 0x00 on device 0x48
const data = bus.writeRead(0x48, [0x00], 2);
const tempRaw = (data[0] << 8) | data[1];
console.log(`Raw Temp: ${tempRaw}`);
```
