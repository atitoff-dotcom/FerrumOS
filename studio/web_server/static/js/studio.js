const currentNodeId = 'c6_supermini_main';
let logEl = null;
let scriptFiles = [];
let activeFileName = '';
let isUnsaved = false;
let showLineNumbers = false;
let editor = null;

function log(msg) {
  if (!logEl) logEl = document.getElementById('consoleLog');
  if (!logEl) return;
  const ts = new Date().toLocaleTimeString();
  logEl.innerHTML += `<div>[${ts}] ${msg}</div>`;
  logEl.scrollTop = logEl.scrollHeight;
}

function clearConsoleLog() {
  if (!logEl) logEl = document.getElementById('consoleLog');
  if (logEl) logEl.innerHTML = '';
}

function getEditorValue() {
  if (editor && typeof editor.getValue === 'function') {
    return editor.getValue();
  }
  const textarea = document.getElementById('codeEditor');
  return textarea ? textarea.value : '';
}

function setEditorValue(val) {
  if (editor && typeof editor.setValue === 'function') {
    editor.setValue(val);
  } else {
    const textarea = document.getElementById('codeEditor');
    if (textarea) textarea.value = val;
  }
  updateStatusBar();
}

// Initialize CodeMirror with fallback
function initEditor() {
  const textarea = document.getElementById('codeEditor');
  if (!textarea) return;

  if (typeof CodeMirror !== 'undefined') {
    try {
      editor = CodeMirror.fromTextArea(textarea, {
        mode: 'javascript',
        theme: 'material-darker',
        lineNumbers: showLineNumbers,
        matchBrackets: true,
        autoCloseBrackets: true,
        tabSize: 4,
        indentUnit: 4,
        lineWrapping: false,
        extraKeys: {
          'Tab': function(cm) {
            if (cm.somethingSelected()) {
              cm.indentSelection('add');
            } else {
              cm.replaceSelection('    ', 'end', '+input');
            }
          },
          'Ctrl-S': function(cm) { saveCurrentScript(); },
          'Cmd-S': function(cm) { saveCurrentScript(); },
          'Ctrl-O': function(cm) { openFileManagerModal(); },
          'Cmd-O': function(cm) { openFileManagerModal(); },
          'Ctrl-Enter': function(cm) { deployScript(); },
          'Cmd-Enter': function(cm) { deployScript(); },
          'F7': function(cm) { runPreFlight(); }
        }
      });

      editor.on('cursorActivity', updateStatusBar);
      editor.on('change', () => {
        isUnsaved = true;
        updateStatusBar();
        const ind = document.getElementById('unsavedIndicator');
        if (ind) ind.style.display = 'inline';
      });
    } catch (e) {
      console.warn('CodeMirror initialization error, using raw textarea:', e);
    }
  } else {
    // Fallback: Bind plain textarea
    textarea.addEventListener('input', () => {
      isUnsaved = true;
      updateStatusBar();
      const ind = document.getElementById('unsavedIndicator');
      if (ind) ind.style.display = 'inline';
    });
    textarea.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        saveCurrentScript();
      } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'o') {
        e.preventDefault();
        openFileManagerModal();
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        deployScript();
      }
    });
  }
}

function toggleLineNumbers() {
  showLineNumbers = !showLineNumbers;
  if (editor && typeof editor.setOption === 'function') {
    editor.setOption('lineNumbers', showLineNumbers);
  }
  const btn = document.getElementById('btnToggleLineNumbers');
  if (btn) {
    if (showLineNumbers) {
      btn.style.color = '#38bdf8';
      btn.style.borderColor = '#38bdf8';
    } else {
      btn.style.color = '#cbd5e1';
      btn.style.borderColor = '#334155';
    }
  }
}

