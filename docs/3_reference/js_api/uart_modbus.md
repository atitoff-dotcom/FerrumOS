# UART & Modbus Reference
Controls serial communication ports and Modbus RTU frames.

```javascript
const port = UART.port(1)
    .baud(9600)
    .parity("none");

port.write([0x01, 0x03, 0x00, 0x00, 0x00, 0x02, 0xC4, 0x0B]);
```
