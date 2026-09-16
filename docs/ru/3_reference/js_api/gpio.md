# Справочник GPIO

Объект `GPIO` предоставляет доступ к пинам ввода/вывода микроконтроллера.

---

## Цифровой выход: `GPIO.output(pin)`

Настраивает пин на вывод. Возвращает объект управления выходом.

### Методы цепочки конфигурации
- `.openDrain(enabled: boolean)` — Включает или выключает режим открытого стока (по умолчанию: `false` = push-pull).
- `.pullUp()` — Включает внутреннюю подтяжку к питанию (pull-up).
- `.pullDown()` — Включает внутреннюю подтяжку к земле (pull-down).
- `.invert(enabled: boolean)` — Инвертирует логический уровень (`true` = активный ноль).
- `.initial(level: boolean)` — Атомарно задает начальный уровень при инициализации.

### Методы управления
- `handle.write(level: boolean): void` — Устанавливает состояние HIGH (`true`) или LOW (`false`).
- `handle.read(): boolean` — Считывает текущее состояние выхода.

### Пример
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

## Цифровой вход: `GPIO.input(pin)`

Настраивает пин на ввод. Возвращает объект управления входом.

### Методы цепочки конфигурации
- `.pullUp()` — Включает подтяжку к питанию.
- `.pullDown()` — Включает подтяжку к земле.
- `.invert(enabled: boolean)` — Инвертирует логический уровень.
- `.debounce(ms: number)` — Задает окно аппаратного антидребезга в миллисекундах.
- `.delayedOn(ms: number)` — Задержка включения: уровень должен удерживаться `ms` для фиксации HIGH.
- `.delayedOff(ms: number)` — Задержка выключения: уровень должен удерживаться `ms` для фиксации LOW.
- `.autoOff(ms: number)` — Автосброс сигнала через `ms` миллисекунд после срабатывания.

### Методы управления
- `handle.read(): boolean` — Возвращает текущий отфильтрованный уровень.
- `handle.wait(): boolean` — Приостанавливает задачу до следующего изменения состояния.

### Пример
<!-- snippet: id="gpio_input" category="Кнопки / Входы" title="Вход с фильтром (Debounce)" icon="fa-shield" desc="Цифровой вход с аппаратным антидребезгом и задержкой." badges="['Debounce: 50ms', 'Pull-up', 'Zero-CPU']" -->
```javascript
const reedSwitch = GPIO.input(4)
    .pullUp()
    .debounce(50)
    .delayedOn(20);

while (true) {
    reedSwitch.wait();
    console.log(`Статус двери: ${reedSwitch.read() ? "ОТКРЫТА" : "ЗАКРЫТА"}`);
}
```

---

## Умная кнопка и жесты: `handle.button()`

Превращает цифровой вход в аппаратный детектор жестов.

### Методы цепочки настройки жестов
- `.clickMs(ms: number)` — Максимальная длительность клика (по умолчанию: `350`).
- `.doubleClickMs(ms: number)` — Окно ожидания второго клика (по умолчанию: `250`).
- `.longPressMs(ms: number)` — Порог длительного удержания (по умолчанию: `800`).

### Константы жестов
- `Button.CLICK` (`1`)
- `Button.DOUBLE_CLICK` (`2`)
- `Button.LONG_PRESS` (`3`)
- `Button.RELEASE` (`4`)

### Пример
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
        console.log("Обнаружен клик");
    }
}
```