function updateStatusBar() {
  const code = getEditorValue();
  const bytes = new TextEncoder().encode(code).length;
  
  const statFile = document.getElementById('statFileSize');
  if (statFile) statFile.innerHTML = `<i class="fa-regular fa-file-code"></i> ${bytes} B`;

  const estFrb = Math.max(16, Math.round(bytes * 0.35));
  const statBytecode = document.getElementById('statBytecodeSize');
  if (statBytecode) statBytecode.innerHTML = `<i class="fa-solid fa-microchip"></i> ~${estFrb} B FRB`;

  if (editor && typeof editor.getCursor === 'function') {
    const cursor = editor.getCursor();
    const statCursor = document.getElementById('statCursor');
    if (statCursor) statCursor.innerHTML = `<i class="fa-solid fa-location-crosshairs"></i> Ln ${cursor.line + 1}, Col ${cursor.ch + 1}`;
  }

  const statSave = document.getElementById('statSaveState');
  if (statSave) {
    if (isUnsaved) {
      statSave.innerHTML = `<span style="color:#f59e0b;"><i class="fa-solid fa-circle-dot"></i> Не сохранено</span>`;
    } else {
      statSave.innerHTML = `<span style="color:#34d399;"><i class="fa-solid fa-check"></i> Синхронизировано</span>`;
    }
  }
}

// Modal File Manager
function openFileManagerModal() {
  const searchInput = document.getElementById('modalFileSearch');
  if (searchInput) searchInput.value = '';
  renderModalFileList(scriptFiles);
  const modal = document.getElementById('modalFiles');
  if (modal) modal.style.display = 'flex';
  if (searchInput) setTimeout(() => searchInput.focus(), 50);
}

function closeFileManagerModal() {
  const modal = document.getElementById('modalFiles');
  if (modal) modal.style.display = 'none';
}

function onModalOverlayClick(e) {
  if (e.target && e.target.id === 'modalFiles') {
    closeFileManagerModal();
  }
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeFileManagerModal();
  } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'o') {
    e.preventDefault();
    openFileManagerModal();
  }
});

function filterModalFiles() {
  const q = (document.getElementById('modalFileSearch')?.value || '').toLowerCase().trim();
  const filtered = scriptFiles.filter(item => {
    const fn = (typeof item === 'object' ? item.filename : item).toLowerCase();
    const desc = ((typeof item === 'object' && item.description) ? item.description : '').toLowerCase();
    return fn.includes(q) || desc.includes(q);
  });
  renderModalFileList(filtered);
}

