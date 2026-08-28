# Scripting API Reference (Rhai & JS Style)

**FerrumOS** provides a **JavaScript-compatible scripting layer** built on top of the Rhai embedded engine running in a bare-metal `no_std` microcontroller environment.

---

## ⚡ Execution Model: Zero-Cost Coroutines (State Machine)

FerrumOS uses a **non-blocking cooperative state machine** model instead of heavy OS threads (e.g. FreeRTOS):

* **Intuitive Linear JS DX:** Write straightforward, synchronous-style code (`delay_ms(500);`, `let line = device.uart("GPS").read_line(1000);`) without callback hell or async/await state allocations.
* **Instant Yield to Kernel:** When calling `delay_ms()` or waiting for queues/buses, the script yields execution back to the kernel event loop.
* **Full CPU Efficiency:** The Wi-Fi network stack, HTTP REST server, and concurrent scripts run at full line rate without blocking.

```javascript
// Clean linear loop — never blocks the kernel or Wi-Fi stack!
loop {
    device.gpio("StatusLED").write(true);
    delay_ms(200); // Microsecond yield to kernel
    device.gpio("StatusLED").write(false);
    delay_ms(800);
}
```

---

## 🖥️ Console & System Logging

### `console.log(message)`
Logs an informational message to the UART serial output (115200 baud) and Web Control Center console.

```javascript
console.log("System initialized successfully");
console.log("Temperature value: " + temp + " °C");
```

### `console.error(message)`
Logs an error message to the system log output with elevated priority.

```javascript
console.error("Sensor communication failed on I2C bus!");
```

---

## 🧮 Math Object (`Math`)

Standard mathematical utilities operating on integer and floating-point values:

- `Math.round(x)` — Rounds to the nearest integer.
- `Math.floor(x)` — Rounds down.
- `Math.ceil(x)` — Rounds up.
- `Math.abs(x)` — Returns absolute value.
- `Math.max(a, b)` — Returns maximum of two numbers.
- `Math.min(a, b)` — Returns minimum of two numbers.
- `Math.pow(base, exp)` — Exponential power base^exp.
- `Math.sqrt(x)` — Square root.

```javascript
let temp = 24.8;
let rounded = Math.round(temp); // 25
let peak = Math.max(rounded, 30); // 30
```

---

## 📦 JSON Serialization (`JSON`)

### `JSON.stringify(object)`
Serializes an object, map, or array into a standard JSON string.

```javascript
let telemetry = #{
    device_id: "ESP32C6_01",
    temperature: 24.5,
    humidity: 60,
    relay: true
};
let json_str = JSON.stringify(telemetry);
mqtt.publish("ferrumos/telemetry", json_str);
```

### `JSON.parse(string)`
Parses a JSON string into a structured data map.

```javascript
let cmd = JSON.parse(incoming_json);
if cmd.action == "POWER_ON" {
    device.gpio("Relay1").write(true);
}
```

---

## 🗄️ Inter-Script Communication & Shared State (`state`)

FerrumOS provides a thread-safe, non-blocking **Shared Blackboard Key-Value Store** for inter-script communication (IPC) between isolated script instances.

### `state.set(key, value)`
Atomically stores a value (number, string, boolean, map, or array) into global kernel state.

```javascript
// Producer script (e.g. sensor_reader.js)
state.set("climate.temperature", 24.8);
state.set("climate.humidity", 58);
state.set("system.status", #{ online: true, battery: 95 });
```

### `state.get(key)`
Atomically reads a value from global state. Returns `()` (`null`) if the key does not exist.

```javascript
// Consumer script (e.g. display.js or thermostat.js)
let temp = state.get("climate.temperature");
if temp != () {
    console.log("Current Temperature: " + temp + " °C");
    if temp > 28.0 {
        device.gpio("FanRelay").write(true);
    }
}
```

### `state.has(key)` / `state.delete(key)`
```javascript
if state.has("alert.active") {
    console.log("Active alert cleared");
    state.delete("alert.active");
}
```

---

## 📬 Message Queues (`queue`) & Event Bus (`events`)

### 1. FIFO Message Queues (`queue`)
Enables non-blocking message passing between microservices running on the MCU with bounded ring buffer memory protection:

```javascript
// Push structured telemetry to a channel
queue.send("telemetry", #{
    sensor: "BME280",
    temp: 24.8,
    humidity: 62.0
});

// Non-blocking pop with timeout (yields CPU without blocking Wi-Fi or other scripts)
let msg = queue.receive("telemetry", 1000);
if msg != () {
    console.log("Received temperature: " + msg.temp);
}
```

### 2. Pub/Sub Event Bus (`events`)
Enables broadcast of discrete events across scripts:

```javascript
// Emit an event
events.emit("security/alarm", #{ zone: "warehouse", level: 3 });

// Subscribe to an event
events.on("security/alarm", |data| {
    console.log("Alarm triggered in zone: " + data.zone);
    device.gpio("SirenPin").write(true);
});
```

---

---

## 🔌 Hardware & Peripheral API (`gpio` & `device`)

### Pin Mode Configuration & GPIO Control (`gpio`)
FerrumOS provides zero-overhead hardware pin configuration (Push-Pull / Open-Drain, Pull-Up / Pull-Down, Initial level). All configuration properties compile into a **single 1-byte bitmask**:

