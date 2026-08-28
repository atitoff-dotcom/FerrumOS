# 🐍 FerrumOS Python Toolchain & Home Assistant Guide

This document specifies the architecture and implementation of the **FerrumOS Python Toolchain Suite**, including:
1. **Pre-Flight Hardware & Driver Validator**
2. **Native RWP Binary Client (`struct.pack` / `struct.unpack`)**
3. **Fleet Manager & Inventory**
4. **Home Assistant MQTT Discovery Bridge**

---

## 🎯 Package Architecture (`tools/ferrum/`)

```text
tools/ferrum/
├── __init__.py          # Module exports
├── protocol.py          # RWP v1 binary frames (48B status, 8B ACK, RHB container)
├── validator.py         # 4-stage Pre-Flight hardware & driver compliance checker
├── discovery.py         # Subnet & UDP device scanner
├── fleet.py             # Inventory manager and versioned backups
├── ha_bridge.py         # Home Assistant MQTT Discovery daemon
└── cli.py               # Unified CLI interface
```

---

## 💻 CLI Commands

```powershell
# Fetch binary telemetry
python -m tools.ferrum.cli status --ip 192.168.1.243

# Output structured JSON
python -m tools.ferrum.cli status --ip 192.168.1.243 --json

# Run pre-flight validation
python -m tools.ferrum.cli validate scripts/wifi_blink.js --target esp32c6_supermini

# Deploy validated script over Wi-Fi
python -m tools.ferrum.cli run scripts/wifi_blink.js --ip 192.168.1.243

# Start Home Assistant MQTT Bridge daemon
python -m tools.ferrum.cli ha-bridge --mqtt-host 192.168.1.100
```
