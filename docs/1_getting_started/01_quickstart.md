# Tutorial 1: Quickstart (Zero to Hero)

`Status: 🟢 Stable (v5.0)` • `Targets: ESP32-C6, ESP32-C3, BL702` • `Tool: FerrumOS Studio 5.0`

Welcome to FerrumOS! This tutorial takes you from an unboxed RISC-V microcontroller to writing and executing your first live automation script in under 5 minutes.

---

## Prerequisites & Hardware

You will need:
- An **ESP32-C6** (recommended for Thread + Wi-Fi) or **ESP32-C3** development board, or **BL702** evaluation board.
- A standard USB-C cable for serial communication and flashing.
- A Chromium-based web browser (Chrome, Edge) with Web Serial support, or the standalone **FerrumOS Studio** desktop application (`FerrumOS-Studio.exe`).

---

## Step 1: Launch FerrumOS Studio

1. Download or launch `FerrumOS-Studio.exe` (or open the local Studio web server at `http://localhost:8080`).
2. Plug your microcontroller into your computer using the USB-C data cable.
3. In the top navigation bar of Studio, click **Connect**. Select your microcontroller's USB Serial COM port from the prompt.

---

## Step 2: 1-Click Firmware Provisioning

If your board does not have FerrumOS installed yet:
1. Navigate to the **Flasher** tab in Studio.
2. Select your chip target: **ESP32-C6** (or ESP32-C3).
3. Select radio profile: **Balanced (8 dBm)** or **Eco (4 dBm)**.
4. Click **Flash Firmware**. FerrumOS Studio will automatically install the bootloader, partition table, and FerrumOS real-time kernel via Web Serial.

Once complete, the board will reboot and emit a green connection badge in the Studio dashboard.

---

## Step 3: Write Your First Automation Script

Navigate to the **IDE / Scripts** tab. Create a new file called `blink.js` and paste the following code:

<!-- snippet: id="delay_timing" category="Циклы и задержки" title="Мигание и задержка (Blink)" icon="fa-clock" desc="Периодический цикл переключения выхода с задержкой delay(ms)." badges="['Main Loop', 'delay(500)', 'Fluent Chaining']" -->
```javascript
// Configure status LED on GPIO 8 using atomic Fluent Chaining
const led = GPIO.output(8)
    .pullUp()
    .invert(true)
    .initial(false);

// Periodic blink loop
while (true) {
    led.write(true);
    delay(500);
    led.write(false);
    delay(500);
}
```

> [!NOTE]
> Notice the configuration syntax: `GPIO.output(8).pullUp().invert(true).initial(false)`. FerrumOS enforces **Fluent Chaining** to ensure that register configuration is atomic and prevents glitches on hardware pins.

---

## Step 4: Deploy and Run

1. Click the **Run** button (or press `Ctrl+Enter`).
2. The Studio compiler compiles your JavaScript to FerrumOS bytecode in ~2 milliseconds and uploads it to the microcontroller.
3. Look at your board: the LED on GPIO 8 will immediately begin blinking.
4. Check the **Telemetry** window at the bottom: live execution logs and loop performance will be displayed in real time.

Congratulations! You have deployed your first fault-tolerant task on FerrumOS. Next, continue to [Tutorial 2: First Climate Sensor](02_first_sensor.md).
