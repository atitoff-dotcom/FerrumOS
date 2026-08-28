<script lang="ts">
  import type { DigitalTwinState } from '../lib/api';

  let {
    twin = null,
    telemetry = null,
    isOnline = false,
    onLoadTask,
    onUnloadTask,
    onCommitTask
  }: {
    twin: DigitalTwinState | null;
    telemetry: any;
    isOnline?: boolean;
    onLoadTask: (taskId: string) => void;
    onUnloadTask: (taskId: string) => void;
    onCommitTask: (taskId: string) => void;
  } = $props();

  let activeTasksList = $derived(Object.values(twin?.active_tasks || {}));
  let openMenuTaskId = $state<string | null>(null);

  function closeMenu() {
    openMenuTaskId = null;
  }
</script>

<svelte:window onclick={closeMenu} />

<aside class="w-80 bg-[#0c1322] border-r border-[#1e293b] flex flex-col shrink-0 min-h-0">
  <!-- Section: Active Tasks in RAM -->
  <div class="p-3 border-b border-[#1e293b] flex items-center justify-between bg-[#090d16]">
    <div class="flex items-center gap-2 font-bold text-sm text-slate-200">
      <i class="fa-solid fa-microchip text-sky-400 text-base"></i>
      <span>Задачи на контроллере</span>
    </div>
    <span class="bg-[#1e293b] text-sky-300 font-mono text-xs rounded px-2.5 py-0.5 font-semibold">
      {activeTasksList.length}
    </span>
  </div>

  <div class="flex-1 p-3 overflow-y-auto flex flex-col gap-2.5 min-h-0">
    {#if activeTasksList.length === 0}
      <div class="text-center py-8 text-slate-500 text-sm">
        Нет активных задач в памяти чипа
      </div>
    {:else}
      {#each activeTasksList as task}
        {@const taskName = task.task_id || task.id}
        {@const isFlash = task.storage !== 'ram' && task.persisted !== false}
        <div class="bg-[#111a2e] border border-[#1e293b] hover:border-slate-700 rounded-lg p-3 flex flex-col gap-2 transition shadow-sm">
          <div class="flex items-center justify-between relative">
            <div class="flex items-center gap-2 font-semibold text-sm text-slate-100 min-w-0 pr-1">
              <i class="fa-solid fa-play text-emerald-400 text-xs shrink-0"></i>
              <span class="font-mono truncate">{taskName}</span>
              {#if isFlash}
                <span class="text-xs bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded px-1.5 py-0.5 shrink-0 font-sans font-medium" title="Сохранено во Flash (автозапуск)">
                  Flash
                </span>
              {:else}
                <span class="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded px-1.5 py-0.5 shrink-0 font-sans font-medium" title="Временно в RAM (не сохранено во Flash)">
                  RAM
                </span>
              {/if}
            </div>

            <div class="flex items-center gap-1.5 shrink-0">
              <button
                onclick={() => onLoadTask(taskName)}
                class="text-slate-400 hover:text-sky-400 p-1.5 transition cursor-pointer"
                title="Открыть в редакторе"
              >
                <i class="fa-solid fa-code text-sm"></i>
              </button>

              <!-- 3-dots Context Menu Button -->
              <div class="relative">
                <button
                  onclick={(e) => { e.stopPropagation(); openMenuTaskId = openMenuTaskId === taskName ? null : taskName; }}
                  class="text-slate-400 hover:text-white p-1.5 hover:bg-[#1e293b] rounded transition cursor-pointer"
                  title="Действия с задачей"
                >
                  <i class="fa-solid fa-ellipsis-vertical text-sm"></i>
                </button>

                {#if openMenuTaskId === taskName}
                  <div
                    onclick={(e) => e.stopPropagation()}
                    class="absolute right-0 top-full mt-1 w-48 bg-[#0f172a] border border-[#1e293b] rounded-lg shadow-2xl py-1.5 z-50 flex flex-col text-sm"
                  >
                    <button
                      onclick={() => { onCommitTask(taskName); openMenuTaskId = null; }}
                      class="flex items-center gap-2.5 px-3 py-2 text-left text-slate-300 hover:text-purple-300 hover:bg-[#1e293b] transition cursor-pointer font-medium"
                    >
                      <i class="fa-solid fa-floppy-disk text-purple-400 w-4"></i>
                      <span>Записать во Flash</span>
                    </button>
                    <div class="h-px bg-[#1e293b] my-1"></div>
                    <button
                      onclick={() => { onUnloadTask(taskName); openMenuTaskId = null; }}
                      class="flex items-center gap-2.5 px-3 py-2 text-left text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition cursor-pointer font-medium"
                    >
                      <i class="fa-solid fa-stop text-rose-400 w-4"></i>
                      <span>Выгрузить</span>
                    </button>
                  </div>
                {/if}
              </div>
            </div>
          </div>

          <div class="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>{task.frb_size ?? task.rhb_size ?? task.size ?? task.js_size ?? 0} B</span>
            <span class="text-emerald-400 font-medium">● Active</span>
          </div>

          <!-- Pin Badges -->
          <div class="flex flex-wrap gap-1.5 mt-0.5">
            {#if Object.keys(task.pins || {}).length === 0}
              <span class="text-xs text-slate-500 bg-[#070a12] rounded px-2 py-0.5">No GPIO</span>
            {:else}
              {#each Object.entries(task.pins) as [pin, tag]}
                <span class="text-xs text-sky-300 bg-sky-950/60 border border-sky-800/50 rounded px-2 py-0.5 font-mono">
                  GPIO {pin} ({tag})
                </span>
              {/each}
            {/if}
          </div>
        </div>
      {/each}
    {/if}
  </div>

  <!-- Section: Live Telemetry Gauges -->
  <div class="p-3.5 border-t border-[#1e293b] bg-[#090d16] flex flex-col gap-3">
    <div class="flex items-center justify-between text-sm font-bold text-slate-300">
      <span class="flex items-center gap-2">
        <i class="fa-solid fa-chart-line {isOnline ? 'text-emerald-400' : 'text-slate-500'}"></i>
        <span>RWP Телеметрия</span>
      </span>
      {#if isOnline && telemetry}
        <span class="text-xs text-emerald-400 flex items-center gap-1.5 font-mono">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Live
        </span>
      {:else}
        <span class="text-xs text-rose-400 flex items-center gap-1.5 font-mono">
          <span class="w-2 h-2 rounded-full bg-rose-500"></span> Offline
        </span>
      {/if}
    </div>

    <!-- CPU Usage Gauge -->
    <div class="flex flex-col gap-1 text-xs">
      <div class="flex justify-between text-slate-300 font-mono">
        <span>CPU Load</span>
        <span class="text-white font-bold">{isOnline && telemetry?.system?.cpu_usage_pct !== undefined ? `${telemetry.system.cpu_usage_pct}%` : '—'}</span>
      </div>
      <div class="h-2 bg-[#1e293b] rounded-full overflow-hidden">
        <div
          class="h-full bg-gradient-to-r from-sky-400 to-indigo-500 transition-all duration-300"
          style="width: {isOnline && telemetry?.system?.cpu_usage_pct !== undefined ? `${telemetry.system.cpu_usage_pct}%` : '0%'}"
        ></div>
      </div>
    </div>

    <!-- Free Heap Gauge -->
    <div class="flex flex-col gap-1 text-xs">
      <div class="flex justify-between text-slate-300 font-mono">
        <span>Free Heap</span>
        <span class="text-emerald-400 font-bold">{isOnline && telemetry?.memory?.free_heap_kb !== undefined ? `${telemetry.memory.free_heap_kb} KB` : '—'}</span>
      </div>
      <div class="text-xs text-slate-500 font-mono">
        Used: {isOnline && telemetry?.memory?.used_heap_kb !== undefined ? `${telemetry.memory.used_heap_kb} KB` : '—'}
      </div>
    </div>

    <!-- Wi-Fi Stats -->
    <div class="grid grid-cols-2 gap-2 pt-2 border-t border-[#1e293b] text-xs font-mono">
      <div class="flex flex-col">
        <span class="text-slate-500">Wi-Fi RSSI</span>
        <span class="text-slate-200 font-semibold">{isOnline && telemetry?.wifi?.rssi_dbm !== undefined ? `${telemetry.wifi.rssi_dbm} dBm` : '—'}</span>
      </div>
      <div class="flex flex-col">
        <span class="text-slate-500">Задержка</span>
        <span class="text-slate-200 font-semibold">{isOnline && telemetry?.wifi?.latency_ms !== undefined ? `${telemetry.wifi.latency_ms} ms` : '—'}</span>
      </div>
    </div>
  </div>
</aside>
