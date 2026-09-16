# Troubleshooting & FAQ

Common hardware, USB, and flashing issues and their quick solutions.

---

## 🔌 1. Device Not Detected in Studio

### Symptoms:
The **Connect** dropdown in the top bar shows "No COM ports found" or your board is not listed.

### Solutions:
1. **USB Cable Type**: Ensure you are using a **data USB-C cable**, not a charge-only cable.
2. **USB-Serial Drivers**:
   - **ESP32-C6 / ESP32-C3 DevKits**: Most boards use the native on-chip USB-JTAG/CDC peripheral (`USB Serial Device`). Windows 10/11 supports it natively.
   - If your board uses an external bridge chip (**CH340**, **CP2102**, or **CH9102**), install the respective Windows VCP driver.
3. **Hardware Boot Mode**:
   Hold the **BOOT** button, plug the board into USB, then release **BOOT**. This forces ROM bootloader mode.

---

## ⚡ 2. Access Denied / COM Port Busy

### Symptoms:
Error: `Access Denied` or `Serial port is already in use by another process`.

### Solutions:
1. Close other serial monitors (Arduino IDE, PuTTY, VS Code Serial Monitor, Cura).
2. If Studio was forcefully closed, unplug and re-plug the USB cable to release the Windows driver handle.

---

## 🚀 3. Flashing Timeout or Checksum Failure

### Symptoms:
The **Flasher** tab stalls at 0% or reports a connection timeout.

### Solutions:
1. Select the correct chip target (**ESP32-C6** or **ESP32-C3**).
2. Lower the flashing baud rate to `460800` or `115200` if using long USB cables or unpowered USB hubs.
3. Keep the board connected directly to a motherboard USB port.

---

## 🌐 4. Wi-Fi or MQTT Connection Drop

### Symptoms:
The node does not appear in Home Assistant or drops off the local network.

### Solutions:
1. Verify that your Wi-Fi SSID operates on the **2.4 GHz band** (ESP32-C6/C3 do not support 5 GHz Wi-Fi).
2. Check that the MQTT broker address in `ferrum_config.json` uses the local IP address (e.g., `192.168.1.100`), not `localhost`.
