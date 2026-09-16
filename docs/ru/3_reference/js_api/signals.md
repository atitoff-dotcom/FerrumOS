# Справочник сигналов и IPC (state.signal)

`state.signal(topic, initialValue)` реализует неблокирующее межскриптовое взаимодействие (IPC) с нулевым копированием памяти между задачами, аппаратными датчиками, сетью CAN и Home Assistant.

<!-- snippet: id="signal_declare" category="Циклы и задержки" title="Реактивный сигнал (IPC)" icon="fa-bolt" desc="Создание общего реактивного сигнала для межскриптового взаимодействия." badges="['IPC', 'Zero-Copy']" -->
```javascript
// Объявление разделяемого реактивного сигнала
const temp = state.signal("climate/temp", 20);

// Атомарное обновление значения (генерирует OP_SIGNAL_SET)
temp = 24.5;
```

---

## 📐 Цепочки конфигурации сигнала

```javascript
// Привязка сигнала к Home Assistant и шине CAN
const alarm = state.signal("security/alarm", false)
    .exposeHA("binary_sensor", { name: "Охранная тревога" })
    .can(42)
    .urgent();
```

---

## ⚙️ Реактивный подписчик (`.watch()`)

Метод `.watch()` переводит задачу в режим аппаратного ожидания до изменения версии сигнала. Выполнение уступает процессор через опкод `OP_SIGNAL_WAIT` с нулевой нагрузкой на CPU во время паузы.

<!-- snippet: id="signal_watch" category="Циклы и задержки" title="Подписчик сигнала (.watch)" icon="fa-eye" desc="Асинхронная подписка на изменение сигнала без нагрузки на CPU." badges="['Reactive', 'Sleep']" -->
```javascript
const waterTemp = state.signal("boiler/temp", 40);
const heater = GPIO.output(14).initial(false);

waterTemp.watch((val) => {
    // Просыпается только при реальном изменении температуры
    heater.write(val < 50);
});
```

---

## 📋 Спецификация API

### `state.signal(topic: string, initialValue?: number | boolean): Signal`
Регистрирует или находит слот сигнала в ядре по 16-битному хэшу FNV-1a.
- `topic`: Иерархический путь канала (например, `"living/temp"`, `"relay/state"`).
- `initialValue`: Опциональное начальное значение (число или булево).

### `.watch(callback: (value: any) => void): void`
Регистрирует реактивного слушателя. Цикл задачи уступает процессор до публикации новой версии значения.

### `.exposeHA(component: string, options: object): Signal`
Публикует метаданные авто-обнаружения MQTT для Home Assistant:
- `component`: `"sensor"`, `"binary_sensor"`, `"switch"` или `"number"`.
- `options`: Параметры сущности (`name`, `unit`, `icon`, `device_class`).

### `.can(canId?: number): Signal`
Привязывает сигнал к аппаратной шине CAN / TWAI для распределенного вещания по сети:
- `canId`: Опциональный 11-битный идентификатор кадра CAN. Если не указан, формируется автоматически из хэша топика.

### `.urgent(): Signal`
Устанавливает флаг повышенного приоритета в арбитраже шины CAN для мгновенной доставки пакета.
