<p align="center">
  <img src="../assets/logo.png" alt="FerrumOS Logo" width="130" height="130" style="border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);">
</p>

# FerrumOS

> **Реактивная микро-ОС и среда Live Hot-Swap для микроконтроллеров RISC-V и ESP32.**

[![Release: v0.6.0](https://img.shields.io/badge/Релиз-v0.6.0-blue.svg)](https://github.com/atitoff-dotcom/FerrumOS/releases)
[![Лицензия: Apache 2.0](https://img.shields.io/badge/Лицензия-Apache%202.0-green.svg)](https://github.com/atitoff-dotcom/FerrumOS/blob/master/LICENSE)
[![Платформа: Windows 10%2F11](https://img.shields.io/badge/Платформа-Windows%2010%2F11-0078D6.svg?logo=windows)](https://github.com/atitoff-dotcom/FerrumOS/releases)
[![Целевая архитектура: RISC-V](https://img.shields.io/badge/Архитектура-RISC--V%20(ESP32--C6%20%7C%20C3)-orange.svg)](https://github.com/atitoff-dotcom/FerrumOS#supported-hardware)

---

FerrumOS — это сверхбыстрая реактивная микро-операционная система прямого управления оборудованием (bare-metal) и среда живой разработки для устройств Интернета вещей (IoT), умного дома и сенсорных узлов.

Пишите на чистом **Modern JavaScript**, загружайте скрипты на работающий чип за **15 миллисекунд по USB или Wi-Fi без перезагрузки платы** и отслеживайте цифровой двойник периферии в реальном времени.

---

## ⚡ Быстрый переход

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Быстрый старт__

    ---

    Прошивка платы и первый реактивный скрипт менее чем за 3 минуты.

    [:octicons-arrow-right-24: Начать обучение](1_getting_started/01_quickstart.md)

-   :material-download:{ .lg .middle } __Скачать Studio__

    ---

    Установщик для Windows или портативная версия без зависимостей.

    [:octicons-arrow-right-24: Скачать v0.6.0](https://github.com/atitoff-dotcom/FerrumOS/releases)

-   :material-book-open-page-variant:{ .lg .middle } __Справочник JS API__

    ---

    Полная спецификация атомарного цепочечного Fluent Chaining API.

    [:octicons-arrow-right-24: Открыть справочник](3_reference/js_api/index.md)

-   :material-file-document-edit:{ .lg .middle } __Реестр RFC__

    ---

    Архитектурные предложения, новые протоколы (CAN, BSB/OpenTherm) и статусы.

    [:octicons-arrow-right-24: Смотреть RFC](rfcs/index.md)

</div>

---

## 📐 Fluent Chaining JavaScript API

FerrumOS строго следует стандарту **Fluent Chaining** для обеспечения абсолютной надежности и исключения аппаратных скачков напряжения (глитчей):

```javascript
// Атомарная инициализация выхода
const relay = GPIO.output(15)
    .openDrain(true)
    .pullUp()
    .invert(true)
    .initial(false);

// Аппаратный детектор жестов с нулевым расходом процессора
const btn = GPIO.input(9)
    .pullUp()
    .button()
    .clickMs(350)
    .doubleClickMs(250)
    .longPressMs(800);

// Реактивный цикл событий
while (true) {
    const gesture = btn.wait(); // Просыпается только при физическом нажатии

    if (gesture === Button.CLICK) {
        relay.write(!relay.read());
    }
}
```

---

## 🚀 Ключевые возможности

- **Мгновенный деплой Hot-Swap за 15 мс**: Обновление кода без перезагрузки платы, потери сетевых соединений или сброса калибровки датчиков.
- **Реактивный спящий процессор**: Процессор спит в глубоком энергосбережении и просыпается только по аппаратным очередям прерываний.
- **Цифровой двойник (Digital Twin)**: Наглядная схема пинов, уровней сигналов, коэффициентов заполнения ШИМ и напряжений АЦП в Studio.
- **Home Assistant MQTT Auto-Discovery**: Автоматическая публикация сенсоров и реле в Lovelace-дашборды без ручной правки YAML.
- **Атомарный I/O без глитчей**: Полная защита от дребезга и зависаний силовых ключей при реконфигурации.

---

## 🔌 Поддерживаемые платы

| Микроконтроллер / Плата | Архитектура ядра | Радиоинтерфейсы | Сценарии применения |
|---|---|---|---|
| **ESP32-C6 SuperMini** | RISC-V (rv32imac, 160 МГц) | Wi-Fi 6, 802.15.4 (Thread / Zigbee), BLE 5 | Thread роутер / конечное устройство, узлы Home Assistant |
| **ESP32-C3 DevKit** | RISC-V (rv32imc, 160 МГц) | Wi-Fi 4, BLE 5 | Автономные Wi-Fi сенсоры, умные реле |
| **BouffaloLab BL702** | RISC-V (rv32imac, 144 МГц) | Zigbee, BLE 5 | Батарейные BLE-метки, электронные ценники ESL |

---

## 🧭 Разделы документации

- **[🚀 Начало работы](1_getting_started/01_quickstart.md)** — Пошаговые вводные уроки от распаковки до первой программы.
- **[💡 Рецепты и задачи](2_recipes/home_assistant_mqtt.md)** — Практические руководства: Home Assistant, глубокий сон, CAN-шина, E-Paper.
- **[📖 Справочник API](3_reference/js_api/index.md)** — Полное описание `GPIO`, `ADC`, `I2C`, `SPI`, `Power`, `CLI`.
- **[⚙️ Концепции платформы](4_concepts/fluent_chaining.md)** — Архитектурные принципы: Fluent Chaining, Hot-Swap, реактивность.
- **[📐 RFC и протоколы](rfcs/index.md)** — Будущие протоколы, открытые предложения и процесс контрибьютинга.