function renderModalFileList(files) {
  const listEl = document.getElementById('modalFileList');
  const totalFilesEl = document.getElementById('modalTotalFiles');
  const countBadge = document.getElementById('fileCountBadge');
  if (totalFilesEl) totalFilesEl.innerText = scriptFiles.length;
  if (countBadge) countBadge.innerText = scriptFiles.length;
  if (!listEl) return;
  listEl.innerHTML = '';
  
  if (files.length === 0) {
    listEl.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:1.5rem; font-size:0.85rem;">Скрипты не найдены</div>';
    return;
  }

  files.forEach(item => {
    const f = typeof item === 'object' ? item.filename : item;
    const desc = (typeof item === 'object' && item.description) ? item.description : '';
    const isActive = (f === activeFileName);
    const itemEl = document.createElement('div');
    itemEl.className = `file-dialog-item ${isActive ? 'active' : ''}`;
    itemEl.ondblclick = () => { selectScript(f); closeFileManagerModal(); };
    itemEl.innerHTML = `
      <div class="file-dialog-info">
        <div class="file-dialog-name">
          <i class="fa-brands fa-js" style="color: ${isActive ? '#38bdf8' : '#fbbf24'};"></i>
          <span>${f}</span>
          ${isActive ? '<span style="font-size:0.68rem; color:#38bdf8; background:rgba(56,189,248,0.15); padding:0.1rem 0.35rem; border-radius:4px; margin-left:0.25rem;">Текущий</span>' : ''}
        </div>
        ${desc ? `<div class="file-dialog-desc" title="${desc.replace(/"/g, '&quot;')}">${desc}</div>` : ''}
      </div>
      <div class="file-dialog-actions">
        <button class="btn-file-open" onclick="selectScript('${f}'); closeFileManagerModal();">Открыть</button>
        <button class="btn-file-del" onclick="deleteScriptFile('${f}', event)" title="Удалить файл"><i class="fa-solid fa-trash"></i></button>
      </div>
    `;
    listEl.appendChild(itemEl);
  });
}

async function deleteScriptFile(filename, e) {
  if (e) e.stopPropagation();
  if (!confirm(`Удалить скрипт '${filename}'?`)) return;
  try {
    const resp = await fetch(`/api/scripts/${filename}`, { method: 'DELETE' });
    if (resp.ok) {
      log(`🗑️ Файл '${filename}' удален.`);
      await fetchScriptsList();
      const names = scriptFiles.map(f => typeof f === 'object' ? f.filename : f);
      if (activeFileName === filename && names.length > 0) {
        selectScript(names[0]);
      }
      filterModalFiles();
    } else {
      log(`❌ Ошибка удаления файла '${filename}'`);
    }
  } catch (err) {
    log(`❌ Ошибка: ${err}`);
  }
}

// Hierarchical Snippets Inserter
function insertSnippet(type) {
  let snippet = '';
  switch (type) {
    // Buttons & Inputs
    case 'btn_debounce':
      snippet = `// Кнопка с аппаратным антидребезгом (25 мс)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    debounce_ms: 25\n});\n`;
      break;
    case 'btn_auto_off':
      snippet = `// Одновибратор / Кнопка с импульсным автосбросом (200 мс)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    debounce_ms: 25,\n    auto_off_ms: 200\n});\n`;
      break;
    case 'btn_delayed_on':
      snippet = `// Вход с защитой от помех (задержка включения 100 мс)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    delayed_on_ms: 100\n});\n`;
      break;
    case 'btn_delayed_off':
      snippet = `// Вход с задержкой выключения (удержание 500 мс для датчиков движения)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    delayed_off_ms: 500\n});\n`;
      break;
    case 'btn_symmetric':
      snippet = `// Симметричный фильтр включения и выключения (50 мс)\ngpio.input(9, {\n    pull: "up",\n    invert: true,\n    delayed_on_off_ms: 50\n});\n`;
      break;
    case 'btn_direct_read':
      snippet = `if (gpio.read(9)) {\n    // Действие при нажатии кнопки\n}\n`;
      break;

    // LEDs & Outputs
    case 'led_blink':
      snippet = `// Мигание светодиодом (Pin 15)\ngpio.output(15);\nwhile (true) {\n    gpio.write(15, 1);\n    delay(500);\n    gpio.write(15, 0);\n    delay(500);\n}\n`;
      break;
    case 'led_pulse':
      snippet = `// Одиночный импульс (100 мс)\ngpio.write(15, 1);\ndelay(100);\ngpio.write(15, 0);\n`;
      break;
    case 'out_opendrain':
      snippet = `// Выход Open-Drain (для реле и транзисторных ключей)\ngpio.output(15, { type: "open_drain", initial: 0 });\n`;
      break;

    // RGB WS2812
    case 'rgb_static':
      snippet = `// Управление адресным светодиодом WS2812 (Pin 8: R, G, B)\nrgb.set(8, 0, 255, 0); // Зеленый\n`;
      break;
    case 'rgb_rainbow':
      snippet = `// Плавная радуга WS2812\nwhile (true) {\n    rgb.set(8, 255, 0, 0); delay(300);\n    rgb.set(8, 0, 255, 0); delay(300);\n    rgb.set(8, 0, 0, 255); delay(300);\n}\n`;
      break;
    case 'rgb_strobe':
      snippet = `// Вспышка стробоскопа WS2812\nrgb.set(8, 255, 255, 255);\ndelay(50);\nrgb.set(8, 0, 0, 0);\n`;
      break;
    case 'rgb_off':
      snippet = `rgb.set(8, 0, 0, 0);\n`;
      break;

    // MQTT & IoT
    case 'mqtt_pub':
      snippet = `// Отправка значения в MQTT брокер\nmqtt.publish("home/sensors/btn9", 1);\n`;
      break;
    case 'mqtt_wait':
      snippet = `// Ожидание команды из топика MQTT\nlet cmd = mqtt.wait("home/commands/relay", 5000);\n`;
      break;

    // IPC Bus
    case 'ipc_send':
      snippet = `// Отправка в локальную шину IPC (канал 10, значение 1)\nipc.send(10, 1);\n`;
      break;
    case 'ipc_recv':
      snippet = `// Прием значения из локальной шины IPC\nlet val = ipc.recv(10);\n`;
      break;

    // Timers & Control
    case 'delay':
      snippet = `delay(500);\n`;
      break;
    case 'loop_while':
      snippet = `while (true) {\n    // Тело главного цикла задачи\n    delay(50);\n}\n`;
      break;
  }

  if (editor && typeof editor.getDoc === 'function') {
    const doc = editor.getDoc();
    const cursor = doc.getCursor();
    doc.replaceRange(snippet, cursor);
    editor.focus();
  } else {
    const textarea = document.getElementById('codeEditor');
    if (textarea) {
      const start = textarea.selectionStart || 0;
      const end = textarea.selectionEnd || 0;
      textarea.value = textarea.value.substring(0, start) + snippet + textarea.value.substring(end);
      textarea.selectionStart = textarea.selectionEnd = start + snippet.length;
      textarea.focus();
      updateStatusBar();
    }
  }
}

