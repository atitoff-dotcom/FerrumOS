<script lang="ts">
  import { onMount } from 'svelte';
  import Header from './components/Header.svelte';
  import SnippetsMenu from './components/SnippetsMenu.svelte';
  import Editor from './components/Editor.svelte';
  import LeftPanel from './components/LeftPanel.svelte';
  import RightPanel from './components/RightPanel.svelte';
  import FileModal from './components/FileModal.svelte';
  import {
    fetchScripts,
    fetchScriptCode,
    saveScript,
    deleteScript,
    fetchDigitalTwin,
    deployScript,
    validateScriptContext,
    commitFlash,
    unloadTask,
    testMqtt,
    type ScriptItem,
    type DigitalTwinState
  } from './lib/api';

  const nodeId = 'c6_supermini_main';

  let scripts = $state<ScriptItem[]>([]);
  let activeFileName = $state('task.js');
  let code = $state('');
  let isUnsaved = $state(false);
  let showLineNumbers = $state(false);
  let fileModalOpen = $state(false);

  let isNodeOnline = $state(false);
  let twinState = $state<DigitalTwinState | null>(null);
  let telemetryState = $state<any>(null);
  let logs = $state<string[]>([]);

  let editorComponent = $state<any>(null);

  function log(msg: string) {
    const ts = new Date().toLocaleTimeString();
    logs = [...logs, `<span class="text-slate-500">[${ts}]</span> ${msg}`];
  }

  async function loadScriptsList() {
    try {
      scripts = await fetchScripts();
      if (scripts.length > 0 && (!activeFileName || !scripts.some(s => s.filename === activeFileName))) {
        const defaultScript = scripts.find(s => s.filename === 'rgb_rainbow.js') || scripts[0];
        await switchScript(defaultScript.filename);
      }
    } catch (e: any) {
      log(`<span class="text-red-400">❌ Ошибка загрузки списка: ${e.message}</span>`);
    }
  }

  async function switchScript(filename: string) {
    if (activeFileName === filename && code) return;
    if (isUnsaved) {
      if (!confirm(`Файл '${activeFileName}' содержит несохраненные изменения. Переключить?`)) {
        return;
      }
    }
    activeFileName = filename;
    try {
      const scriptCode = await fetchScriptCode(filename);
      code = scriptCode;
      editorComponent?.setEditorContent(scriptCode);
      isUnsaved = false;
      log(`Загружен файл <strong class="text-sky-300">'${filename}'</strong> в редактор.`);
    } catch (e: any) {
      log(`<span class="text-red-400">❌ Ошибка чтения '${filename}': ${e.message}</span>`);
    }
  }

  async function handleSave() {
    if (!activeFileName) return;
    try {
      await saveScript(activeFileName, code);
      isUnsaved = false;
      log(`💾 Файл <strong class="text-emerald-400">'${activeFileName}'</strong> сохранен на диск.`);
      await loadScriptsList();
    } catch (e: any) {
      log(`<span class="text-red-400">❌ Ошибка сохранения: ${e.message}</span>`);
    }
  }

  async function handleNewFile() {
    const name = prompt('Введите имя нового файла:', 'task.js');
    if (!name) return;
    const filename = name.endsWith('.js') ? name : `${name}.js`;
    const initialCode = '// FerrumOS JavaScript Task\nprint(">>> Running ' + filename + '...");\n\nwhile (true) {\n    rgb.set(8, 0, 255, 0);\n    delay(500);\n    rgb.set(8, 0, 0, 0);\n    delay(500);\n}\n';
    try {
      await saveScript(filename, initialCode);
      log(`✨ Создан файл <strong class="text-emerald-400">'${filename}'</strong>!`);
      await loadScriptsList();
      await switchScript(filename);
      fileModalOpen = false;
    } catch (e: any) {
      log(`<span class="text-red-400">❌ Ошибка создания: ${e.message}</span>`);
    }
  }

  async function handleDeleteFile(filename: string) {
    if (!confirm(`Удалить скрипт '${filename}'?`)) return;
    try {
      await deleteScript(filename);
      log(`🗑️ Файл '${filename}' удален.`);
      await loadScriptsList();
      if (activeFileName === filename && scripts.length > 0) {
        await switchScript(scripts[0].filename);
      }
    } catch (e: any) {
      log(`<span class="text-red-400">❌ Ошибка удаления: ${e.message}</span>`);
    }
  }

  async function handlePreFlight() {
    const taskId = activeFileName.replace('.js', '');
    log(`🔍 Кросс-проверка <strong class="text-sky-300">'${taskId}'</strong> с задачами в RAM чипа...`);
    try {
      const res = await validateScriptContext(nodeId, taskId, code);
      if (res.valid) {
        log('✅ <strong class="text-emerald-400">Кросс-проверка пройдена!</strong> Коллизий пинов и шин не обнаружено.');
      } else {
        log('⛔ <strong class="text-red-400">Ошибки коллизии ресурсов:</strong>');
        res.errors.forEach(e => log(`   • <span class="text-red-300">${e.message}</span>`));
      }
    } catch (e: any) {
      log(`<span class="text-red-400">❌ Ошибка проверки: ${e.message}</span>`);
    }
  }

  function handleCloseFile() {
    if (isUnsaved) {
      if (!confirm(`Файл '${activeFileName}' содержит несохраненные изменения. Закрыть?`)) {
        return;
      }
    }
    activeFileName = '';
    code = '';
    editorComponent?.setEditorContent('');
    isUnsaved = false;
    log('Вкладка закрыта.');
  }

  async function handleDeploy() {
    log(`🚀 Hot-Swap задачи <strong class="text-sky-300">'${activeFileName}'</strong> в RAM ESP32-C6...`);
    try {
      await deployScript(nodeId, activeFileName, code);
      log(`✨ <strong class="text-emerald-400">Hot-Swap '${activeFileName}' успешен!</strong> Запущено в RAM микропроцессора.`);
      await refreshTwin();
    } catch (e: any) {
      log(`<span class="text-red-400">❌ Ошибка деплоя: ${e.message}</span>`);
    }
  }

  async function handleCommitFlash() {
    log('💾 Фиксация задач в энергонезависимую Flash-память (0x300000)...');
    try {
      const res = await commitFlash(nodeId);
      log(`💾 <strong class="text-sky-300">Сохранено ${res.saved_count} задач во Flash!</strong>`);
      await refreshTwin();
    } catch (e: any) {
      log(`<span class="text-red-400">❌ Ошибка записи во Flash: ${e.message}</span>`);
    }
  }

  async function handleUnloadTask(taskId: string) {
    if (!confirm(`Выгрузить задачу '${taskId}' из RAM чипа?`)) return;
    log(`🛑 Выгрузка задачи '${taskId}' из памяти микропроцессора...`);
    try {
      await unloadTask(nodeId, taskId);
      log(`✅ Задача '${taskId}' остановлена и выгружена из RAM.`);
      await refreshTwin();
    } catch (e: any) {
      log(`<span class="text-red-400">❌ Ошибка выгрузки: ${e.message}</span>`);
    }
  }

  async function refreshTwin() {
    try {
      twinState = await fetchDigitalTwin(nodeId);
    } catch (e) {
      console.error('Digital Twin error:', e);
    }
  }

  function initWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/telemetry`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => log('WebSocket подключен к RWP телеметрии.');
    ws.onclose = () => {
      isNodeOnline = false;
      telemetryState = null;
      setTimeout(initWebSocket, 3000);
    };
    ws.onmessage = (event) => {
      try {
        const nodes = JSON.parse(event.data);
        const node = nodes[nodeId] || Object.values(nodes)[0];
        if (node) {
          isNodeOnline = !!node.online;
          telemetryState = node.online ? node.telemetry : null;
        } else {
          isNodeOnline = false;
          telemetryState = null;
        }
      } catch (e) {
        console.error(e);
      }
    };
  }

  onMount(() => {
    loadScriptsList();
    refreshTwin();
    initWebSocket();
    const timer = setInterval(refreshTwin, 2500);
    return () => clearInterval(timer);
  });
</script>

<div class="h-screen w-screen flex flex-col bg-[#070a12] text-slate-100 overflow-hidden font-sans select-none">
  <!-- Top Navigation Header -->
  <Header
    {nodeId}
    {activeFileName}
    totalFiles={scripts.length}
    {isUnsaved}
    isOnline={isNodeOnline}
    onOpenModal={() => (fileModalOpen = true)}
    onCloseFile={handleCloseFile}
    onSave={handleSave}
    onNewFile={handleNewFile}
    onPreFlight={handlePreFlight}
    onDeploy={handleDeploy}
    onTestMqtt={() => testMqtt(nodeId)}
  />

  <!-- Main 3-Column Studio Layout -->
  <div class="flex-1 flex min-h-0">
    <!-- Left: Fleet, Tasks in RAM, Telemetry -->
    <LeftPanel
      twin={twinState}
      telemetry={telemetryState}
      isOnline={isNodeOnline}
      onLoadTask={switchScript}
      onUnloadTask={handleUnloadTask}
      onCommitTask={() => handleCommitFlash()}
    />

    <!-- Center: Snippets Bar & Code Editor -->
    <main class="flex-1 flex flex-col min-w-0 bg-[#050811]">
      <SnippetsMenu
        onInsertSnippet={(snippet) => editorComponent?.insertSnippetText(snippet)}
        {showLineNumbers}
        onToggleLineNumbers={() => (showLineNumbers = !showLineNumbers)}
      />

      <Editor
        bind:this={editorComponent}
        bind:code
        bind:isUnsaved
        {showLineNumbers}
        onSave={handleSave}
        onDeploy={handleDeploy}
        onPreFlight={handlePreFlight}
        onOpenModal={() => (fileModalOpen = true)}
      />
    </main>

    <!-- Right: Pinout Matrix, Busses, Console Output -->
    <RightPanel
      twin={twinState}
      {logs}
      onClearLogs={() => (logs = [])}
    />
  </div>

  <!-- Searchable File Manager Dialog -->
  <FileModal
    open={fileModalOpen}
    {scripts}
    {activeFileName}
    onSelectScript={switchScript}
    onDeleteScript={handleDeleteFile}
    onCreateNew={handleNewFile}
    onClose={() => (fileModalOpen = false)}
  />
</div>
