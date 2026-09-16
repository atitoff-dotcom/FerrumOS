# GPIO Reference

The `GPIO` object provides access to general-purpose input/output pins on the microcontroller.

---

## Digital Output: `GPIO.output(pin)`

Configures a pin as a digital output. Returns an output handle.

### Chained Configuration Methods
- `.openDrain(enabled: boolean)` — Enables or disables open-drain mode (default: `false` = push-pull).
- `.pullUp()` — Enables internal weak pull-up resistor.
- `.pullDown()` — Enables internal weak pull-down resistor.
- `.invert(enabled: boolean)` — Inverts logic level (`true` means active-low).
- `.initial(level: boolean)` — Sets the output state atomically during initialization.

### Control Methods
- `handle.write(level: boolean): void` — Drives the output HIGH (`true`) or LOW (`false`).
- `handle.read(): boolean` — Reads back the current output level.

### Example
<!-- snippet: id="gpio_output" category="Выходы / Реле" title="Реле / Цифровой выход" icon="fa-lightbulb" desc="Атомарная инициализация и управление дискретным выходом (реле, светодиод)." badges="['Digital Out', 'Push-Pull / Open-Drain']" -->
```javascript
const buzzer = GPIO.output(14)
    .openDrain(false)
    .pullUp()
    .invert(false)
    .initial(false);

buzzer.write(true);
delay(100);
buzzer.write(false);
```

---

## Digital Input: `GPIO.input(pin)`

Configures a pin as a digital input. Returns an input handle.

### Chained Configuration Methods
- `.pullUp()` — Enables internal pull-up resistor.
- `.pullDown()` — Enables internal pull-down resistor.
- `.invert(enabled: boolean)` — Inverts read logic level.
- `.debounce(ms: number)` — Sets hardware glitch filter window in milliseconds.
- `.delayedOn(ms: number)` — Signal must remain active for `ms` before reporting HIGH.
- `.delayedOff(ms: number)` — Signal must remain inactive for `ms` before reporting LOW.
- `.autoOff(ms: number)` — Automatically clears active state after `ms` duration.

### Control Methods
- `handle.read(): boolean` — Reads instantaneous filtered level.
- `handle.wait(): boolean` — Blocks task until next state change.

### Example
<!-- snippet: id="gpio_input" category="Кнопки / Входы" title="Вход с фильтром (Debounce)" icon="fa-shield" desc="Цифровой вход с аппаратным антидребезгом и задержкой." badges="['Debounce: 50ms', 'Pull-up', 'Zero-CPU']" -->
```javascript
const reedSwitch = GPIO.input(4)
    .pullUp()
    .debounce(50)
    .delayedOn(20);

while (true) {
    reedSwitch.wait();
    console.log(`Door state: ${reedSwitch.read() ? "OPEN" : "CLOSED"}`);
}
```

---

## Smart Button Gestures: `handle.button()`

Converts a digital input into a smart button detector with gesture recognition.

### Chained Gesture Methods
- `.clickMs(ms: number)` — Maximum duration for a single click (default: `350`).
- `.doubleClickMs(ms: number)` — Maximum gap between two clicks for double click (default: `250`).
- `.longPressMs(ms: number)` — Minimum duration to register a long press/hold (default: `800`).

### Gesture Constants
- `Button.CLICK` (`1`)
- `Button.DOUBLE_CLICK` (`2`)
- `Button.LONG_PRESS` (`3`)
- `Button.RELEASE` (`4`)

### Example
<!-- snippet: id="gpio_button" category="Кнопки / Входы" title="Умная кнопка (Click / Hold)" icon="fa-hand-pointer" desc="Аппаратное распознавание жестов кнопки с нулевой нагрузкой на CPU." badges="['Жесты: Click/Hold', 'Zero-CPU wait']" -->
```javascript
const btn = GPIO.input(9)
    .pullUp()
    .button()
    .clickMs(300)
    .doubleClickMs(200)
    .longPressMs(700);

while (true) {
    const gesture = btn.wait();
    if (gesture === Button.CLICK) {
        console.log("Click detected");
    }
}
```
