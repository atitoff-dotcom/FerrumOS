# Справочник Power и сна

Модуль `Power` управляет профилями энергосбережения, таймером RTC и замером напряжения батареи.

---

## Настройка глубокого сна: `Power.sleep()`

<!-- snippet: id="power_sleep" category="Питание и сон" title="Глубокий сон (Deep Sleep)" icon="fa-moon" desc="Перевод ядра в PDS-сон с пробуждением по таймеру или пину." badges="['PDS Sleep', 'RTC Timer', 'Wake Pin']" -->
```javascript
Power.sleep()
    .after(60).seconds()
    .wakeOnPin(4).falling()
    .enter();
```

### Методы цепочки настройки
- `.after(n: number).seconds()` — Задает интервал сна RTC в секундах.
- `.after(n: number).minutes()` — Задает интервал сна RTC в минутах.
- `.wakeOnPin(pin: number)` — Задает пин RTC в качестве внешнего источника пробуждения.
- `.rising()` — Пробуждение по нарастающему фронту (LOW -> HIGH).
- `.falling()` — Пробуждение по спадающему фронту (HIGH -> LOW).
- `.enter()` — Обесточивает периферию и переводит чип в глубокий сон PDS.

---

## Замер заряда батареи: `Power.batteryVoltage()`

Возвращает текущее напряжение питания в Вольтах со встроенного калиброванного АЦП-делителя:

<!-- snippet: id="power_vbat" category="Питание и сон" title="Телеметрия батарейки (VBat)" icon="fa-battery-half" desc="Измерение напряжения аккумулятора через калиброванный встроенный делитель." badges="['VBat', 'Calibrated ADC']" -->
```javascript
const vbat = Power.batteryVoltage();
console.log(`Напряжение АКБ: ${vbat.toFixed(2)} В`);
```
