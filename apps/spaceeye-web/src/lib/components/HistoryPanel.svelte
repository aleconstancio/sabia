<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { historyStore } from '$lib/stores/history.svelte';
  import { Button } from '$lib/components/ui/button';
  import type { AnalysisRecord } from '$lib/api/types';

  let { onRestore = (r: AnalysisRecord) => {} } = $props();
  let history = $state<AnalysisRecord[]>([]);
  let show = $state(false);
  let panelRef: HTMLDivElement;

  function refresh() { history = historyStore.refresh(); }

  function handleClickOutside(e: MouseEvent) {
    if (panelRef && !panelRef.contains(e.target as Node)) {
      show = false;
    }
  }

  onMount(() => document.addEventListener('mousedown', handleClickOutside));
  onDestroy(() => document.removeEventListener('mousedown', handleClickOutside));

  $effect(() => { if (show) refresh(); });
</script>

<div class="relative" bind:this={panelRef}>
  <Button size="sm" variant="ghost" onclick={() => { show = !show; refresh(); }} class="!text-xs">History</Button>
  {#if show}
    <div class="absolute top-full right-0 mt-1 w-80 rounded-lg border border-border bg-card shadow-lg p-2 z-[1000] max-h-80 overflow-y-auto">
      <div class="flex items-center justify-between mb-2 px-1">
        <h4 class="text-xs font-semibold text-muted-foreground uppercase">Recent Analyses</h4>
        <button class="text-xs text-destructive bg-transparent border-none cursor-pointer hover:underline" onclick={() => { historyStore.clear(); refresh(); }}>Clear</button>
      </div>
      {#if history.length === 0}
        <p class="text-xs text-muted-foreground p-2">No analyses yet. Draw a polygon, search for images, and process one to build your history.</p>
      {:else}
        {#each history as r}
          <button class="w-full text-left px-2 py-1.5 rounded hover:bg-muted cursor-pointer bg-transparent border-none" onclick={() => { onRestore(r); show = false; }}>
            <div class="flex justify-between items-center">
              <span class="text-xs font-mono truncate flex-1">{r.imageId?.slice(0, 24)}...</span>
              <span class="text-xs text-muted-foreground ml-2">{r.product}</span>
            </div>
            <div class="flex justify-between text-xs text-muted-foreground">
              <span>{new Date(r.timestamp).toLocaleString()}</span>
              <span>{r.collection}</span>
            </div>
          </button>
        {/each}
      {/if}
    </div>
  {/if}
</div>
