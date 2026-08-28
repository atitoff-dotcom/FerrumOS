# FerrumOS Fleet Script & Pin Manager Guide (`tools/fleet_manager.py`)

The **FerrumOS Fleet Manager** is a centralized Python orchestration tool designed for managing, validating, and deploying Rhai/JS scripts across multiple FerrumOS IoT nodes.

---

## 🏗️ Core Responsibilities

1. **Centralized Device Inventory (`tools/fleet.json`):**
   Maintains a global registry of all ESP32-C6 nodes across the smart home environment (IP addresses, HTTP ports, descriptions).

2. **Pre-flight Hardware Pin Conflict Validation:**
   Scans Rhai/JS script code *before* network transmission to ensure that hardware pins (GPIO, I2C SDA/SCL) are not claimed by competing scripts on the same node.

3. **Automatic Driver Dependency Resolution (`import "drivers/..."`):**
   Parses `import "drivers/<name>"` in user scripts. If a script references a driver file in `drivers/` (e.g. `drivers/mhz19b.rhai`), the Fleet Manager automatically uploads the required driver to the node before deploying the user script.

4. **Instant OTA Script Deployment:**
   Sends verified scripts to nodes via HTTP REST API (`POST /api/scripts`) in <0.1 seconds.

5. **Fleet Health Monitoring:**
   Aggregates execution statuses (`LOADED`, `RUNNING`, `FAILED`) and execution counts across all registered nodes.


---

## 📋 Device Inventory Configuration (`tools/fleet.json`)

```json
{
  "nodes": {
    "living_room_gateway": {
      "ip": "192.168.1.50",
      "port": 8080,
      "description": "ESP32-C6 Living Room Main Controller"
    },
    "kitchen_controller": {
      "ip": "192.168.1.51",
      "port": 8080,
      "description": "ESP32-C6 Kitchen Climate & Lighting Node"
    }
  }
}
```

---

## 💻 CLI Usage Guide

### 1. Check Fleet Health Status
Checks connectivity and script statuses across all nodes:

```bash
python tools/fleet_manager.py status
```

### 2. Validate Script Pin Assignments (Pre-flight Check)
Validates dynamic pin bindings without deploying:

```bash
python tools/fleet_manager.py validate path/to/script.rhai
```

### 3. Deploy Script OTA to Specific Node
Performs pre-flight validation and deploys the script to the specified node:

```bash
python tools/fleet_manager.py deploy living_room_gateway climate_ctrl path/to/script.rhai
```
