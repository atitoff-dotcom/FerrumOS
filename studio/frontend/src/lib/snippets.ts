export interface SnippetOption {
  id: string;
  label: string;
  icon: string;
  code: string;
}

export interface SnippetCategory {
  title: string;
  icon: string;
  color: string;
  items: SnippetOption[];
}

export const SNIPPET_CATEGORIES: SnippetCategory[] = [
  {
    title: 'Кнопки / Входы',
    icon: 'fa-toggle-on',
    color: 'text-sky-400',
    items: [
      {
        id: 'btn_smart_gestures',
        label: 'Умная кнопка (Click, Double, Hold)',
        icon: 'fa-hand-pointer',
        code: `// Умная кнопка с распознаванием жестов (Pin 9)
let btn = gpio.button(9, {
    pull: "up",
    debounce_ms: 25,
    click_ms: 350,
    double_click_ms: 250,
    long_press_ms: 800
});

while (true) {
    let evt = btn.wait(); // Ожидание события без нагрузки на CPU
    if (evt == "click") {
        print(">>> Одиночный клик!");
        gpio.write(15, 1);
    } else if (evt == "double_click") {
        print(">>> Двойной клик!");
        gpio.write(15, 0);
    } else if (evt == "long_press") {
        print(">>> Длинное удержание!");
        rgb.set(8, 255, 0, 0);
    } else if (evt == "release") {
        print(">>> Кнопка отпущена");
        rgb.set(8, 0, 0, 0);
    }
}
`
      },
      {
        id: 'btn_debounce',
        label: 'Антидребезг (Debounce 25ms)',
        icon: 'fa-shield',
        code: '// Кнопка с аппаратным антидребезгом (25 мс)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    debounce_ms: 25\n});\n'
      },
      {
        id: 'btn_auto_off',
        label: 'Импульс / Автосброс (Auto-Off 200ms)',
        icon: 'fa-stopwatch',
        code: '// Одновибратор / Кнопка с импульсным автосбросом (200 мс)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    debounce_ms: 25,\n    auto_off_ms: 200\n});\n'
      },
      {
        id: 'btn_delayed_on',
        label: 'Задержка включения (Delayed ON 100ms)',
        icon: 'fa-hourglass-start',
        code: '// Вход с защитой от помех (задержка включения 100 мс)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    delayed_on_ms: 100\n});\n'
      },
      {
        id: 'btn_delayed_off',
        label: 'Задержка выключения (Delayed OFF 500ms)',
        icon: 'fa-hourglass-end',
        code: '// Вход с задержкой выключения (удержание 500 мс для датчиков движения)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    delayed_off_ms: 500\n});\n'
      },
      {
        id: 'btn_symmetric',
        label: 'Симметричный фильтр (50ms ON / 50ms OFF)',
        icon: 'fa-sliders',
        code: '// Симметричный фильтр включения и выключения (50 мс)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    delayed_on_off_ms: 50\n});\n'
      },
      {
        id: 'btn_direct_read',
        label: 'Прямое чтение gpio.read(pin)',
        icon: 'fa-eye',
        code: 'if (gpio.read(9)) {\n    // Действие при нажатии кнопки\n}\n'
      }
    ]
  },
  {
    title: 'Выходы / LED',
    icon: 'fa-lightbulb',
    color: 'text-amber-400',
    items: [
      {
        id: 'led_blink',
        label: 'Мигание светодиодом (Blink 500ms)',
        icon: 'fa-bolt',
        code: '// Мигание светодиодом (Pin 15)\ngpio.output(15);\nwhile (true) {\n    gpio.write(15, 1);\n    delay(500);\n    gpio.write(15, 0);\n    delay(500);\n}\n'
      },
      {
        id: 'led_pulse',
        label: 'Одиночный импульс (Pulse 100ms)',
        icon: 'fa-wave-square',
        code: '// Одиночный импульс (100 мс)\ngpio.write(15, 1);\ndelay(100);\ngpio.write(15, 0);\n'
      },
      {
        id: 'out_opendrain',
        label: 'Выход Open-Drain (Реле/Ключи)',
        icon: 'fa-network-wired',
        code: '// Выход Open-Drain (для реле и транзисторных ключей)\ngpio.output(15, { type: "open_drain", initial: 0 });\n'
      }
    ]
  },
  {
    title: 'RGB WS2812',
    icon: 'fa-palette',
    color: 'text-emerald-400',
    items: [
      {
        id: 'rgb_static',
        label: 'Статичный цвет (rgb.set R,G,B)',
        icon: 'fa-paint-roller',
        code: '// Управление адресным светодиодом WS2812 (Pin 8: R, G, B)\nrgb.set(8, 0, 255, 0); // Зеленый\n'
      },
      {
        id: 'rgb_rainbow',
        label: 'Плавная радуга (Rainbow)',
        icon: 'fa-rainbow',
        code: '// Плавная радуга WS2812\nwhile (true) {\n    rgb.set(8, 255, 0, 0); delay(300);\n    rgb.set(8, 0, 255, 0); delay(300);\n    rgb.set(8, 0, 0, 255); delay(300);\n}\n'
      },
      {
        id: 'rgb_strobe',
        label: 'Вспышка стробоскопа (Strobe)',
        icon: 'fa-sun',
        code: '// Вспышка стробоскопа WS2812\nrgb.set(8, 255, 255, 255);\ndelay(50);\nrgb.set(8, 0, 0, 0);\n'
      },
      {
        id: 'rgb_off',
        label: 'Выключить RGB',
        icon: 'fa-power-off',
        code: 'rgb.set(8, 0, 0, 0);\n'
      }
    ]
  },
  {
    title: 'MQTT & Cloud',
    icon: 'fa-tower-broadcast',
    color: 'text-purple-400',
    items: [
      {
        id: 'mqtt_pub',
        label: 'Отправка в топик (mqtt.publish)',
        icon: 'fa-paper-plane',
        code: '// Отправка значения в MQTT брокер\nmqtt.publish("home/sensors/btn9", 1);\n'
      },
      {
        id: 'mqtt_wait',
        label: 'Ожидание команды (mqtt.wait)',
        icon: 'fa-inbox',
        code: '// Ожидание команды из топика MQTT\nlet cmd = mqtt.wait("home/commands/relay", 5000);\n'
      }
    ]
  },
  {
    title: 'Шина IPC',
    icon: 'fa-microchip',
    color: 'text-indigo-400',
    items: [
      {
        id: 'ipc_send',
        label: 'Отправка в канал IPC (ipc.send)',
        icon: 'fa-arrow-up-from-bracket',
        code: '// Отправка в локальную шину IPC (канал 10, значение 1)\nipc.send(10, 1);\n'
      },
      {
        id: 'ipc_recv',
        label: 'Прием из канала IPC (ipc.recv)',
        icon: 'fa-arrow-down-to-bracket',
        code: '// Прием значения из локальной шины IPC\nlet val = ipc.recv(10);\n'
      }
    ]
  },
  {
    title: 'Циклы и задержки',
    icon: 'fa-clock',
    color: 'text-slate-400',
    items: [
      {
        id: 'delay',
        label: 'Задержка delay(500)',
        icon: 'fa-hourglass',
        code: 'delay(500);\n'
      },
      {
        id: 'loop_while',
        label: 'Бесконечный цикл while (true)',
        icon: 'fa-rotate',
        code: 'while (true) {\n    // Тело главного цикла задачи\n    delay(50);\n}\n'
      }
    ]
  }
];
