# PWM & Addressable LEDs Reference
Controls hardware PWM channels and addressable WS2812 RGB strips.

## Addressable RGB: `WS2812.pin(pin)`

<!-- snippet: id="ws2812_rgb" category="RGB WS2812" title="Статичный цвет WS2812" icon="fa-palette" desc="Прямая установка цвета RGB на адресном светодиоде." badges="['WS2812B', 'RGB 0-255', 'Pin 8']" -->
```javascript
const ledStrip = WS2812.pin(8)
    .length(1);

ledStrip.set(0, 0, 255, 0); // Green
ledStrip.show();
```

### Rainbow Animation

<!-- snippet: id="ws2812_rainbow" category="RGB WS2812" title="Плавная радуга WS2812" icon="fa-rainbow" desc="Циклический перебор цветов на светодиоде в бесконечном цикле." badges="['Анимация', 'Спектр', 'WS2812B']" -->
```javascript
const ledStrip = WS2812.pin(8)
    .length(1);

while (true) {
    ledStrip.set(0, 255, 0, 0); ledStrip.show(); delay(300);
    ledStrip.set(0, 0, 255, 0); ledStrip.show(); delay(300);
    ledStrip.set(0, 0, 0, 255); ledStrip.show(); delay(300);
}
```
