# FerrumOS RFCs (Request for Comments & Living Specifications)

Этот каталог содержит архитектурные спецификации, описания протоколов и дорожную карту подсистем **FerrumOS**.

Каталог `rfcs/` является **Единым источником правды (Single Source of Truth)** для инженерной документации и встроенной справки FerrumOS Studio.

---

## 📐 Обязательный стандарт структуры каждого RFC

Каждый RFC строится строго из двух ключевых разделов:

1. **`## Реализовано` (Active Specification)**:
   - Точные спецификации того, что фактически закодировано и работает в текущем релизе.
   - Wire-протоколы, опкоды байткода, регистры и структуры пакетов.
   - Сигнатуры Fluent JS API (`GPIO`, `I2C`, `SPI`, `ADC`, `Power`, `Signal`, `MQTT`).
   - **Все интерактивные сниппеты для FerrumOS Studio** (разметка `<!-- snippet: ... -->`).
2. **`## Планируется` (Roadmap & Future Work)**:
   - Проектируемые фичи следующих релизов, открытые вопросы (Open Questions) и архитектурные наброски.
   - По мере реализации фичи переносятся наверх — в раздел `## Реализовано`.

---

## 📋 Реестр спецификаций

| Номер | Заголовок | Статус | Связанные модули |
|---|---|---|---|
| [RFC-0001](0001-can-distributed-bus.md) | Распределенная шина CAN (TWAI) и реактивные сигналы | In Progress | `esp32c6-firmware`, `ferrum-compiler` |
| [RFC-0002](0002-gpio-input-gestures.md) | Аппаратный детектор жестов и фильтрация цифровых входов | Implemented | `vm.rs`, `ferrum-compiler` |
| [RFC-0003](0003-self-healing-discovery.md) | Самовосстанавливающийся Discovery и сетевой контур WSRPC | Implemented / Active | `fleet_management`, `esp32c6-firmware`, `web_server` |
| [RFC-0004](0004-ferrum-hub.md) | FerrumHub: Сервер оркестрации, плагинов и мостов (CAN/Matter/Web) | Draft / Accepted | `ferrum-hub`, `rs-matter`, `wire_protocol` |
| [RFC-0005](0005-high-availability-clustering.md) | High Availability & Hot Standby: Отказоустойчивая кластеризация 1+1 для FerrumHub | Draft / Accepted | `ferrum-runner`, `ferrum-hub`, `ferrum-protocol` |
| [RFC-0006](0006-ferrum-canvas-visual-dashboard.md) | FerrumCanvas & FerrumTouch: Визуальный No-Code конструктор дашбордов для смартфонов и планшетов | Draft / Accepted | `ferrum-hub`, `ferrum-runner`, `tools/ferrum/frontend` |
| [RFC-0007](0007-brokerless-decentralized-fabric.md) | Brokerless Decentralized Fabric: Децентрализованный P2P-обмен (Thread / CAN / UDP Multicast) без брокеров | Draft / Accepted | `esp32c6-firmware`, `ferrum-compiler`, `ferrum-hub` |
| [RFC-0008](0008-ferrum-scada-universal-mimic.md) | FerrumSCADA: Сквозная компонентная архитектура, иерархия путей, умный компилятор и живые SVG-мнемосхемы | Draft / Accepted | `@ferrumos/compiler`, `ferrum-runner`, `ferrum-hub` |
| [RFC-0009](0009-fault-and-stress-testing-protocol.md) | Регламент испытаний на надежность: инъекция сбоев (Fault Injection), стресс-тесты и эталон ESPHome | Draft / Accepted | `ferrum-runner`, `esp32c6-firmware`, `ferrum-protocol` |
| [RFC-0010](0010-bsb-boiler-system-bus.md) | Unified Boiler Stack: мультипротокольный шлюз (BSB, OpenTherm, eBUS, EMS) | Draft / Accepted | `ferrum-runner`, `esp32c6-firmware`, `@ferrumos/compiler` |
| [RFC-0011](0003-self-healing-discovery.md#планируется) | *(Консолидирован в RFC-0003: Embedded WSRPC & Lightweight Crypto)* | Consolidated | `crates/esp32c6-firmware`, `tools/ferrum` |
| [RFC-0012](0012-network-time-synchronization-and-scheduled-events.md) | Сетевая синхронизация времени и события по расписанию (RFC-0012) | Implemented | `ferrum-protocol`, `tools/ferrum/web_server` |
| [RFC-0013](0013-fluent-hardware-api.md) | Базовая аппаратная периферия — GPIO Выходы, АЦП, ШИМ WS2812 и тайминги | Implemented | `ferrum-compiler`, `vm.rs`, Studio |
| [RFC-0014](0014-buses-i2c-spi.md) | Цифровые шины данных — I2C и SPI Master | Implemented | `esp32c6-firmware`, `ferrum-compiler` |
| [RFC-0015](0015-power-management-deep-sleep.md) | Энергосбережение, режимы сна (Deep Sleep) и телеметрия питания | Implemented | `esp32c6-firmware`, `ferrum-compiler` |
| [RFC-0016](0016-reactive-signals-ipc.md) | Реактивные сигналы и межскриптовое взаимодействие (Zero-Copy IPC) | Implemented | `vm.rs`, `ferrum-compiler` |
| [RFC-0017](0017-home-assistant-mqtt-discovery.md) | Интеграция с Home Assistant и протокол MQTT Auto-Discovery | Implemented | `tools/ferrum/bridge`, Studio |
| [RFC-0018](0018-sqlite-sequential-migrations.md) | Последовательный конвейер миграций базы данных (Sequential Migration Pipeline) | Implemented | `tools/ferrum/migrations.py`, Studio |
