<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { monitorsStore } from '$lib/stores/monitors.svelte';
  import { bookmarksStore } from '$lib/stores/bookmarks.svelte';
  import { Button } from '$lib/components/ui/button';
  import * as Dialog from '$lib/components/ui/dialog';
  import type { Monitor, Bookmark } from '$lib/api/types';

  let show = $state(false);
  let monitors = $state<Monitor[]>([]);
  let checking = $state(false);
  let statusMsg = $state('');
  let showNameInput = $state(false);
  let nameInputValue = $state('');
  let availableBookmarks = $state<Bookmark[]>([]);
  let panelRef: HTMLDivElement;
  let deleteTarget = $state<Monitor | null>(null);
  let showDeleteDialog = $state(false);

  function handleClickOutside(e: MouseEvent) {
    if (panelRef && !panelRef.contains(e.target as Node) && !showNameInput) {
      show = false;
    }
  }

  onMount(() => document.addEventListener('mousedown', handleClickOutside));
  onDestroy(() => document.removeEventListener('mousedown', handleClickOutside));

  function refresh() { monitors = monitorsStore.getAll(); }

  $effect(() => { if (show) refresh(); });

  async function runAllChecks() {
    checking = true;
    statusMsg = `Verificando ${monitors.length} locais...`;
    for (const m of monitors) {
      if (m.active) await monitorsStore.check(m);
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
    const bm = availableBookmarks.find(b => b.id === nameInputValue);
    if (bm) {
      monitorsStore.add(bm);
      refresh();
      statusMsg = `Monitorando "${bm.name}"`;
    } else {
      statusMsg = 'Local não encontrado';
    }
    showNameInput = false;
  }

  function confirmDeleteMonitor(m: Monitor) {
    deleteTarget = m;
    showDeleteDialog = true;
  }

  function handleConfirmDeleteMonitor() {
    if (deleteTarget) {
      monitorsStore.remove(deleteTarget.id);
      refresh();
    }
    showDeleteDialog = false;
    deleteTarget = null;
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
            <button class="text-xs text-destructive bg-transparent border-none cursor-pointer ml-2" aria-label="Remover monitor" onclick={() => confirmDeleteMonitor(m)}>✕</button>
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
            <option value={bm.id}>{bm.name}</option>
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

<Dialog.Root bind:open={showDeleteDialog}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" />
    <Dialog.Content class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card border border-border p-6 shadow-lg">
      <Dialog.Title>Remover monitor?</Dialog.Title>
      <p class="text-sm text-muted-foreground">
        Tem certeza que deseja remover o monitor de "{deleteTarget?.bookmarkName}"?
      </p>
      <Dialog.Footer>
        <Button variant="ghost" onclick={() => { showDeleteDialog = false; deleteTarget = null; }}>Cancelar</Button>
        <Button variant="destructive" onclick={handleConfirmDeleteMonitor}>Remover</Button>
      </Dialog.Footer>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
