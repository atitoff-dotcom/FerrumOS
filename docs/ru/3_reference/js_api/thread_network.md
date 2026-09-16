# Справочник Thread и сети 802.15.4

`Статус: 🔵 Превью / RFC` • `Чип: ESP32-C6 (802.15.4)` • `Этап: Дорожная карта (Этап 9)`

> [!NOTE]
> Стек ячеистой сети Thread и Matter-over-Thread находится в стадии архитектурного проектирования. Низкоуровневый арбитраж радиоэфира описан в [Радиоархитектура](../../rfcs/0007-brokerless-decentralized-fabric.md).

Модуль `Thread` обеспечивает прямое IPv6-взаимодействие по радиоканалу IEEE 802.15.4 в mesh-сетях Thread и стандарте Matter.

---

## Отправка телеметрии: `Thread.endpoint(uri)`

```javascript
Thread.endpoint("coap://[fd00::1]/sensors/climate")
    .confirmable(false)
    .payload({ temp: 22.5, humidity: 45 })
    .send();
```

### Методы цепочки конфигурации
- `.confirmable(enabled: boolean)` — Задает режим передачи CoAP: подтверждаемый (CON) или неподтверждаемый (NON). Для экономии батарейки рекомендуется `false`.
- `.payload(data: object | string | number[])` — Упаковывает данные в компактный JSON/CBOR.
- `.timeoutMs(ms: number)` — Таймаут ожидания ответа.
- `.send(): boolean` — Передает пакет родительскому роутеру через 6LoWPAN.
