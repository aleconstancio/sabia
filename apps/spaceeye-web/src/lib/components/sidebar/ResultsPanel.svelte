<script lang="ts">
  import ImageGallery from '$lib/components/ImageGallery.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import Button from '$lib/ui/components/Button.svelte';
  import { mapState } from '$lib/stores/map.svelte.ts';
  import { processImage } from '$lib/api/processing';

  let expanded = $state(true);

  function handleProcess(id: string) {
    mapState.showImageGallery = false;
    processImage(id);
  }
</script>

<div class="sidebar-section">
  <button onclick={() => expanded = !expanded} class="sidebar-section-header" aria-expanded={expanded} aria-label="Resultados">
    <span class="text-lg mr-2">🖼</span>
    <span class="text-xs font-bold uppercase tracking-wider" style="color: var(--muted-foreground);">Resultados</span>
    {#if mapState.results.length > 0}
      <span class="ml-2 text-xs font-mono" style="color: var(--muted-foreground);">{mapState.results.length}</span>
    {/if}
    <svg class="ml-auto w-3 h-3 transition-transform" class:rotate-180={expanded} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
  </button>
  {#if expanded && mapState.results.length > 0}
    <div class="space-y-2 mt-2">
      <FilterBar
        bind:dateFrom={mapState.filterDateFrom}
        bind:dateTo={mapState.filterDateTo}
        bind:maxCloud={mapState.filterMaxCloud}
        bind:sortBy={mapState.filterSortBy}
        bind:sortOrder={mapState.filterSortOrder}
      />
      <div class="max-h-60 overflow-y-auto">
        <ImageGallery
          images={mapState.results}
          selectedProduct={mapState.selectedProduct}
          processImage={handleProcess}
          selectionMode={mapState.showComparison}
          selectedIds={mapState.selectedIds}
        />
      </div>
    </div>
  {:else if expanded}
    <p class="text-xs mt-2" style="color: var(--muted-foreground);">Nenhum resultado ainda. Busque imagens para começar.</p>
  {/if}
</div>

<style>
  .sidebar-section { margin-bottom: 1rem; }
  .sidebar-section-header {
    display: flex; align-items: center; width: 100%;
    padding: 0.5rem; border-radius: var(--radius);
    cursor: pointer; transition: background 150ms;
    background: transparent; border: none; color: inherit;
  }
  .sidebar-section-header:hover { background: var(--muted); }
</style>