async function selectScript(filename) {
  if (activeFileName === filename) return;
  if (isUnsaved) {
    if (!confirm(`Файл '${activeFileName}' содержит несохраненные изменения. Переключить без сохранения?`)) {
      return;
    }
  }
  activeFileName = filename;
  const nameBadge = document.getElementById('activeFileNameText');
  if (nameBadge) nameBadge.innerText = filename;
  await loadScriptContent(filename);
  isUnsaved = false;
  const ind = document.getElementById('unsavedIndicator');
  if (ind) ind.style.display = 'none';
  renderModalFileList(scriptFiles);
}

async function loadScriptContent(filename) {
  try {
    const resp = await fetch(`/api/scripts/${filename}`);
    if (resp.ok) {
      const data = await resp.json();
      setEditorValue(data.code);
      isUnsaved = false;
      const ind = document.getElementById('unsavedIndicator');
      if (ind) ind.style.display = 'none';
      updateStatusBar();
      log(`Загружен файл '${filename}' в редактор.`);
    }
  } catch (e) {
    log(`❌ Ошибка чтения файла: ${e}`);
  }
}

async function saveCurrentScript() {
  if (!activeFileName) return;
  const code = getEditorValue();
  try {
    const resp = await fetch(`/api/scripts/${activeFileName}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code})
    });
    if (resp.ok) {
      isUnsaved = false;
      const ind = document.getElementById('unsavedIndicator');
      if (ind) ind.style.display = 'none';
      updateStatusBar();
      log(`💾 Файл '${activeFileName}' сохранен на диск.`);
    }
  } catch (e) {
    log(`❌ Ошибка сохранения: ${e}`);
  }
}

async function createNewScript() {
  const name = prompt('Введите имя нового файла:', 'task.js');
  if (!name) return;
  const filename = name.endsWith('.js') ? name : `${name}.js`;
  const initialCode = '// FerrumOS JavaScript Task\\nprint(">>> Running ' + filename + '...");\\n\\nwhile (true) {\n    rgb.set(8, 0, 255, 0);\n    delay(500);\n    rgb.set(8, 0, 0, 0);\n    delay(500);\n}\\n';
  try {
    const resp = await fetch(`/api/scripts/${filename}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code: initialCode})
    });
    if (resp.ok) {
      log(`✨ Создан файл '${filename}'!`);
      await fetchScriptsList();
      selectScript(filename);
      closeFileManagerModal();
    }
  } catch (e) {
    log(`❌ Ошибка создания: ${e}`);
  }
}

async function runPreFlight() {
  const filename = activeFileName || 'task.js';
  const taskId = filename.replace('.js', '');
  const code = getEditorValue();
  log(`🔍 Кросс-проверка '${taskId}' с задачами в RAM чипа...`);
  try {
    const resp = await fetch(`/api/nodes/${currentNodeId}/validate-context`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code, board: 'esp32c6_supermini', task_id: taskId})
    });
    const data = await resp.json();
    if (data.valid) {
      log('✅ <strong style="color:#34d399">Кросс-проверка пройдена!</strong> Коллизий пинов и шин с активными задачами не обнаружено.');
    } else {
      log('⛔ <strong style="color:#ef4444">Ошибки коллизии ресурсов:</strong>');
      data.errors.forEach(e => log(`   • ${e.message}`));
    }
  } catch (err) {
    log(`❌ Ошибка проверки: ${err}`);
  }
}

