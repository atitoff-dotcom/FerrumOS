# Web UI Dashboard & REST API Guide

FerrumOS features an embedded, zero-dependency HTTP server (`http_server.rs`):
* **On ESP32-C6 Microcontroller:** Listens on standard **port 80** (`http://<device_ip>/`).
* **On Host PC Simulator:** Listens on **port 8080** (`http://localhost:8080/`).

The server provides both a single-page Glassmorphism Web UI control center and a REST API for automated CI/CD OTA deployment.

---

## 🌐 Web UI Control Center

The built-in web dashboard is accessible from any modern web browser:

### Features:
1. **Real-time Script Monitor:**
   - Displays all registered JS/Rhai scripts.
   - Live status badges (`Running`, `Stopped`, `Failed`).
   - Execution counters and error logs.
   - Interactive **Delete** button.

2. **Live IDE (OTA Deploy):**
   - Script ID input and source code editor.
   - **«🚀 Deploy over OTA»** button.
   - Hot-deploys scripts directly into RAM in <**0.05 seconds** without rebooting the microcontroller core!

---

## 🔌 REST API Reference

### 1. List All Scripts
* **Endpoint:** `GET /api/scripts`
* **Response:** `200 OK`, `application/json`
```json
{
  "scripts": [
    {
      "id": "blink",
      "status": "Running",
      "execution_count": 142
    },
    {
      "id": "thermostat",
      "status": "Running",
      "execution_count": 78
    }
  ]
}
```

### 2. Deploy / Create Script (OTA POST)
* **Endpoint:** `POST /api/scripts`
* **Headers:** `Content-Type: application/json`
* **Request Body:**
```json
{
  "id": "fast_blink",
  "code": "bind_gpio_output(\"StatusLED\", 15);\ndevice.gpio(\"StatusLED\").write(true);\ndelay_ms(50);\ndevice.gpio(\"StatusLED\").write(false);\ndelay_ms(50);"
}
```
* **Response:** `200 OK`
```json
{
  "status": "created",
  "id": "fast_blink"
}
```

### 3. Hot-Swap Script Code (OTA PUT)
* **Endpoint:** `PUT /api/scripts/<id>`
* **Headers:** `Content-Type: application/json`
* **Request Body:**
```json
{
  "code": "console.log('Updated logic!'); delay_ms(1000);"
}
```
* **Response:** `200 OK`
```json
{
  "status": "updated",
  "id": "fast_blink"
}
```

### 4. Delete Script
* **Endpoint:** `DELETE /api/scripts/<id>`
* **Response:** `200 OK`
```json
{
  "status": "deleted",
  "id": "fast_blink"
}
```
* Returns `404 Not Found` if the script ID is invalid.
