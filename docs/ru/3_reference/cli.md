# Справочник CLI ferrum

`Статус: 🟢 В релизе (v5.0)` • `Тулчейн: Python / Rust Toolchain`

Утилита командной строки `ferrum` управляет сборкой, прошивкой и упаковкой компонентов FerrumOS.

## Основные команды
- `ferrum build` — Компиляция пользовательских JS-скриптов в байткод.
- `ferrum flash --target <чип>` — Прошивка ядра и загрузчика по USB.
- `ferrum as-build` — Компиляция исходников AssemblyScript (`.ts` -> `.wasm`).
- `ferrum aot-pack` — Сборка AOT RISC-V пакетов драйверов (`.faot`).
- `ferrum aot-info <pkg.faot>` — Анализ символов и VTable в архиве `.faot`.
