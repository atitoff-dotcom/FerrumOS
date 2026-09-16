# Справочник шины SPI
Модуль `SPI` управляет аппаратной шиной SPI для скоростной периферии.

<!-- snippet: id="spi_bus" category="Шины данных (I2C / SPI)" title="Шина SPI (Транзакция)" icon="fa-network-wired" desc="Полнодуплексный обмен байтами по шине SPI." badges="['SPI Master', '10MHz', 'Full-Duplex']" -->
```javascript
const spi = SPI.bus(0)
    .frequency(10000000)
    .mode(0);

const response = spi.transfer([0x9F, 0x00, 0x00, 0x00]);
```
