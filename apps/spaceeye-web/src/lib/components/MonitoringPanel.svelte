<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { getMonitors, removeMonitor, checkMonitor, addMonitor } from '$lib/stores/monitors.svelte';
  import { bookmarksStore } from '$lib/stores/bookmarks.svelte';
  import { Button } from '$lib/components/ui/button';

  let show = $state(false);
  let monitors = $state<any[]>([]);
  let checking = $state(false);
  let statusMsg = $state('');
  let showNameInput = $state(false);
  let nameInputValue = $state('');
  let availableBookmarks = $state<any[]>([]);
  let panelRef: HTMLDivElement;

  function handleClickOutside(e: MouseEvent) {
    if (panelRef && !panelRef.contains(e.target as Node) && !showNameInput) {
      show = false;
    }
  }

  onMount(() => document.addEventListener('mousedown', handleClickOutside));
  onDestroy(() => document.removeEventListener('mousedown', handleClickOutside));

  function refresh() { monitors = getMonitors(); }

  $effect(() => { if (show) refresh(); });

  async function runAllChecks() {
    checking = true;
    statusMsg = `Verificando ${monitors.length} locais...`;
    for (const m of monitors) {
      if (m.active) await checkMonitor(m);
    }
    refresh();
    statusMsg = 'Verificação concluída';
    checking = false;
  }

  function addFromBookmark() {
    const bookmarks = bookmarksStore.all;
    if (bookmarks.length === 0) { statusMsg = 'Nenhum local salvo'; return; }
    availableBookmarks = bookmarks;
    nameInputValue = bookmarks[0]?.name || '';
    showNameInput = true;
  }

  function handleNameSubmit() {
    const bm = availableBookmarks.find(b => b.name === nameInputValue);
    if (bm) {
      addMonitor(bm);
      refresh();
      statusMsg = `Monitorando "${bm.name}"`;
    } else {
      statusMsg = 'Local não encontrado';
    }
    showNameInput = false;
  }
</script>

<div class="relative" bind:this={panelRef}>
  <Button size="sm" variant="ghost" onclick={() => { show = !show; refresh(); }} class="!text-xs">
    {monitors.length > 0 ? `${monitors.length} monitores` : 'Monitorar'}
  </Button>
  {#if show}
    <div class="absolute top-full right-0 mt-1 w-80 rounded-lg border border-border bg-card shadow-lg p-2 z-[1000] max-h-96 overflow-y-auto">
      <div class="flex items-center justify-between mb-2 px-1">
        <h4 class="text-xs font-semibold text-muted-foreground uppercase">Monitoramento</h4>
        <button class="text-xs text-primary bg-transparent border-none cursor-pointer hover:underline" onclick={addFromBookmark}>+ Adicionar</button>
      </div>
      {#if monitors.length === 0}
        <p class="text-xs text-muted-foreground p-2">Nenhum monitor ativo. Adicione um local salvo para monitorar novas imagens.</p>
      {:else}
        {#each monitors as m}
          <div class="flex items-center justify-between px-2 py-1.5 rounded hover:bg-muted">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium truncate">{m.bookmarkName}</p>
              <p class="text-xs text-muted-foreground truncate">{m.lastResult || 'Aguardando verificação'}</p>
              {#if m.lastChecked}
                <p class="text-xs text-muted-foreground">{new Date(m.lastChecked).toLocaleString('pt-BR')}</p>
              {/if}
            </div>
            <button class="text-xs text-destructive bg-transparent border-none cursor-pointer ml-2" aria-label="Remover monitor" onclick={() => { // TODO: Replace with custom Dialog component for consistency
              if (confirm('Remover este monitor?')) { removeMonitor(m.id); refresh(); }
            }}>✕</button>
          </div>
        {/each}
        <div class="mt-2 pt-2 border-t border-border">
          <Button size="sm" variant="outline" class="!w-full !text-xs" onclick={runAllChecks}>
            {#if checking}<span class="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full"></span>{/if}
            {checking ? 'Verificando...' : 'Verificar todos agora'}
          </Button>
        </div>
      {/if}
      {#if statusMsg}
        <p class="text-xs text-muted-foreground mt-1 px-1" aria-live="polite">{statusMsg}</p>
      {/if}
    </div>
  {/if}
  {#if showNameInput}
    <div class="fixed inset-0 z-[2000] flex items-center justify-center bg-black/50">
      <form onsubmit={(e) => { e.preventDefault(); handleNameSubmit(); }} class="bg-card border border-border rounded-lg p-6 shadow-xl w-80 space-y-4">
        <label class="text-sm font-medium" for="monitor-name-input">Qual local monitorar?</label>
        <select
          id="monitor-name-input"
          bind:value={nameInputValue}
          class="w-full px-3 py-2 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
        >
          {#each availableBookmarks as bm}
            <option value={bm.name}>{bm.name}</option>
          {/each}
        </select>
        <div class="flex justify-end gap-2">
          <Button type="button" variant="ghost" onclick={() => { showNameInput = false; }}>Cancelar</Button>
          <Button type="submit">Monitorar</Button>
        </div>
      </form>
    </div>
  {/if}
</div>