async function deployScript() {
  const filename = activeFileName || 'task.js';
  const code = getEditorValue();
  log(`🚀 Hot-Swap задачи '${filename}' в RAM ESP32-C6...`);
  try {
    const resp = await fetch(`/api/nodes/${currentNodeId}/deploy`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code, filename, board: 'esp32c6_supermini'})
    });
    const data = await resp.json();
    if (resp.ok) {
      log(`✨ <strong style="color:#34d399">Hot-Swap '${filename}' успешен!</strong> Запущено в RAM микропроцессора.`);
      await refreshDigitalTwin();
    } else {
      log(`❌ Ошибка деплоя: ${data.detail || 'Неизвестная ошибка'}`);
    }
  } catch (err) {
    log(`❌ Ошибка соединения: ${err}`);
  }
}

async function commitFlashStorage() {
  log(`💾 Фиксация задач в энергонезависимую Flash-память (0x300000)...`);
  try {
    const resp = await fetch(`/api/nodes/${currentNodeId}/flash/commit`, {method: 'POST'});
    const data = await resp.json();
    if (resp.ok) {
      log(`💾 <strong style="color:#38bdf8">Успешно сохранено ${data.saved_count} задач во Flash!</strong> Автозапуск активирован.`);
    } else {
      log(`❌ Ошибка записи во Flash: ${data.detail || 'Ошибка'}`);
    }
  } catch (err) {
    log(`❌ Ошибка соединения: ${err}`);
  }
}

async function testMqttConnection() {
  const btn = document.getElementById('btnMqttTest');
  if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing...';
  log(`📡 Проверка связи с MQTT Брокером...`);
  try {
    const resp = await fetch(`/api/nodes/${currentNodeId}/mqtt/test`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({host: '192.168.1.114', port: 1883, username: 'alex', password: 'bh0020'})
    });
    const data = await resp.json();
    if (data.ok) {
      if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-circle-check" style="color:#34d399"></i> MQTT OK';
        btn.style.borderColor = 'rgba(52, 211, 153, 0.5)';
        btn.style.color = '#34d399';
      }
      log(`🟢 <strong style="color:#34d399">MQTT Брокер доступен!</strong> ${data.broker} (Задержка: ${data.latency_ms} мс)`);
    } else {
      if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-circle-xmark" style="color:#ef4444"></i> MQTT Fail';
        btn.style.borderColor = 'rgba(239, 68, 68, 0.5)';
        btn.style.color = '#ef4444';
      }
      log(`❌ <strong style="color:#ef4444">MQTT Брокер недоступен:</strong> ${data.error || data.message}`);
    }
    setTimeout(() => {
      if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-tower-broadcast"></i> Test MQTT';
        btn.style.borderColor = 'rgba(6, 182, 212, 0.4)';
        btn.style.color = '#38bdf8';
      }
    }, 4000);
  } catch (err) {
    if (btn) btn.innerHTML = '<i class="fa-solid fa-circle-xmark" style="color:#ef4444"></i> Err';
    log(`❌ Ошибка проверки MQTT: ${err}`);
  }
}

