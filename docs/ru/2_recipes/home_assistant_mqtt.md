# Рецепт: Интеграция с Home Assistant по MQTT

`Статус: 🟢 В релизе (v5.0)` • `Чипы: ESP32-C6, ESP32-C3` • `Стандарт: Home Assistant MQTT Discovery`

FerrumOS поддерживает стандартный протокол **Home Assistant MQTT Discovery**. Устройства автоматически передают информацию о своих сущностях (сенсорах, реле, климате) на брокер, и они появляются в панелях Home Assistant без ручного редактирования файлов `configuration.yaml`.

---

## 1. Авто-дискавери сущностей

При подключении к брокеру FerrumOS отправляет конфигурационный пакет в топик `homeassistant/<компонент>/<node_id>/<object_id>/config`.

<!-- snippet: id="mqtt_switch" category="MQTT & Cloud" title="Реле Home Assistant (MQTT Switch)" icon="fa-tower-broadcast" desc="MQTT клиент с интеграцией Home Assistant Discovery для управления реле." badges="['MQTT Discovery', 'Switch Entity', 'Auto-Reconnect']" -->
```javascript
// Инициализация MQTT-клиента
const mqtt = MQTT.client("mqtt://192.168.1.100:1883")
    .clientId("ferrum-living-room")
    .autoReconnect(true);

// Атомарная настройка реле через Fluent Chaining
const relay = GPIO.output(15)
    .openDrain(true)
    .pullUp()
    .invert(true)
    .initial(false);

// Регистрация выключателя в Home Assistant Discovery
mqtt.discovery("switch", "main_light")
    .name("Свет в гостиной")
    .stateTopic("ferrum/living/light/state")
    .commandTopic("ferrum/living/light/set")
    .onCommand((payload) => {
        const state = payload === "ON";
        relay.write(state);
        mqtt.publish("ferrum/living/light/state", state ? "ON" : "OFF");
    });
```

---

## 2. Отправка показаний датчиков

Для автоматической регистрации климатического сенсора:

<!-- snippet: id="mqtt_sensor" category="MQTT & Cloud" title="Сенсор Home Assistant (MQTT Sensor)" icon="fa-chart-line" desc="Публикация телеметрии температуры в Home Assistant по MQTT." badges="['MQTT Discovery', 'Sensor Entity', 'JSON Payload']" -->
```javascript
// Регистрация сенсора температуры
mqtt.discovery("sensor", "temperature")
    .name("Температура в комнате")
    .deviceClass("temperature")
    .unitOfMeasurement("°C")
    .stateTopic("ferrum/living/climate")
    .valueTemplate("{{ value_json.temperature }}");

// Периодическая отправка данных
while (true) {
    const temp = I2C.bus(0).aht20().readTemperature();
    mqtt.publish("ferrum/living/climate", JSON.stringify({ temperature: temp }));
    delay(5000);
}
```

---

## 3. Проверка в Home Assistant

1. Перейдите в **Настройки -> Устройства и службы -> MQTT**.
2. Устройство FerrumOS автоматически отобразится в списке с привязанными сущностями (`Свет в гостиной`, `Температура в комнате`).
3. Время реакции на команды управления через веб-интерфейс составляет менее 5 миллисекунд.
