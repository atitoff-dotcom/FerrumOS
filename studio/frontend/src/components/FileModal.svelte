<script lang="ts">
  import type { ScriptItem } from '../lib/api';

  let {
    open = false,
    scripts = [],
    activeFileName = '',
    onSelectScript,
    onDeleteScript,
    onCreateNew,
    onClose
  }: {
    open: boolean;
    scripts: ScriptItem[];
    activeFileName: string;
    onSelectScript: (filename: string) => void;
    onDeleteScript: (filename: string) => void;
    onCreateNew: () => void;
    onClose: () => void;
  } = $props();

  let searchQuery = $state('');
  let searchInput = $state<HTMLInputElement | null>(null);

  let filteredScripts = $derived(
    scripts.filter((s) => {
      const q = searchQuery.toLowerCase().trim();
      return s.filename.toLowerCase().includes(q) || (s.description || '').toLowerCase().includes(q);
    })
  );

  $effect(() => {
    if (open) {
      searchQuery = '';
      setTimeout(() => searchInput?.focus(), 50);
    }
  });

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onClose();
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <div
    class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-150"
    onclick={onClose}
    role="presentation"
  >
    <div
      class="bg-[#0f172a] border border-[#1e293b] rounded-xl w-[580px] max-w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden"
      onclick={(e) => e.stopPropagation()}
      role="dialog"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 bg-[#131d2e] border-b border-[#1e293b]">
        <div class="flex items-center gap-2.5 font-bold text-sky-400 text-base">
          <i class="fa-solid fa-folder-open text-lg"></i>
          <span>Менеджер скриптов FerrumOS</span>
        </div>
        <button
          onclick={onClose}
          class="text-slate-400 hover:text-rose-400 text-lg transition cursor-pointer"
        >
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <!-- Search Input -->
      <div class="p-4 border-b border-[#1e293b] bg-[#0c1322]">
        <div class="relative">
          <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3 text-slate-500 text-sm"></i>
          <input
            bind:this={searchInput}
            bind:value={searchQuery}
            type="text"
            placeholder="Поиск скрипта по названию или описанию..."
            class="w-full bg-[#070a12] border border-[#1e293b] focus:border-sky-500 rounded-lg pl-9 pr-3.5 py-2 text-sm text-white outline-none transition"
          />
        </div>
      </div>

      <!-- File List -->
      <div class="p-3.5 overflow-y-auto flex-1 flex flex-col gap-2 max-h-[380px]">
        {#if filteredScripts.length === 0}
          <div class="text-center py-8 text-slate-500 text-sm">
            Скрипты не найдены
          </div>
        {:else}
          {#each filteredScripts as item}
            {@const isActive = item.filename === activeFileName}
            <div
              class="flex items-center justify-between p-3 rounded-lg border transition cursor-pointer {isActive ? 'bg-sky-500/10 border-sky-500/40 shadow-sm' : 'bg-[#1e293b]/70 hover:bg-[#1e293b] border-transparent hover:border-slate-700'}"
              ondblclick={() => { onSelectScript(item.filename); onClose(); }}
            >
              <div class="flex flex-col gap-1 min-w-0 flex-1 pr-3">
                <div class="flex items-center gap-2 font-semibold text-sm text-slate-100">
                  <i class="fa-brands fa-js text-base {isActive ? 'text-sky-400' : 'text-amber-400'}"></i>
                  <span class="font-mono">{item.filename}</span>
                  {#if isActive}
                    <span class="text-xs bg-sky-500/20 text-sky-400 rounded px-2 py-0.5 font-medium">Текущий</span>
                  {/if}
                </div>
                {#if item.description}
                  <div class="text-xs text-slate-400 pl-6 truncate" title={item.description}>
                    {item.description}
                  </div>
                {/if}
              </div>

              <div class="flex items-center gap-2">
                <button
                  onclick={(e) => { e.stopPropagation(); onSelectScript(item.filename); onClose(); }}
                  class="bg-sky-600/80 hover:bg-sky-500 text-white rounded px-2.5 py-1 text-xs font-semibold transition cursor-pointer"
                  title="Открыть в редакторе"
                >
                  Открыть
                </button>
                <button
                  onclick={(e) => { e.stopPropagation(); onDeleteScript(item.filename); }}
                  class="text-slate-500 hover:text-rose-400 p-1 transition cursor-pointer"
                  title="Удалить файл"
                >
                  <i class="fa-solid fa-trash text-sm"></i>
                </button>
              </div>
            </div>
          {/each}
        {/if}
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between px-5 py-3.5 bg-[#090d16] border-t border-[#1e293b]">
        <span class="text-xs text-slate-400">
          Всего скриптов: <strong class="text-white">{scripts.length}</strong>
        </span>
        <button
          onclick={() => { onCreateNew(); onClose(); }}
          class="flex items-center gap-2 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white rounded-lg px-4 py-1.5 text-sm font-semibold transition cursor-pointer shadow-lg shadow-sky-900/20"
        >
          <i class="fa-solid fa-plus text-xs"></i>
          <span>Создать новый скрипт</span>
        </button>
      </div>
    </div>
  </div>
{/if}