async function refreshDigitalTwin() {
  try {
    const resp = await fetch(`/api/nodes/${currentNodeId}/twin`);
    if (!resp.ok) return;
    const data = await resp.json();
    
    // 1. Render Running Tasks in RAM
    const taskListEl = document.getElementById('runningTasksList');
    const tasks = Object.values(data.active_tasks || {});
    const taskCountEl = document.getElementById('taskCount');
    if (taskCountEl) taskCountEl.innerText = tasks.length;
    
    if (taskListEl) {
      if (tasks.length === 0) {
        taskListEl.innerHTML = '<div style="font-size: 0.75rem; color: var(--text-muted); text-align: center; padding: 1rem;">Нет активных задач в RAM чипа</div>';
      } else {
        taskListEl.innerHTML = '';
        tasks.forEach(t => {
          let pinBadges = '';
          for (const [p, tag] of Object.entries(t.pins || {})) {
            pinBadges += `<span class="pin-badge">GPIO ${p} (${tag})</span>`;
          }
          const execCountInfo = t.execution_count ? ` • ⚡ ${t.execution_count} execs` : '';
          let statusLabel = `<span style="color:#34d399;">● Active</span>`;
          if (t.status === 'Running') statusLabel = `<span style="color:#38bdf8;">● Exec</span>`;
          else if (t.status === 'WaitingIpc') statusLabel = `<span style="color:#a78bfa;">● Wait IPC</span>`;
          else if (t.status === 'WaitingMqtt') statusLabel = `<span style="color:#06b6d4;">● Wait MQTT</span>`;
          else if (t.status === 'Stopped') statusLabel = `<span style="color:#f87171;">● Stopped</span>`;
          else if (t.status === 'Failed') statusLabel = `<span style="color:#ef4444;">● Error</span>`;

          const sizeBytes = t.frb_size ?? t.rhb_size ?? t.size ?? t.js_size ?? 0;
          taskListEl.innerHTML += `
            <div class="task-item">
              <div class="task-info">
                <div class="task-name">
                  <i class="fa-solid fa-play" style="color:#34d399; font-size:0.65rem;"></i> 
                  ${t.task_id || t.id}
                  <span class="live-chip-badge"><i class="fa-solid fa-floppy-disk"></i> Flash</span>
                </div>
                <div class="task-meta">${sizeBytes} B • ${statusLabel}${execCountInfo}</div>
                <div class="task-pins">${pinBadges || '<span class="pin-badge">No GPIO</span>'}</div>
              </div>
              <div class="task-actions">
                <button class="btn-edit-task" onclick="loadTaskIntoEditor('${t.task_id || t.id}')" title="Открыть в редакторе"><i class="fa-solid fa-code"></i></button>
                <button class="btn-unload" onclick="unloadTask('${t.task_id || t.id}')" title="Выгрузить из RAM"><i class="fa-solid fa-stop"></i></button>
              </div>
            </div>
          `;
        });
      }
    }

    // 2. Render Pinout Grid
    const gridEl = document.getElementById('pinGrid');
    if (gridEl) {
      gridEl.innerHTML = '';
      (data.pin_matrix || []).forEach(p => {
        if (p.pin > 23) return;
        let statusClass = 'pin-free';
        if (p.status === 'claimed') statusClass = 'pin-claimed';
        else if (p.status === 'bus') statusClass = 'pin-bus';
        else if (p.status === 'forbidden') statusClass = 'pin-forbidden';

        gridEl.innerHTML += `
          <div class="pin-cell ${statusClass}" title="GPIO ${p.pin}: ${p.owner}">
            <div class="pin-num">${p.pin}</div>
            <div style="font-size:0.6rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${p.status}</div>
          </div>
        `;
      });
    }

    // 3. Render Shared Busses
    const busListEl = document.getElementById('busList');
    if (busListEl) {
      const busses = data.shared_busses || {};
      let busHtml = '';
      
      (busses.i2c || []).forEach(i2c => {
        busHtml += `
          <div class="bus-item">
            <div class="bus-header"><span><i class="fa-solid fa-circle-nodes"></i> I2C '${i2c.alias}'</span> <span>${i2c.sda}/${i2c.scl}</span></div>
            <div class="bus-detail">Dev: ${(i2c.devices || []).join(', ')} • ${i2c.task_id}</div>
          </div>
        `;
      });
      (busses.spi || []).forEach(spi => {
        busHtml += `
          <div class="bus-item">
            <div class="bus-header"><span><i class="fa-solid fa-microchip"></i> SPI '${spi.alias}'</span> <span>CS:${spi.cs}</span></div>
            <div class="bus-detail">MOSI:${spi.mosi} • ${spi.task_id}</div>
          </div>
        `;
      });
      (busses.uart || []).forEach(u => {
        busHtml += `
          <div class="bus-item">
            <div class="bus-header"><span><i class="fa-solid fa-arrow-right-arrow-left"></i> UART '${u.alias}'</span> <span>${u.baud}</span></div>
            <div class="bus-detail">TX:${u.tx} RX:${u.rx} • ${u.task_id}</div>
          </div>
        `;
      });

      busListEl.innerHTML = busHtml || '<div style="font-size: 0.75rem; color: var(--text-muted);">Нет настроенных шин</div>';
    }
  } catch (e) {
    console.error('Digital Twin error:', e);
  }
}

