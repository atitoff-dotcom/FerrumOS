// FerrumOS Community Driver: SSD1306 OLED (128x64 / 128x32)
export class SSD1306 {
    constructor(i2cBus, addr = 0x3C, width = 128, height = 64) {
        this.bus = i2cBus;
        this.addr = addr;
        this.width = width;
        this.height = height;
        this.bus.claim(this.addr);
    }
    clear() {
        this.bus.writeReg(this.addr, 0x00, [0xAE, 0x00, 0x10, 0x40]);
    }
}
