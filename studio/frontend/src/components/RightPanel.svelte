<script lang="ts">
  import type { DigitalTwinState } from '../lib/api';

  let {
    twin = null,
    logs = [],
    onClearLogs
  }: {
    twin: DigitalTwinState | null;
    logs: string[];
    onClearLogs: () => void;
  } = $props();

  let logContainer = $state<HTMLDivElement | null>(null);

  $effect(() => {
    if (logs.length > 0 && logContainer) {
      logContainer.scrollTop = logContainer.scrollHeight;
    }
  });
</script>

<aside class="w-80 bg-[#0c1322] border-l border-[#1e293b] flex flex-col shrink-0 min-h-0">
  <!-- Section: Pinout Matrix Grid (0..23) -->
  <div class="p-3 border-b border-[#1e293b] bg-[#090d16] flex items-center justify-between">
    <div class="flex items-center gap-2 font-bold text-sm text-slate-200">
      <i class="fa-solid fa-border-all text-sky-400 text-base"></i>
      <span>Матрица GPIO (ESP32-C6)</span>
    </div>
    <span class="text-xs text-slate-400 font-mono">24 Pins</span>
  </div>

  <div class="p-3 border-b border-[#1e293b]">
    <div class="grid grid-cols-8 gap-1.5">
      {#each (twin?.pin_matrix || []).filter(p => p.pin <= 23) as p}
        {@const isClaimed = p.status === 'claimed'}
        {@const isBus = p.status === 'bus'}
        {@const isForbidden = p.status === 'forbidden'}
        <div
          class="flex flex-col items-center justify-center p-1.5 rounded border text-xs font-mono transition cursor-pointer hover:scale-105 {isClaimed ? 'border-sky-500 bg-sky-500/20 text-sky-300 font-bold shadow-sm' : isBus ? 'border-purple-500 bg-purple-500/20 text-purple-300 font-bold shadow-sm' : isForbidden ? 'border-red-500/50 bg-red-500/10 text-red-400 opacity-60' : 'border-[#1e293b] bg-[#111a2e] text-slate-300'}"
          title="GPIO {p.pin}: {p.owner} ({p.status})"
        >
          <span class="font-bold">{p.pin}</span>
          <span class="text-xs opacity-75 truncate max-w-full font-sans scale-90">{p.status === 'claimed' ? 'used' : p.status === 'free' ? 'free' : p.status}</span>
        </div>
      {/each}
    </div>
  </div>

  <!-- Section: Shared Busses -->
  <div class="p-3 border-b border-[#1e293b] bg-[#090d16] flex items-center justify-between">
    <div class="flex items-center gap-2 font-bold text-sm text-purple-300">
      <i class="fa-solid fa-circle-nodes text-base"></i>
      <span>Общие шины (Busses)</span>
    </div>
  </div>

  <div class="p-3 border-b border-[#1e293b] flex flex-col gap-2 max-h-40 overflow-y-auto text-xs font-mono">
    {#if !twin?.shared_busses || (
      (!twin.shared_busses.i2c || twin.shared_busses.i2c.length === 0) &&
      (!twin.shared_busses.spi || twin.shared_busses.spi.length === 0) &&
      (!twin.shared_busses.uart || twin.shared_busses.uart.length === 0)
    )}
      <div class="text-slate-500 text-xs text-center py-2">Нет настроенных шин</div>
    {:else}
      {#each (twin.shared_busses.i2c || []) as i2c}
        <div class="bg-[#111a2e] border-l-2 border-purple-500 rounded p-2 flex flex-col gap-1 text-xs">
          <div class="flex justify-between text-purple-300 font-semibold">
            <span>I2C '{i2c.alias}'</span>
            <span>{i2c.sda}/{i2c.scl}</span>
          </div>
          <div class="text-xs text-slate-400 truncate">
            Dev: {(i2c.devices || []).join(', ')} • {i2c.task_id}
          </div>
        </div>
      {/each}

      {#each (twin.shared_busses.spi || []) as spi}
        <div class="bg-[#111a2e] border-l-2 border-sky-500 rounded p-2 flex flex-col gap-1 text-xs">
          <div class="flex justify-between text-sky-300 font-semibold">
            <span>SPI '{spi.alias}'</span>
            <span>CS:{spi.cs}</span>
          </div>
          <div class="text-xs text-slate-400 truncate">
            MOSI:{spi.mosi} • {spi.task_id}
          </div>
        </div>
      {/each}
    {/if}
  </div>

  <!-- Section: Console Output Log -->
  <div class="p-3 border-b border-[#1e293b] bg-[#090d16] flex items-center justify-between">
    <div class="flex items-center gap-2 font-bold text-sm text-slate-200">
      <i class="fa-solid fa-terminal text-sky-400 text-base"></i>
      <span>Консоль событий</span>
    </div>
    <button
      onclick={onClearLogs}
      class="text-slate-400 hover:text-white text-xs transition cursor-pointer px-2 py-0.5 rounded hover:bg-[#1e293b]"
    >
      Очистить
    </button>
  </div>

  <div
    bind:this={logContainer}
    class="flex-1 p-3 bg-[#050811] overflow-y-auto font-mono text-xs leading-relaxed flex flex-col gap-1.5 text-slate-200"
  >
    {#if logs.length === 0}
      <div class="text-slate-600 text-center py-4">Лог пуст</div>
    {:else}
      {#each logs as l}
        <div class="break-words">{@html l}</div>
      {/each}
    {/if}
  </div>
</aside>
