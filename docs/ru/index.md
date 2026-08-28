# Документация FerrumOS

Добро пожаловать в официальную техническую документацию **FerrumOS** — модульной, отказоустойчивой IoT-платформы на базе Rust и встроенного скриптового движка JavaScript / Rhai для ESP32-C6 и симулятора на ПК.

---

## 📚 Оглавление документации

1. [Архитектурный обзор](architecture.md)
   - 4-уровневая структура разделов памяти (System Base, ядро FerrumOS Core, WASM-драйверы, уровень JS/Rhai)
   - Zero-Cost Сопрограммы: неблокирующий ввод-вывод без тяжелых потоков FreeRTOS
   - Межскриптовое взаимодействие (IPC): шина общего состояния `state`, очереди `queue` и события `events`
   - Сетевой стек `esp-wifi` + `smoltcp` и встроенный HTTP REST сервер (порт 80)
   - Микро-рантайм WAMR AOT и офлайн-конвейер компиляции (`wamrc`)
   - Отказоустойчивость и супервизор скриптов (`ScriptSupervisor`)
   - Бюджет памяти и распределение SRAM на ESP32-C6

2. [Справочник API скриптов (JavaScript и Rhai)](api_reference.md)
   - Zero-Cost сопрограммы (`delay_ms`, неблокирующее выполнение)
   - `console.log` / `console.error`
   - Методы объекта `Math` (`round`, `floor`, `ceil`, `abs`, `max`, `min`, `pow`, `sqrt`)
   - Сериализация `JSON` (`JSON.stringify`, `JSON.parse`)
   - Межскриптовое общее состояние (`state.get`, `state.set`, `state.has`, `state.delete`)
   - Очереди сообщений (`queue.send`, `queue.receive`) и события (`events.emit`, `events.on`)
   - Аппаратный API `device`:
     - GPIO (`read`, `write`)
     - ШИМ и Сервоприводы PWM/LEDC (`set_duty`, `set_angle`)
     - 1-Wire датчики DS18B20 (`read`)
     - Шины I2C, SPI, UART (`read_line`, `write`)
   - Динамическая привязка пинов (`bind_gpio_output`, `bind_pwm`, `bind_onewire_bus`, `bind_i2c_bus`, `bind_uart`)
   - Промышленный Modbus RTU / TCP (`modbus.read_holding`, `modbus.write_single`)
   - Протокол Matter Smart Home (`matter.endpoint`, `on_command`, `set`)
   - Сетевая телеметрия `mqtt.publish`
   - Локальная обработка исключений `try { ... } catch (err) { ... }`

3. [Панель управления Web UI и REST API](web_ui_and_rest.md)
   - Встроенный дашборд в стиле Glassmorphism (`http://<device_ip>/` на ESP32-C6, `http://localhost:8080` на ПК)
   - Мгновенный OTA-деплой скриптов прямо из браузера за <0.05 сек
   - Справочник эндпоинтов REST API (`GET`, `POST`, `PUT`, `DELETE` на `/api/scripts`)

4. [Управление парком устройств (Fleet Manager) и валидация пинов](fleet_management.md)
   - Python CLI для оркестрации (`tools/fleet_manager.py`)
   - Предварительная валидация аппаратных конфликтов пинов
   - Централизованный реестр устройств (`tools/fleet.json`)
   - Мониторинг состояния парка (`status`, `deploy`, `validate`)

5. [Электронные ценники (ESL) и архитектура с потреблением < 1 мкА](esl_electronic_shelf_label.md)
   - Расчет 10+ лет работы от одной батарейки CR2032 (3-часовой цикл пробуждения)
   - Схема дискретной защелки полного обесточивания за $0.02
   - Интеграция E-Paper с Bouffalo Lab BL702 / Telink TLSR8258
   - Шаблон скрипта управления ценником на JS/Rhai

6. [Нативная прошивка ESP32-C6 и руководство по прошивке](esp32c6_native_firmware.md)
   - Архитектура RISC-V `no_std` (`esp-hal`, `esp-alloc`, `esp-wifi`, `smoltcp`)
   - Карта разделов Flash и заголовок дескриптора приложения ESP-IDF
   - Оптимизация размера прошивки до ~689 КБ
   - Прошивка через `esptool` и `espflash` по USB (`COM3`)
   - Мониторинг вывода UART в реальном времени

7. [Руководство по настройке и сборке Wi-Fi (ESP32-C6 Bare-Metal)](wifi_hardware_guide.md)
   - Эталонная матрица зависимостей (`esp-hal 1.0`, `esp-wifi 0.15.1`, `smoltcp`)
   - Настройка скрипта линкера (`linkall.x`) и дескриптора `esp_app_desc!()`
   - Автопоиск сетей, подключение, DHCP-клиент и HTTP REST сервер
   - Таблица решения типовых проблем сборки и подключения (Troubleshooting)

8. [Руководство по OTA Hot-Swap и компилятору JavaScript](ota_hot_swap_guide.md)
   - Спецификация бинарного контейнера `.rhb` (Magic `RHB\x01`, CRC16)
   - Использование CLI-утилиты `ferrum-cli` (`compile`, `test`, `run`, `status`)
   - Горячая замена байткода на ESP32-C6 по Wi-Fi без перезагрузки платы (zero-downtime)
   - Деплой через HTTP REST (`POST /api/bytecode`), `curl` и `PowerShell`

9. [Спецификация бинарного протокола Ferrum Realtime Protocol (FRP v1)](ferrum_wire_protocol.md)
   - Сверхкомпактный протокол: телеметрия за 48 байт, подтверждение загрузки за 8 байт
   - Прямой обмен C/Rust структурами без JSON и строковых аллокаций
   - Нативная совместимость с MTU 127 байт в Thread / IEEE 802.15.4
   - Миллисекундный отклик и максимальная энергоэффективность

10. [Руководство по Python-тулчейну и интеграции с Home Assistant](python_toolchain_and_ha_guide.md)
   - Архитектура единого хостового пакета `tools/ferrum/`
   - Pre-Flight Валидатор железа, карты пинов, соответствия драйверов и коллизий
   - Прямой бинарный клиент RWP на базе `struct.pack` / `struct.unpack`
   - Автоматическое обнаружение и публикация сенсоров в Home Assistant (MQTT Discovery)

11. [Начало работы и руководство по разработке](getting_started.md)
   - Сборка и тестирование (`cargo test`, `cargo run`)
   - Оптимизация release-бинарника (`opt-level = "z"`, LTO, strip)

12. [План разработки и дорожная карта](../../ROADMAP.md)
   - Драйверы DS18B20 1-Wire, Modbus RTU RS485, PWM LEDC
   - Кроссплатформенность: BL602 (RISC-V), RP2040, STM32
