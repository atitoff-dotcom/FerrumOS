# Панель управления Web UI и руководство по REST API

В FerrumOS встроен легковесный HTTP-сервер (`http_server.rs`):
* **На микроконтроллере ESP32-C6:** работает на стандартном **порту 80** (`http://<ip-адрес-платы>/`).
* **В режиме хост-симулятора на ПК:** работает на **порту 8080** (`http://localhost:8080/`).

Сервер предоставляет как встроенную Web UI панель управления в стиле Glassmorphism, так и REST API для автоматизации и CI/CD деплоя.

---

## 🌐 Центр управления Web UI

Встроенный веб-интерфейс доступен в любом современном браузере:

### Возможности:
1. **Мониторинг скриптов в реальном времени:**
   - Отображение всех зарегистрированных скриптов JavaScript / Rhai.
   - Живые статусы (`Running`, `Stopped`, `Failed`).
   - Счетчики циклов выполнения и журнал ошибок.
   - Кнопка мгновенного удаления (**Delete**).

2. **Интерактивная среда деплоя (OTA Deploy):**
   - Поле ввода ID скрипта и редактор исходного кода.
   - Кнопка **«🚀 Deploy over OTA»**.
   - Горячее развертывание и старт выполнения скрипта в RAM менее чем за **0.05 секунды** без перезагрузки платы!

---

## 🔌 Справочник REST API

### 1. Получение списка всех скриптов
* **Метод:** `GET /api/scripts`
* **Формат ответа:** `200 OK`, `application/json`
```json
{
  "scripts": [
    {
      "id": "blink",
      "status": "Running",
      "execution_count": 142
    },
    {
      "id": "thermostat",
      "status": "Running",
      "execution_count": 78
    }
  ]
}
```

### 2. Загрузка / Создание нового скрипта (OTA POST)
* **Метод:** `POST /api/scripts`
* **Заголовки:** `Content-Type: application/json`
* **Тело запроса:**
```json
{
  "id": "fast_blink",
  "code": "bind_gpio_output(\"StatusLED\", 15);\ndevice.gpio(\"StatusLED\").write(true);\ndelay_ms(50);\ndevice.gpio(\"StatusLED\").write(false);\ndelay_ms(50);"
}
```
* **Ответ:** `200 OK`
```json
{
  "status": "created",
  "id": "fast_blink"
}
```

### 3. Горячая замена кода существующего скрипта (OTA PUT)
* **Метод:** `PUT /api/scripts/<id>`
* **Заголовки:** `Content-Type: application/json`
* **Тело запроса:**
```json
{
  "code": "console.log('Новый алгоритм!'); delay_ms(1000);"
}
```
* **Ответ:** `200 OK`
```json
{
  "status": "updated",
  "id": "fast_blink"
}
```

### 4. Удаление скрипта и освобождение ресурсов
* **Метод:** `DELETE /api/scripts/<id>`
* **Ответ:** `200 OK`
```json
{
  "status": "deleted",
  "id": "fast_blink"
}
```
* Если скрипт не найден: `404 Not Found` `{"error": "Script not found"}`.