async function loadTaskIntoEditor(taskId) {
  const filename = taskId.endsWith('.js') ? taskId : `${taskId}.js`;
  const names = scriptFiles.map(f => typeof f === 'object' ? f.filename : f);
  if (!names.includes(filename)) {
    scriptFiles.push({ filename, description: '', size: 0 });
  }
  selectScript(filename);
}

async function unloadTask(taskId) {
  if (!confirm(`Выгрузить задачу '${taskId}' из RAM чипа?`)) return;
  log(`🛑 Выгрузка задачи '${taskId}' из памяти микропроцессора...`);
  try {
    const resp = await fetch(`/api/nodes/${currentNodeId}/tasks/${taskId}`, { method: 'DELETE' });
    if (resp.ok) {
      log(`✅ Задача '${taskId}' остановлена и выгружена из RAM.`);
      await refreshDigitalTwin();
    } else {
      log(`❌ Ошибка выгрузки задачи '${taskId}'`);
    }
  } catch (e) {
    log(`❌ Ошибка: ${e}`);
  }
}

async function fetchScriptsList() {
  try {
    const resp = await fetch('/api/scripts');
    if (resp.ok) {
      scriptFiles = await resp.json();
      const countBadge = document.getElementById('fileCountBadge');
      if (countBadge) countBadge.innerText = scriptFiles.length;
      const names = scriptFiles.map(f => typeof f === 'object' ? f.filename : f);
      if (names.length > 0) {
        if (!activeFileName || !names.includes(activeFileName)) {
          if (names.includes('rgb_rainbow.js')) {
            activeFileName = 'rgb_rainbow.js';
          } else {
            activeFileName = names[0];
          }
        }
        const badgeText = document.getElementById('activeFileNameText');
        if (badgeText) badgeText.innerText = activeFileName;
        await loadScriptContent(activeFileName);
      }
    }
  } catch (e) {
    log(`❌ Ошибка загрузки списка скриптов: ${e}`);
  }
}

// Connect WebSocket
function initWebSocket() {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${wsProtocol}//${window.location.host}/ws/telemetry`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    const dot = document.getElementById('wsDot');
    const txt = document.getElementById('wsText');
    if (dot) dot.style.background = '#34d399';
    if (txt) txt.innerText = 'Подключено';
    log('WebSocket подключен к RWP телеметрии.');
  };

  ws.onclose = () => {
    const dot = document.getElementById('wsDot');
    const txt = document.getElementById('wsText');
    if (dot) dot.style.background = '#ef4444';
    if (txt) txt.innerText = 'Отключено';
    setTimeout(initWebSocket, 3000);
  };

  ws.onmessage = (event) => {
    try {
      const nodes = JSON.parse(event.data);
      const node = nodes[currentNodeId] || Object.values(nodes)[0];
      if (node && node.online && node.telemetry) {
        const t = node.telemetry;
        if (t.system) {
          const valCpu = document.getElementById('valCpu');
          const fillCpu = document.getElementById('fillCpu');
          if (valCpu) valCpu.innerText = `${t.system.cpu_usage_pct}%`;
          if (fillCpu) fillCpu.style.width = `${t.system.cpu_usage_pct}%`;
        }
        if (t.memory) {
          const valHeap = document.getElementById('valHeap');
          const valHeapUsed = document.getElementById('valHeapUsed');
          if (valHeap) valHeap.innerText = `${t.memory.free_heap_kb} KB`;
          if (valHeapUsed) valHeapUsed.innerText = `Used: ${t.memory.used_heap_kb} KB`;
        }
        if (t.wifi) {
          const valRssi = document.getElementById('valRssi');
          const valChannel = document.getElementById('valChannel');
          const valLatency = document.getElementById('valLatency');
          if (valRssi) valRssi.innerText = `${t.wifi.rssi_dbm} dBm`;
          if (valChannel) valChannel.innerText = `Ch: ${t.wifi.channel}`;
          if (valLatency) valLatency.innerText = `${t.wifi.latency_ms} ms`;
        }
      }
    } catch (e) {
      console.error(e);
    }
  };
}

// Robust bootstrap
function bootstrap() {
  logEl = document.getElementById('consoleLog');
  initEditor();
  fetchScriptsList();
  refreshDigitalTwin();
  initWebSocket();
  setInterval(refreshDigitalTwin, 2500);
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}