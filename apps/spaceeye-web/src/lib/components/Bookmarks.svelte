<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Button } from '$lib/components/ui/button';
  import Dialog from '$lib/ui/components/Dialog.svelte';
  import { bookmarksStore } from '$lib/stores/bookmarks.svelte';
  import type { Bookmark } from '$lib/api/types';

  let {
    onSelect = (coords: number[][][], name: string) => {},
    currentCoords = null as number[][][] | null,
  }: {
    onSelect: (coords: number[][][], name: string) => void;
    currentCoords?: number[][][] | null;
  } = $props();

  let bookmarks = $state<Bookmark[]>([]);
  let showPanel = $state(false);
  let panelRef: HTMLDivElement;
  let deleteTarget = $state<Bookmark | null>(null);
  let showDeleteDialog = $state(false);

  function handleClickOutside(e: MouseEvent) {
    if (panelRef && !panelRef.contains(e.target as Node)) {
      showPanel = false;
    }
  }

  onMount(() => document.addEventListener('mousedown', handleClickOutside));
  onDestroy(() => document.removeEventListener('mousedown', handleClickOutside));

  function loadBookmarks() {
    bookmarks = bookmarksStore.refresh();
  }

  function handleAddBookmark(name: string, coords: number[][][]) {
    bookmarksStore.add(name, coords);
    bookmarks = bookmarksStore.all;
  }

  function confirmDelete(b: Bookmark, e: MouseEvent) {
    e.stopPropagation();
    deleteTarget = b;
    showDeleteDialog = true;
  }

  function handleConfirmDelete() {
    if (deleteTarget) {
      bookmarksStore.remove(deleteTarget.id);
      bookmarks = bookmarksStore.all;
    }
    showDeleteDialog = false;
    deleteTarget = null;
  }

  function selectBookmark(b: Bookmark) {
    onSelect(b.coords, b.name);
    showPanel = false;
  }

  loadBookmarks();
</script>

<div class="relative" bind:this={panelRef}>
  <Button size="sm" variant="ghost" onclick={() => showPanel = !showPanel}>
    {bookmarks.length > 0 ? `${bookmarks.length} salvos` : 'Salvos'}
  </Button>

  {#if showPanel}
    <div class="absolute top-full right-0 mt-1 w-64 rounded-lg border border-border bg-card shadow-lg p-2 z-[1000] max-h-64 overflow-y-auto">
      <div class="flex items-center justify-between mb-2 px-1">
        <h4 class="text-xs font-semibold text-muted-foreground uppercase">Locais Salvos</h4>
        <button class="text-xs text-primary bg-transparent border-none cursor-pointer" onclick={loadBookmarks}>Atualizar</button>
      </div>
      {#if bookmarks.length === 0}
        <p class="text-xs text-muted-foreground p-2">Nenhum local salvo ainda.</p>
      {:else}
        {#each bookmarks as b}
          <div class="flex items-center justify-between px-2 py-1.5 rounded hover:bg-muted cursor-pointer group" role="button" tabindex="0" onclick={() => selectBookmark(b)} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') selectBookmark(b); }}>
            <div>
              <p class="text-sm font-medium">{b.name}</p>
              <p class="text-xs text-muted-foreground">{new Date(b.created_at).toLocaleDateString('pt-BR')}</p>
            </div>
            <button
              class="text-xs text-destructive bg-transparent border-none cursor-pointer opacity-0 group-hover:opacity-100"
              aria-label="Remover"
              onclick={(e) => confirmDelete(b, e)}
            >
              ✕
            </button>
          </div>
        {/each}
      {/if}
    </div>
  {/if}
</div>

<Dialog bind:open={showDeleteDialog} title="Remover local salvo?">
  <p class="text-sm text-muted-foreground">
    Tem certeza que deseja remover "{deleteTarget?.name}"?
  </p>
  {#snippet actions()}
    <Button variant="ghost" onclick={() => { showDeleteDialog = false; deleteTarget = null; }}>Cancelar</Button>
    <Button variant="destructive" onclick={handleConfirmDelete}>Remover</Button>
  {/snippet}
</Dialog>
