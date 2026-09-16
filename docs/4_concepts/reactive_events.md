# Reactive Events vs Busy Waits

FerrumOS is designed from the ground up around a **pure reactive event model**. 

In battery-powered IoT devices and real-time edge nodes, blocking delays (`delay(1000)` or busy loops) waste energy and ruin concurrency. FerrumOS replaces busy waiting with hardware event listeners and interrupt-driven sleep.

---

## ⚡ The Flaw of Blocking Delays

Consider traditional Arduino / MicroPython code:

```javascript
// ❌ Traditional blocking approach:
while (true) {
    if (readPin(9) == LOW) {
        togglePin(15);
    }
    delay(100); // CPU remains fully powered and wastes millions of clock cycles!
}
```

### Why this is inefficient:
1. **Battery Drain**: While executing `delay()`, the CPU runs at full frequency (160 MHz on ESP32-C6), drawing 25–40 mA continuously.
2. **Missed Pulses**: While sleeping inside `delay()`, fast input transitions or network packets can be delayed or dropped.
3. **Complex Debounce Logic**: Developers write fragile software timers to filter contact chatter.

---

## 🛡️ The FerrumOS Reactive Event Model

In FerrumOS, input processing is delegated directly to hardware timers and interrupt queues:

```javascript
// ✅ FerrumOS Reactive Model
const btn = GPIO.input(9)
    .pullUp()
    .button()
    .clickMs(350);

const relay = GPIO.output(15)
    .openDrain(false)
    .initial(false);

while (true) {
    // Wakes up ONLY when a physical gesture is recognized by hardware
    const gesture = btn.wait();

    if (gesture === Button.CLICK) {
        relay.write(!relay.read());
    }
}
```

### How the Micro-Kernel Manages Execution:
1. **Hardware Sleep**: During `btn.wait()`, the task yields execution immediately. The RISC-V CPU enters low-power sleep (`WFI` — Wait For Interrupt).
2. **Zero Idle Overhead**: CPU consumption drops to microamps.
3. **Sub-Microsecond Wakeup**: The instant a pin edge or hardware timer triggers, the kernel wakes up the task without latency.
