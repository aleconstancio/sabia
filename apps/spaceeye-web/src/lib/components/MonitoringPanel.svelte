<script lang="ts">
  import { getMonitors, removeMonitor, checkMonitor, addMonitor } from '$lib/stores/monitors.svelte.ts';
  import { getBookmarks } from '$lib/stores/bookmarks.svelte.ts';
  import Button from '$lib/ui/components/Button.svelte';

  let show = $state(false);
  let monitors = $state<any[]>([]);
  let checking = $state(false);
  let statusMsg = $state('');

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
    const bookmarks = getBookmarks();
    if (bookmarks.length === 0) { statusMsg = 'Nenhum local salvo'; return; }
    const name = prompt('Qual local monitorar?', bookmarks[0]?.name || '');
    if (!name) return;
    const bm = bookmarks.find(b => b.name === name);
    if (bm) {
      addMonitor(bm);
      refresh();
      statusMsg = `Monitorando "${bm.name}"`;
    } else {
      statusMsg = 'Local não encontrado';
    }
  }
</script>

<div class="relative">
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
            <button class="text-xs text-destructive bg-transparent border-none cursor-pointer ml-2" aria-label="Remover monitor" onclick={() => { if (confirm('Remover este monitor?')) { removeMonitor(m.id); refresh(); } }}>✕</button>
          </div>
        {/each}
        <div class="mt-2 pt-2 border-t border-border">
          <Button size="sm" variant="outline" class="!w-full !text-xs" onclick={runAllChecks} loading={checking}>
            {checking ? 'Verificando...' : 'Verificar todos agora'}
          </Button>
        </div>
      {/if}
      {#if statusMsg}
        <p class="text-xs text-muted-foreground mt-1 px-1">{statusMsg}</p>
      {/if}
    </div>
  {/if}
</div>
