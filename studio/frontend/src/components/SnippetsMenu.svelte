<script lang="ts">
  import { SNIPPET_CATEGORIES, type SnippetOption } from '../lib/snippets';

  let { onInsertSnippet, showLineNumbers, onToggleLineNumbers }: {
    onInsertSnippet: (code: string) => void;
    showLineNumbers: boolean;
    onToggleLineNumbers: () => void;
  } = $props();

  let openCategory = $state<string | null>(null);

  function toggleCategory(title: string, e: MouseEvent) {
    e.stopPropagation();
    openCategory = openCategory === title ? null : title;
  }

  function handleSelect(snippet: SnippetOption) {
    onInsertSnippet(snippet.code);
    openCategory = null;
  }

  function closeAll() {
    openCategory = null;
  }
</script>

<svelte:window onclick={closeAll} />

<div class="h-10 bg-[#0c1322] border-b border-[#1e293b] px-3 flex items-center justify-between shrink-0 select-none text-xs">
  <div class="flex items-center gap-2">
    <span class="text-slate-400 font-medium mr-1 text-xs">Сниппеты:</span>

    {#each SNIPPET_CATEGORIES as cat}
      <div class="relative">
        <button
          onclick={(e) => toggleCategory(cat.title, e)}
          class="flex items-center gap-1.5 bg-[#1e293b] hover:bg-[#334155] text-slate-200 hover:text-white px-2.5 py-1 rounded transition cursor-pointer text-xs font-medium {openCategory === cat.title ? 'border-sky-500 text-sky-300 bg-[#334155]' : 'border border-[#334155]'}"
        >
          <i class="fa-solid {cat.icon} {cat.color}"></i>
          <span>{cat.title}</span>
          <i class="fa-solid fa-chevron-down text-xs text-slate-400"></i>
        </button>

        {#if openCategory === cat.title}
          <div
            onclick={(e) => e.stopPropagation()}
            class="absolute top-full left-0 mt-1 w-72 bg-[#0f172a] border border-[#1e293b] rounded-lg shadow-2xl py-1.5 z-50 flex flex-col"
          >
            {#each cat.items as item}
              <button
                onclick={() => handleSelect(item)}
                class="flex items-center gap-2.5 px-3 py-2 text-left hover:bg-[#1e293b] text-slate-300 hover:text-sky-300 transition text-xs cursor-pointer"
              >
                <i class="fa-solid {item.icon} w-4 text-slate-400"></i>
                <span class="flex-1 truncate font-medium">{item.label}</span>
              </button>
            {/each}
          </div>
        {/if}
      </div>
    {/each}
  </div>

  <div>
    <button
      onclick={onToggleLineNumbers}
      class="flex items-center gap-1.5 bg-[#1e293b] hover:bg-[#334155] border px-2.5 py-1 rounded text-xs font-medium transition cursor-pointer {showLineNumbers ? 'border-sky-500 text-sky-400' : 'border-[#334155] text-slate-400'}"
      title="Переключить номера строк"
    >
      <i class="fa-solid fa-list-ol text-xs"></i>
      <span>Строки</span>
    </button>
  </div>
</div>
