# Tutorial 3: Smart Button Gestures

`Status: 🟢 Stable (v5.0)` • `Targets: ESP32-C6, ESP32-C3` • `Kernel: Hardware ButtonDetector`

Standard microcontrollers require complex timers and state machines to distinguish button clicks, double clicks, and holds. In FerrumOS, gesture detection is implemented directly inside the Rust kernel (`ButtonDetector`), requiring zero CPU overhead from your script.

---

## Hardware Setup

Connect a momentary tactile button between **GPIO 9** (default user button on many ESP32 boards) and **GND**.

---

## Configuring the Smart Button

Create a script called `smart_button.js`:

<!-- snippet: id="btn_smart_gestures" category="Кнопки / Входы" title="Умная кнопка (Click, Double, Hold)" icon="fa-hand-pointer" desc="Аппаратный детектор жестов: одиночный клик, двойной клик, длинное удержание." badges="['Smart Button', '4 события', 'Zero-CPU wait']" -->
```javascript
// Configure status LED
const led = GPIO.output(8)
    .pullUp()
    .invert(true)
    .initial(false);

// Configure hardware button detector on GPIO 9
const btn = GPIO.input(9)
    .pullUp()
    .button()
    .clickMs(350)
    .doubleClickMs(250)
    .longPressMs(800);

System.log("Smart button listening for gestures...");

while (true) {
    // Wait for the next gesture event from the kernel
    const event = btn.wait();

    if (event === Button.CLICK) {
        System.log("Event: Single Click -> Toggle LED");
        led.write(!led.read());
    } else if (event === Button.DOUBLE_CLICK) {
        System.log("Event: Double Click -> Fast Flash");
        for (let i = 0; i < 3; i++) {
            led.write(true);
            delay(100);
            led.write(false);
            delay(100);
        }
    } else if (event === Button.LONG_PRESS) {
        System.log("Event: Long Press / Hold -> Reset State");
        led.write(false);
    }
}
```

---

## Gesture Events Overview

| Event Constant | Description | Default Timing |
|---|---|---|
| `Button.CLICK` | Single momentary press and release | `clickMs(350)` |
| `Button.DOUBLE_CLICK` | Two successive clicks within the timeout window | `doubleClickMs(250)` |
| `Button.LONG_PRESS` | Button held down longer than threshold | `longPressMs(800)` |
| `Button.RELEASE` | Button released after a long press | Immediate |

---

## Why Hardware Gesture Detection Matters

In conventional embedded scripts, debouncing is done in software loops that burn battery and miss events during blocking I/O. FerrumOS executes the button state machine inside timer interrupts at the hardware level, waking the script engine **only when a verified gesture occurs**.

Next, explore our [How-To Guides](../2_recipes/battery_deep_sleep.md) for battery optimization and wireless networking.
