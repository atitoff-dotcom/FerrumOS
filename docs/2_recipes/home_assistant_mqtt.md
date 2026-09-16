# How-To: Home Assistant & MQTT Auto-Discovery

`Status: 🟢 Stable (v5.0)` • `Targets: ESP32-C6, ESP32-C3` • `Standard: Home Assistant MQTT Discovery`

FerrumOS integrates seamlessly with **Home Assistant** using the native MQTT Discovery protocol. Nodes automatically publish self-describing configurations so sensors, switches, and climate entities appear in your Home Assistant dashboard without manually writing YAML.

---

## 1. Zero-Configuration MQTT Discovery

When your device connects to the local broker, FerrumOS broadcasts an entity discovery payload to `homeassistant/<component>/<node_id>/<object_id>/config`.

<!-- snippet: id="mqtt_switch" category="MQTT & Cloud" title="Реле Home Assistant (MQTT Switch)" icon="fa-tower-broadcast" desc="MQTT клиент с интеграцией Home Assistant Discovery для управления реле." badges="['MQTT Discovery', 'Switch Entity', 'Auto-Reconnect']" -->
```javascript
// Initialize MQTT connection with auto-reconnect
const mqtt = MQTT.client("mqtt://192.168.1.100:1883")
    .clientId("ferrum-living-room")
    .autoReconnect(true);

// Configure hardware relay
const relay = GPIO.output(15)
    .openDrain(true)
    .pullUp()
    .invert(true)
    .initial(false);

// Register binary switch entity with Home Assistant Discovery
mqtt.discovery("switch", "main_light")
    .name("Living Room Light")
    .stateTopic("ferrum/living/light/state")
    .commandTopic("ferrum/living/light/set")
    .onCommand((payload) => {
        const state = payload === "ON";
        relay.write(state);
        mqtt.publish("ferrum/living/light/state", state ? "ON" : "OFF");
    });
```

---

## 2. Publishing Telemetry Sensors

To register periodic sensor values:

<!-- snippet: id="mqtt_sensor" category="MQTT & Cloud" title="Сенсор Home Assistant (MQTT Sensor)" icon="fa-chart-line" desc="Публикация телеметрии температуры в Home Assistant по MQTT." badges="['MQTT Discovery', 'Sensor Entity', 'JSON Payload']" -->
```javascript
// Register temperature sensor entity
const tempDiscovery = mqtt.discovery("sensor", "temperature")
    .name("Room Temperature")
    .deviceClass("temperature")
    .unitOfMeasurement("°C")
    .stateTopic("ferrum/living/climate")
    .valueTemplate("{{ value_json.temperature }}");

// Periodic telemetry task
while (true) {
    const temp = I2C.bus(0).aht20().readTemperature();
    mqtt.publish("ferrum/living/climate", JSON.stringify({ temperature: temp }));
    delay(5000);
}
```

---

## 3. Verification in Home Assistant

1. Open **Settings -> Devices & Services -> MQTT** in Home Assistant.
2. Your FerrumOS device will appear under **Devices** with its entities (`Living Room Light`, `Room Temperature`).
3. State changes toggled in Lovelace dashboards take effect in less than 5 milliseconds.
