# JavaScript Fluent API Reference

`Status: 🟢 Stable (v5.0)` • `Standard: Method Chaining (Fluent)` • `Compiler: Ferrum Engine`

FerrumOS scripts are written in **Modern Human-JS**, a high-level, embedded JavaScript subset compiled into compact bytecode for the FerrumOS Virtual Machine.

---

## The Fluent Chaining Standard

In FerrumOS, all hardware initialization follows the **Fluent Chaining (Method Chaining)** design pattern:

```javascript
// Correct: Atomic method chaining
const relay = GPIO.output(15)
    .openDrain(true)
    .pullUp()
    .invert(true)
    .initial(false);
```

### Why Chaining is Required
1. **Atomic Hardware Configuration**: Chained methods compile into a single atomic hardware configuration command (`OP_BIND_GPIO` with bitmask flags).
2. **Glitch Prevention**: Step-by-step property mutations can leave GPIO pins in intermediate floating or wrongly-driven states for several microseconds, potentially causing relay contact bouncing or triggering attached circuits.
3. **Memory Efficiency**: Chained method calls are resolved at compile-time into static opcodes, requiring zero object allocations on the microcontroller heap.

---

## API Modules

- [Reactive Signals & IPC](signals.md) — Inter-script communication, reactive state variables, and watchers.
- [GPIO](gpio.md) — Digital outputs, inputs, hardware debounce filters, and gesture detection.
- [I2C](i2c.md) — Master I2C bus transactions, register reads/writes, sensor drivers.
- [SPI](spi.md) — High-speed SPI transactions for displays and radio transceivers.
- [ADC](adc.md) — Analog-to-digital converter, voltage attenuation, multisampling.
- [PWM & WS2812](pwm_ws2812.md) — Hardware pulse-width modulation and addressable RGB LEDs.
- [UART & Modbus](uart_modbus.md) — Serial communications, industrial Modbus RTU frames.
- [Power & Sleep](power_sleep.md) — PDS sleep modes, retention RAM, and wake pin sources.
- [Thread Network](thread_network.md) — 802.15.4 low-power mesh networking, UDP, and CoAP endpoints.
