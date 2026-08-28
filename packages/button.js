// FerrumOS Core Helper: Smart Button & Gesture Listener
export class SmartButton {
    constructor(pin, pull = 'up', debounceMs = 50) {
        this.btn = gpio.button(pin, { pull: pull, debounce_ms: debounceMs });
    }
    on(event, callback) {
        while (true) {
            let ev = this.btn.wait();
            if (ev === event) {
                callback();
            }
        }
    }
}
