# RFC 0017: Интеграция с Home Assistant и протокол MQTT Auto-Discovery

Статус: Implemented  
Версия ядра: 0.6.0+

---

## Реализовано

### 1. Архитектура и принципы
- **Стандарт MQTT Auto-Discovery**: узлы FerrumOS автоматически регистрируют сущности (`switch`, `sensor`, `binary_sensor`) в Home Assistant при первом подключении к брокеру.
- **Двунаправленная синхронизация (State / Command Topics)**:
  - Топик команды (`.../set`): Home Assistant переключает реле.
  - Топик состояния (`.../state`): узел публикует фактический статус (включая локальные переключения физической кнопкой).
- **LWT (Last Will and Testament)**: автоматический статус `online / offline` в Home Assistant при потере связи с узлом.
- **Устойчивость к разрывам**: фоновый реконнект с экспоненциальной задержкой без блокировки локальной автоматики.

---

### 2. Спецификация Fluent JS API и проверенные сниппеты

#### 2.1 Реле Home Assistant (MQTT Switch)
<!-- snippet: id="mqtt_switch" category="MQTT & Cloud" title="Реле Home Assistant (MQTT Switch)" icon="fa-tower-broadcast" desc="MQTT клиент с интеграцией Home Assistant Discovery для управления реле." badges="['MQTT Discovery', 'Switch Entity', 'Auto-Reconnect']" -->
```javascript
const relay = GPIO.output(15).initial(false);

// Подключение к MQTT брокеру и авто-регистрация переключателя
const mqtt = MQTT.client("192.168.1.50", 1883)
    .auth("mqtt_user", "password")
    .discoveryPrefix("homeassistant");

// Регистрация сущности Switch в Home Assistant
const haSwitch = mqtt.registerSwitch("relay_main", "Главное Реле")
    .onCommand((state) => {
        if (state) {
            relay.high();
        } else {
            relay.low();
        }
        haSwitch.publishState(state);
    });
```

#### 2.2 Сенсор Home Assistant (MQTT Sensor)
<!-- snippet: id="mqtt_sensor" category="MQTT & Cloud" title="Сенсор Home Assistant (MQTT Sensor)" icon="fa-chart-line" desc="Публикация телеметрии температуры в Home Assistant по MQTT." badges="['MQTT Discovery', 'Sensor Entity', 'JSON Payload']" -->
```javascript
const mqtt = MQTT.client("192.168.1.50", 1883).discoveryPrefix("homeassistant");

// Регистрация сенсора температуры
const tempSensor = mqtt.registerSensor("room_temp", "Температура комнаты")
    .deviceClass("temperature")
    .unitOfMeasurement("°C");

// Периодическая публикация данных
while (true) {
    const currentTemp = 23.5;
    tempSensor.publishValue(currentTemp);
    delay(10000);
}
```

---

## Планируется

1. **Поддержка сложных сущностей Home Assistant**:
   - `climate` (управление кондиционером и термостатом).
   - `cover` (управление жалюзи и рулонными шторами с позиционированием 0..100%).
   - `light` (RGB/CCT освещение с регулировкой яркости и цветовой температуры).
2. **Локальный шлюз без внешнего брокера**:
   - Прямая интеграция FerrumOS Studio с Home Assistant через WebSocket API.
