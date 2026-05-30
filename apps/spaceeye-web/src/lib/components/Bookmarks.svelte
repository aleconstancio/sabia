<script lang="ts">
  import Button from '$lib/ui/components/Button.svelte';

  let {
    onSelect = (coords: number[][][], name: string) => {},
    onSaveBookmark = (name: string, coords: number[][][]) => {},
    currentCoords = null as number[][][] | null,
  }: {
    onSelect: (coords: number[][][], name: string) => void;
    onSaveBookmark: (name: string, coords: number[][][]) => void;
    currentCoords?: number[][][] | null;
  } = $props();

  let bookmarks = $state<any[]>([]);
  let showPanel = $state(false);

  function loadBookmarks() {
    try {
      const raw = localStorage.getItem('spaceeye_bookmarks');
      bookmarks = raw ? JSON.parse(raw) : [];
    } catch { bookmarks = []; }
  }

  function saveBookmarks() {
    localStorage.setItem('spaceeye_bookmarks', JSON.stringify(bookmarks));
  }

  function addBookmark(name: string, coords: number[][][]) {
    bookmarks = [...bookmarks, {
      id: crypto.randomUUID(),
      name,
      coords,
      created_at: new Date().toISOString(),
    }];
    saveBookmarks();
  }

  function removeBookmark(id: string, e: MouseEvent) {
    e.stopPropagation();
    bookmarks = bookmarks.filter((b: any) => b.id !== id);
    saveBookmarks();
  }

  function selectBookmark(b: any) {
    onSelect(b.coords, b.name);
    showPanel = false;
  }

  loadBookmarks();
</script>

<div class="relative">
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
          <div class="flex items-center justify-between px-2 py-1.5 rounded hover:bg-muted cursor-pointer group" onclick={() => selectBookmark(b)}>
            <div>
              <p class="text-sm font-medium">{b.name}</p>
              <p class="text-xs text-muted-foreground">{new Date(b.created_at).toLocaleDateString('pt-BR')}</p>
            </div>
            <button
              class="text-xs text-destructive bg-transparent border-none cursor-pointer opacity-0 group-hover:opacity-100"
              onclick={(e) => removeBookmark(b.id, e)}
            >
              ✕
            </button>
          </div>
        {/each}
      {/if}
    </div>
  {/if}
</div>
