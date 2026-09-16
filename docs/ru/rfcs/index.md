# FerrumOS RFCs (Request for Comments)

Этот каталог содержит архитектурные предложения, спецификации будущих протоколов и черновики крупных аппаратных расширений FerrumOS.

## Жизненный цикл RFC

1. **Draft (Черновик)** — предложение сформулировано, находится на этапе обсуждения и технического моделирования.
2. **Accepted (Принято)** — архитектура одобрена, включена в дорожную карту (`ROADMAP.md`).
3. **Implemented (Реализовано)** — функционал внедрен в кодовую базу ядра и компилятора, документация перенесена в основной раздел `docs/`.
4. **Superseded / Withdrawn (Заменено / Отозвано)** — предложение устарело или заменено более поздним RFC.

## Реестр предложений

| Номер | Заголовок | Статус | Связанные модули |
|---|---|---|---|
| [RFC-0001](0001-can-distributed-bus.md) | Распределенная шина CAN (TWAI) и реактивные сигналы | Accepted / In Progress | `esp32c6-firmware`, `ferrum-compiler` |
| [RFC-0002](0002-gpio-input-gestures.md) | Аппаратный детектор жестов и фильтрация цифровых входов | Implemented (Этап 4) | `vm.rs`, `ferrum-compiler` |
| [RFC-0003](0003-self-healing-discovery.md) | Самовосстанавливающаяся топология и авто-дискавери узлов | Draft | `fleet_management`, `wire_protocol` |
| [RFC-0004](0004-ferrum-hub.md) | FerrumHub: Сервер оркестрации, плагинов и мостов (CAN/Matter/Web) | Draft / Accepted | `ferrum-hub`, `rs-matter`, `wire_protocol` |
| [RFC-0005](0005-high-availability-clustering.md) | High Availability & Hot Standby: Отказоустойчивая кластеризация 1+1 для FerrumHub | Draft / Accepted | `ferrum-runner`, `ferrum-hub`, `ferrum-protocol` |
| [RFC-0006](0006-ferrum-canvas-visual-dashboard.md) | FerrumCanvas & FerrumTouch: Визуальный No-Code конструктор дашбордов для смартфонов и планшетов | Draft / Accepted | `ferrum-hub`, `ferrum-runner`, `tools/ferrum/frontend` |
| [RFC-0007](0007-brokerless-decentralized-fabric.md) | Brokerless Decentralized Fabric: Децентрализованный P2P-обмен (Thread / CAN / UDP Multicast) без брокеров | Draft / Accepted | `esp32c6-firmware`, `ferrum-compiler`, `ferrum-hub` |
| [RFC-0008](0008-ferrum-scada-universal-mimic.md) | FerrumSCADA: Сквозная компонентная архитектура, иерархия путей, умный компилятор и живые SVG-мнемосхемы | Draft / Accepted | `@ferrumos/compiler`, `ferrum-runner`, `ferrum-hub`, `rfcs/0005`, `rfcs/0006` |
| [RFC-0009](0009-fault-and-stress-testing-protocol.md) | Регламент испытаний на надежность: инъекция сбоев (Fault Injection), стресс-тесты и эталон ESPHome (Ethernet / CAN / UART) | Draft / Accepted | `ferrum-runner`, `esp32c6-firmware`, `ferrum-protocol`, `rfcs/0008` |
| [RFC-0010](0010-bsb-boiler-system-bus.md) | Unified Boiler Stack: мультипротокольный шлюз (BSB, OpenTherm, eBUS, EMS) | Draft / Accepted | `ferrum-runner`, `esp32c6-firmware`, `@ferrumos/compiler` |
| [RFC-0011](0011-embedded-wsrpc-lightweight-crypto.md) | Embedded WSRPC & Lightweight Hardware Crypto (UID-Derived AEAD) | Active | `vendor_rsgi_wsrpc`, `esp32c6-firmware`, `esp32c3-firmware`, `tools/ferrum` |
| [RFC-0012](0012-network-time-synchronization-and-scheduled-events.md) | Network Time Synchronization & Scheduled Events (Minute Broadcast over WSRPC & CAN) | Active | `ferrum-protocol`, `esp32c6-firmware`, `tools/ferrum/web_server` |


