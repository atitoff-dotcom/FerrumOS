<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  let {
    code = $bindable(''),
    showLineNumbers = false,
    isUnsaved = $bindable(false),
    onSave,
    onDeploy,
    onPreFlight,
    onOpenModal
  }: {
    code: string;
    showLineNumbers: boolean;
    isUnsaved: boolean;
    onSave: () => void;
    onDeploy: () => void;
    onPreFlight: () => void;
    onOpenModal: () => void;
  } = $props();

  let textareaEl = $state<HTMLTextAreaElement | null>(null);
  let editorInstance: any = null;
  let cursorLine = $state(1);
  let cursorCol = $state(1);

  let byteSize = $derived(new TextEncoder().encode(code).length);
  let estFrbSize = $derived(Math.max(16, Math.round(byteSize * 0.35)));

  export function insertSnippetText(snippet: string) {
    if (editorInstance) {
      const doc = editorInstance.getDoc();
      const cursor = doc.getCursor();
      doc.replaceRange(snippet, cursor);
      editorInstance.focus();
    } else if (textareaEl) {
      const start = textareaEl.selectionStart || 0;
      const end = textareaEl.selectionEnd || 0;
      code = code.substring(0, start) + snippet + code.substring(end);
      textareaEl.focus();
    }
  }

  export function setEditorContent(newCode: string) {
    if (editorInstance) {
      if (editorInstance.getValue() !== newCode) {
        editorInstance.setValue(newCode);
      }
    } else {
      code = newCode;
    }
  }

  onMount(() => {
    if (typeof (window as any).CodeMirror !== 'undefined' && textareaEl) {
      editorInstance = (window as any).CodeMirror.fromTextArea(textareaEl, {
        mode: 'javascript',
        theme: 'material-darker',
        lineNumbers: showLineNumbers,
        matchBrackets: true,
        autoCloseBrackets: true,
        tabSize: 4,
        indentUnit: 4,
        lineWrapping: false,
        extraKeys: {
          'Tab': (cm: any) => {
            if (cm.somethingSelected()) cm.indentSelection('add');
            else cm.replaceSelection('    ', 'end', '+input');
          },
          'Ctrl-S': () => onSave(),
          'Cmd-S': () => onSave(),
          'Ctrl-O': () => onOpenModal(),
          'Cmd-O': () => onOpenModal(),
          'Ctrl-Enter': () => onDeploy(),
          'Cmd-Enter': () => onDeploy(),
          'F7': () => onPreFlight()
        }
      });

      editorInstance.setValue(code);

      editorInstance.on('change', () => {
        const val = editorInstance.getValue();
        if (val !== code) {
          code = val;
          isUnsaved = true;
        }
      });

      editorInstance.on('cursorActivity', () => {
        const cur = editorInstance.getCursor();
        cursorLine = cur.line + 1;
        cursorCol = cur.ch + 1;
      });
    }
  });

  $effect(() => {
    if (editorInstance) {
      editorInstance.setOption('lineNumbers', showLineNumbers);
    }
  });

  onDestroy(() => {
    if (editorInstance) {
      editorInstance.toTextArea();
      editorInstance = null;
    }
  });
</script>

<div class="flex-1 flex flex-col min-h-0 bg-[#050811] relative">
  <!-- CodeMirror Container -->
  <div class="flex-1 min-h-0 relative overflow-hidden flex">
    <textarea
      bind:this={textareaEl}
      class="w-full h-full p-3 font-mono text-sm bg-[#050811] text-slate-100 resize-none outline-none"
    ></textarea>
  </div>

  <!-- Status Bar -->
  <div class="h-6 bg-[#090d16] border-t border-[#1e293b] px-3 flex items-center justify-between text-[11px] text-slate-500 shrink-0 font-mono select-none">
    <div class="flex items-center gap-4">
      <span class="flex items-center gap-1">
        <i class="fa-solid fa-location-crosshairs text-slate-400"></i>
        <span>Ln {cursorLine}, Col {cursorCol}</span>
      </span>
      <span class="flex items-center gap-1">
        <i class="fa-regular fa-file-code text-slate-400"></i>
        <span>{byteSize} B</span>
      </span>
      <span class="flex items-center gap-1 text-sky-400">
        <i class="fa-solid fa-microchip"></i>
        <span>~{estFrbSize} B FRB</span>
      </span>
    </div>

    <div>
      {#if isUnsaved}
        <span class="text-amber-400 flex items-center gap-1">
          <i class="fa-solid fa-circle-dot"></i> Не сохранено
        </span>
      {:else}
        <span class="text-emerald-400 flex items-center gap-1">
          <i class="fa-solid fa-check"></i> Синхронизировано
        </span>
      {/if}
    </div>
  </div>
</div>
