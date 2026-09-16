# How-To: Electronic Shelf Labels & E-Paper Displays

`Status: 🟢 Stable (v5.0)` • `Targets: ESP32-C6, ESP32-C3` • `Panels: SSD1680 (1.54", 2.13", 2.9")`

Electronic Shelf Labels (ESL) and E-Paper (E-Ink) screens are ideal for battery-powered IoT dashboards because they consume power **only when altering the image**. Once drawn, the display maintains the picture indefinitely without consuming electrical energy.

---

## 1. Hardware Architecture

Connect a 1.54", 2.13", or 2.9" GoodDisplay / Waveshare EPD panel to SPI:

| E-Paper Pin | Microcontroller Pin | Function |
|---|---|---|
| **BUSY** | GPIO 4 | Busy Status (Low = Ready) |
| **RESET** | GPIO 5 | Hardware Reset |
| **D/C** | GPIO 6 | Data / Command Select |
| **CS** | GPIO 7 | SPI Chip Select |
| **SCK** | GPIO 19 | SPI Clock |
| **MOSI** | GPIO 18 | SPI Master Out |

> [!TIP]
> Power the E-Paper VCC through a P-Channel MOSFET controlled by a GPIO. Cut power completely when the chip is sleeping to eliminate the display controller's 20 µA quiescent draw.

---

## 2. Fluent Chaining Initialization

```javascript
// Initialize E-Paper display in fluent chain
const epd = Display.epaper()
    .model("2.9_monochrome")
    .spi(0)
    .pins({ busy: 4, reset: 5, dc: 6, cs: 7 });

// Clear canvas and draw climate info
epd.clear();
epd.drawText(10, 20, "FerrumOS Node", { size: 2 });
epd.drawText(10, 50, `Temp: ${I2C.bus(0).aht20().readTemperature().toFixed(1)} C`);
epd.drawText(10, 80, `Battery: ${Power.batteryVoltage().toFixed(2)} V`);

// Refresh screen (takes ~2 seconds)
epd.refresh();

// Power down display and sleep for 15 minutes
Power.sleep()
    .after(15).minutes()
    .enter();
```

---

## 3. RAM Budget Optimization

Monochrome E-Paper displays require only 1 bit per pixel:
- **200 × 200 px (1.54")**: 5,000 bytes RAM.
- **296 × 128 px (2.9")**: 4,736 bytes RAM.

FerrumOS allocates this framebuffer dynamically during rendering and frees it immediately before deep sleep, ensuring zero SRAM wastage while asleep.
