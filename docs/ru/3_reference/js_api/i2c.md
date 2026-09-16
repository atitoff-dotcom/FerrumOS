# Справочник шины I2C

Модуль `I2C` управляет аппаратным контроллером I2C в режиме Master.

---

## Инициализация шины: `I2C.bus(bus_id)`

```javascript
const bus = I2C.bus(0)
    .frequency(400000);
```

### Методы конфигурации
- `.frequency(hz: number)` — Тактовая частота шины в Герцах (например, `100000` для Standard, `400000` для Fast mode).
- `.timeoutMs(ms: number)` — Таймаут транзакции в миллисекундах.

### Методы передачи данных
- `bus.writeTo(addr: number, bytes: number[]): void` — Записывает массив байт по 7-битному адресу устройства.
- `bus.readFrom(addr: number, length: number): number[]` — Считывает указанное количество байт.
- `bus.writeRead(addr: number, writeBytes: number[], readLength: number): number[]` — Атомарная запись регистра с последующим чтением (Repeated Start).

---

## Пример: Чтение регистра сенсора

<!-- snippet: id="i2c_bus" category="Шины данных (I2C / SPI)" title="Шина I2C (Чтение регистра)" icon="fa-microchip" desc="Инициализация шины I2C и чтение регистра данных датчика." badges="['I2C Master', '100kHz', 'Repeated Start']" -->
```javascript
const bus = I2C.bus(0)
    .frequency(100000);

// Чтение 2 байт из регистра 0x00 устройства с адресом 0x48
const data = bus.writeRead(0x48, [0x00], 2);
const tempRaw = (data[0] << 8) | data[1];
console.log(`Сырые данные: ${tempRaw}`);
```