```javascript
// 1. Full Object-Based Configuration:
gpio.mode(15, {
    direction: "output",      // "output" | "input"
    type: "push_pull",        // "push_pull" | "open_drain"
    pull: "none",             // "none" | "up" | "down"
    initial: 0                // 0 (Low / 0V) | 1 (High / 3.3V)
});

// 2. Fast Shortcuts:
gpio.output(15);                                     // Standard Push-Pull Output
gpio.output(8, { type: "open_drain", pull: "up" });  // Open-Drain with internal Pull-Up
gpio.input(9, { pull: "up" });                       // Input with internal Pull-Up

// 3. Fast Level Control:
gpio.write(15, 1);
gpio.high(15);
gpio.low(15);
```

### Named Pin Control (`device.gpio`)
```javascript
// Write pin state (true = High 3.3V, false = Low 0V)
device.gpio("Relay1").write(true);
device.gpio("Relay1").write(false);

// Read pin state
let is_high = device.gpio("Button1").read();
```

### PWM & Servos (LEDC)
```javascript
// Set LED brightness duty cycle (0..255)
device.pwm("DimmerLED").set_duty(128);

// Set servo angle (0..180 degrees)
device.pwm("CameraPan").set_angle(90);
```

### 1-Wire Temperature Sensors (Dallas DS18B20)
```javascript
// Read calibrated temperature with 0.0625 °C precision
let temp = device.ds18b20("TempProbe").read();
console.log("Probe Temperature: " + temp + " °C");
```

### I2C Bus Operations
```javascript
// Read bytes from I2C bus: read(i2c_addr, reg_addr, byte_count)
let bytes = device.i2c("I2C0").read(0x76, 0xD0, 2);

// Write bytes to I2C bus: write(i2c_addr, reg_addr, data_array)
device.i2c("I2C0").write(0x68, 0x10, [0x20, 0x80]);
```

### SPI Bus Operations
```javascript
// SPI Full-Duplex Transfer
let rx_data = device.spi("SPI0").transfer([0x01, 0x02, 0x03]);
```

### UART Serial Operations
```javascript
// Send data
device.uart("GPS").write("$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29\r\n");

// Non-blocking read line with timeout (ms)
let nmea = device.uart("GPS").read_line(1000);
if nmea != () {
    console.log("NMEA: " + nmea);
}
```

---

## 🛠️ Dynamic Hardware Pin & Bus Self-Binding

Scripts can dynamically declare and bind required hardware pins at runtime:

```javascript
// Dynamically bind GPIO pins
bind_gpio_output("StatusLED", 15);
bind_gpio_input("UserButton", 9);

// Dynamically bind PWM (LEDC): alias, pin, frequency Hz
bind_pwm("DimmerLED", 4, 5000);

// Dynamically bind 1-Wire bus
bind_onewire_bus("TempProbe", 8);

// Dynamically bind I2C bus (SDA=6, SCL=7)
bind_i2c_bus("I2C0", 6, 7);

// Dynamically bind UART (TX=16, RX=17, Baud=9600)
bind_uart("GPS", 16, 17, 9600);
```

---

## 🏭 Industrial Modbus RTU / TCP Protocol (`modbus`)

```javascript
// Read Holding Registers: read_holding(port_or_host, unit_id, start_reg, count)
let regs = modbus.read_holding("UART_RS485", 1, 0x0000, 4);
let voltage = regs[0] / 10.0;
let current = regs[1] / 100.0;
let active_power = regs[2];

// Write Single Register: write_single(port_or_host, unit_id, reg, val)
modbus.write_single("UART_RS485", 1, 0x0010, 1);
```

---

## 🏛️ Matter Protocol API (`matter`)

FerrumOS provides native bindings to the Matter Data Model. Endpoint IDs are automatically allocated by the kernel upon creation:

```javascript
// 1. Create Matter Endpoints
let light = matter.endpoint(matter.types.ON_OFF_LIGHT);
let temp_sensor = matter.endpoint(matter.types.TEMPERATURE_SENSOR);

// 2. React to incoming Matter commands (from Home Assistant / Apple Home)
light.on_command("OnOff", |command| {
    if command == "On" {
        device.gpio("StatusLED").write(true);
        light.set("OnOff", true);
    } else {
        device.gpio("StatusLED").write(false);
        light.set("OnOff", false);
    }
});

// 3. Update Matter Attributes (e.g. Temperature in 100ths of °C)
temp_sensor.set("MeasuredValue", 2350);
```

---

## 📡 MQTT Telemetry API (`mqtt`)

```javascript
// Publish to MQTT topic
let payload = JSON.stringify(#{
    device: "ESP32C6",
    status: "HEALTHY",
    uptime_ms: 120000
});
mqtt.publish("ferrumos/telemetry", payload);
```

---

## 🛡️ Error Handling with `try { ... } catch (err) { ... }`

Scripts can catch exceptions locally to prevent supervisor script failure:

```javascript
try {
    let data = device.i2c("I2C0").read(0x76, 0x00, 2);
    console.log("Sensor data: " + data);
} catch (err) {
    console.error("Hardware read failed: " + err);
    device.gpio("FaultLED").write(true);
}
```
