// FerrumOS Community Driver: BME280 I2C Environmental Sensor
export class BME280 {
    constructor(i2cBus, addr = 0x76) {
        this.bus = i2cBus;
        this.addr = addr;
        this.bus.claim(this.addr);
    }
    readTemperature() {
        let raw = this.bus.readReg16(this.addr, 0xFA);
        return (raw / 100.0).toFixed(1);
    }
    readHumidity() {
        let raw = this.bus.readReg16(this.addr, 0xFD);
        return (raw / 1024.0).toFixed(1);
    }
}
