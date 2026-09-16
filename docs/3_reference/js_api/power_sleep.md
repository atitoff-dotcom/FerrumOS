# Power & Sleep Reference

The `Power` module manages sleep profiles, RTC timers, and battery voltage telemetry.

---

## Deep Sleep Configuration: `Power.sleep()`

<!-- snippet: id="power_sleep" category="Питание и сон" title="Глубокий сон (Deep Sleep)" icon="fa-moon" desc="Перевод ядра в PDS-сон с пробуждением по таймеру или пину." badges="['PDS Sleep', 'RTC Timer', 'Wake Pin']" -->
```javascript
Power.sleep()
    .after(60).seconds()
    .wakeOnPin(4).falling()
    .enter();
```

### Chained Configuration Methods
- `.after(n: number).seconds()` — Sets RTC wake-up timer in seconds.
- `.after(n: number).minutes()` — Sets RTC wake-up timer in minutes.
- `.wakeOnPin(pin: number)` — Selects RTC GPIO pin as an external wake-up trigger.
- `.rising()` — Triggers wakeup on LOW-to-HIGH edge transition.
- `.falling()` — Triggers wakeup on HIGH-to-LOW edge transition.
- `.enter()` — Commits power domain shutdown and places core into PDS sleep.

---

## Battery Telemetry: `Power.batteryVoltage()`

Returns the measured battery voltage in volts directly from the internal calibrated ADC divider:

<!-- snippet: id="power_vbat" category="Питание и сон" title="Телеметрия батарейки (VBat)" icon="fa-battery-half" desc="Измерение напряжения аккумулятора через калиброванный встроенный делитель." badges="['VBat', 'Calibrated ADC']" -->
```javascript
const vbat = Power.batteryVoltage();
console.log(`Battery: ${vbat.toFixed(2)} V`);
```
