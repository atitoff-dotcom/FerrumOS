<script lang="ts">
  let {
    nodeId = 'c6_supermini_main',
    activeFileName = 'task.js',
    totalFiles = 0,
    isUnsaved = false,
    isOnline = false,
    onOpenModal,
    onCloseFile,
    onSave,
    onNewFile,
    onPreFlight,
    onDeploy,
    onTestMqtt
  }: {
    nodeId?: string;
    activeFileName?: string;
    totalFiles?: number;
    isUnsaved?: boolean;
    isOnline?: boolean;
    onOpenModal: () => void;
    onCloseFile: () => void;
    onSave: () => void;
    onNewFile: () => void;
    onPreFlight: () => void;
    onDeploy: () => void;
    onTestMqtt: () => void;
  } = $props();

  let mqttTesting = $state(false);
  let mqttSuccess = $state<boolean | null>(null);

  async function handleMqtt() {
    mqttTesting = true;
    try {
      await onTestMqtt();
      mqttSuccess = true;
    } catch {
      mqttSuccess = false;
    } finally {
      setTimeout(() => {
        mqttTesting = false;
        mqttSuccess = null;
      }, 4000);
    }
  }
</script>

<header class="h-14 bg-[#090d16] border-b border-[#1e293b] flex items-center justify-between px-4 shrink-0 gap-4">
  <!-- Brand & Node Status -->
  <div class="flex items-center gap-3">
    <div class="flex items-center gap-2.5 font-bold text-base tracking-wide text-white">
      <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-sm font-black shadow-lg shadow-sky-500/20">
        Fe
      </div>
      <span>FerrumOS <span class="text-sky-400 font-normal text-xs">Studio 5.0</span></span>
    </div>

    <div class="h-5 w-px bg-[#1e293b]"></div>

    <!-- Active Node Badge -->
    <div class="flex items-center gap-2 bg-[#0c1322] border border-[#1e293b] rounded-full px-3 py-1 text-xs">
      {#if isOnline}
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="font-mono text-slate-200 font-medium">{nodeId}</span>
        <span class="text-xs bg-emerald-950/70 border border-emerald-700/50 text-emerald-400 font-mono rounded px-1.5 py-0.5">Online</span>
      {:else}
        <span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
        <span class="font-mono text-slate-400 font-medium">{nodeId}</span>
        <span class="text-xs bg-rose-950/70 border border-rose-800/50 text-rose-400 font-mono rounded px-1.5 py-0.5">Offline</span>
      {/if}
    </div>
  </div>

  <!-- Center Active File Switcher & Tab -->
  <div class="flex items-center gap-2.5">
    <button
      onclick={onOpenModal}
      class="flex items-center gap-2 bg-[#0f172a] hover:bg-[#1e293b] border border-sky-500/30 hover:border-sky-400 text-sky-400 rounded-md px-3.5 py-1.5 text-sm font-medium transition cursor-pointer shadow-sm"
      title="Открыть менеджер файлов (Ctrl+O)"
    >
      <i class="fa-solid fa-folder-open"></i>
      <span>Открыть скрипт ({totalFiles})</span>
    </button>

    {#if activeFileName}
      <div class="flex items-center gap-2 bg-[#050811] border border-[#1e293b] rounded-md px-3.5 py-1.5 text-sm font-medium">
        <i class="fa-brands fa-js text-amber-400 text-base"></i>
        <span class="font-mono text-slate-100 font-semibold">{activeFileName}</span>
        {#if isUnsaved}
          <span class="text-amber-400 text-xs" title="Несохраненные изменения">●</span>
        {/if}
        <button
          onclick={(e) => { e.stopPropagation(); onCloseFile(); }}
          class="ml-1 text-slate-400 hover:text-rose-400 p-0.5 rounded transition cursor-pointer"
          title="Закрыть вкладку"
        >
          <i class="fa-solid fa-xmark text-sm"></i>
        </button>
      </div>
    {/if}
  </div>

  <!-- Action Controls -->
  <div class="flex items-center gap-2">
    <button
      onclick={onNewFile}
      class="flex items-center gap-1.5 bg-[#1e293b] hover:bg-slate-700 text-slate-200 rounded-md px-3 py-1.5 text-sm font-medium transition cursor-pointer"
      title="Создать новый файл"
    >
      <i class="fa-solid fa-plus text-sky-400"></i>
      <span>Новый</span>
    </button>

    <button
      onclick={onSave}
      class="flex items-center gap-1.5 bg-[#1e293b] hover:bg-slate-700 text-slate-200 rounded-md px-3 py-1.5 text-sm font-medium transition cursor-pointer"
      title="Сохранить на диск (Ctrl+S)"
    >
      <i class="fa-solid fa-floppy-disk text-slate-400"></i>
      <span>Сохранить</span>
    </button>

    <button
      onclick={onPreFlight}
      class="flex items-center gap-1.5 bg-sky-950/60 hover:bg-sky-900/80 border border-sky-600/40 text-sky-300 rounded-md px-3.5 py-1.5 text-sm font-semibold transition cursor-pointer shadow-sm"
      title="Проверить коллизии пинов (F7)"
    >
      <i class="fa-solid fa-shield-halved text-sky-400"></i>
      <span>Проверить</span>
    </button>

    <button
      onclick={onDeploy}
      class="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-md px-4 py-1.5 text-sm font-bold transition cursor-pointer shadow-lg shadow-emerald-900/30"
      title="Мгновенный Hot-Swap в RAM чипа (Ctrl+Enter)"
    >
      <i class="fa-solid fa-bolt"></i>
      <span>Hot-Swap</span>
    </button>

    <div class="h-5 w-px bg-[#1e293b] mx-1"></div>

    <button
      onclick={handleMqtt}
      class="flex items-center gap-1.5 bg-[#1e293b] hover:bg-slate-700 border text-slate-200 rounded-md px-3 py-1.5 text-sm font-medium transition cursor-pointer {mqttSuccess === true ? 'border-emerald-500/50 text-emerald-400' : mqttSuccess === false ? 'border-red-500/50 text-red-400' : 'border-[#334155]'}"
      title="Проверить связь с MQTT брокером"
    >
      {#if mqttTesting}
        <i class="fa-solid fa-spinner fa-spin text-sky-400"></i>
      {:else if mqttSuccess === true}
        <i class="fa-solid fa-check text-emerald-400"></i>
      {:else if mqttSuccess === false}
        <i class="fa-solid fa-xmark text-red-400"></i>
      {:else}
        <i class="fa-solid fa-tower-broadcast text-sky-400"></i>
      {/if}
      <span>MQTT</span>
    </button>
  </div>
</header>
