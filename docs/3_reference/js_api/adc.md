# ADC Reference

The `ADC` module reads analog voltage from dedicated ADC pins using hardware oversampling and eFuse calibration.

---

## Initializing an ADC Pin: `ADC.pin(pin)`

Configures an analog-to-digital converter pin. Returns an ADC input handle.

### Example
<!-- snippet: id="adc_pin" category="Аналоговые датчики (АЦП)" title="Измерение напряжения (АЦП)" icon="fa-chart-line" desc="Считывание физического напряжения в милливольтах с калибровкой чипа." badges="['Диапазон: 0..3.3В', 'eFuse калибровка', 'Multisampling: 16']" -->
```javascript
// Configure ADC on GPIO 2
const adc = ADC.pin(2)
    .attenuation("11db") // Measurement range up to ~3.3V (input attenuator)
    .samples(16);        // Multisampling 16 readings for noise filtering

// Read calibrated voltage in millivolts
const millivolts = adc.readMilliVolts();
```

---

## Chained Configuration Methods

### .attenuation(level: string)
Sets the input attenuation (voltage divider) to match the expected signal level.

| Value | Input Voltage Range | Description |
| :--- | :--- | :--- |
| `"0db"` | 0 .. 1100 mV | Maximum sensitivity for weak signals (no divider) |
| `"2.5db"` | 0 .. 1500 mV | Intermediate voltage range |
| `"6db"` | 0 .. 2200 mV | Logic-level signals (1.8V - 2.0V) |
| `"11db"` | 0 .. 3300 mV | Default. Full 3.3V power supply rail range |

### .samples(count: number)
Number of consecutive hardware ADC measurements taken and averaged (multisampling / oversampling).
- **Valid range**: `1` (single conversion, fastest) to `64`.
- **Default / Recommended**: `16` or `32` effectively filters out high-frequency noise from RF radios (Wi-Fi/Thread).

---

## Measurement Methods

### handle.readMilliVolts(): number
Returns the measured voltage in millivolts (`mV`).
- Automatically applies factory polynomial calibration curves from eFuse memory to compensate for hardware ADC non-linearity.

### handle.readRaw(): number
Returns the raw uncalibrated 12-bit ADC reading (`0` .. `4095`).
