# Digital Twin & Live Telemetry

FerrumOS provides a built-in **Digital Twin** architecture that mirrors physical microcontroller pin states directly into FerrumOS Studio in real time.

---

## ⚡ Beyond `print()` Debugging

In standard embedded development, engineers rely on `printf()` / `console.log()` over serial to inspect pin states and debug timing issues. This introduces significant timing distortion (Heisenbugs) and clutters output logs.

---

## 🛡️ The FerrumOS Digital Twin Engine

When FerrumOS Studio connects to a board (over USB-CDC or Wi-Fi WSRPC):

1. **Lightweight Register Telemetry**: The kernel streams packed state words over the wire protocol whenever pin modes, logic levels, or ADC thresholds change.
2. **Interactive Schematic**: Studio renders a live SVG / Canvas pinout diagram of your board (e.g., ESP32-C6 SuperMini or DevKit).
3. **Instant Visual Feedback**:
   - High pins glow in green; Low pins in neutral gray.
   - PWM channels display duty cycle percentages.
   - ADC pins display calibrated millivolt values.
   - I2C & SPI activity flashes indicator LEDs on the virtual board.

---

## 🚀 Key Advantages

- **Zero Logging Overhead**: You don't need to pollute your code with diagnostic print statements.
- **Hardware Diagnostics**: Immediately spot floating pins, missing pull-up resistors, or short circuits visually before running automation logic.
- **Bi-Directional Interaction**: Click pins in the Studio Digital Twin view to toggle test outputs or simulate button presses remotely.
