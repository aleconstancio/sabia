<script lang="ts">
  import '$lib/components/sidebar/sidebar.css';
  import Select from '$lib/ui/components/Select.svelte';
  import Button from '$lib/ui/components/Button.svelte';
  import { mapState } from '$lib/stores/map.svelte.ts';
  import { searchImages } from '$lib/api/processing';

  let expanded = $state(true);
</script>

<div class="sidebar-section">
  <button onclick={() => expanded = !expanded} class="sidebar-section-header" aria-expanded={expanded} aria-label="Busca">
    <span class="text-lg mr-2">🔍</span>
    <span class="text-xs font-bold uppercase tracking-wider" style="color: var(--muted-foreground);">Busca</span>
    <svg class="ml-auto w-3 h-3 transition-transform" class:rotate-180={expanded} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
  </button>
  {#if expanded}
    <div class="space-y-3 mt-2">
      <div class="text-xs" style="color: var(--muted-foreground);">
        Desenhe um polígono no mapa para buscar imagens
      </div>
      <Select bind:value={mapState.selectedProduct} options={[
        { value: 'NDVI', label: 'NDVI' },
        { value: 'TCI', label: 'TCI' },
        { value: 'NDWI', label: 'NDWI' },
        { value: 'SAVI', label: 'SAVI' },
        { value: 'EVI', label: 'EVI' },
        { value: 'CIR', label: 'CIR' },
      ]} />
      {#if mapState.polygonCoords}
        <Button onclick={searchImages} loading={mapState.isLoading} class="!w-full">Buscar imagens</Button>
      {/if}
      {#if mapState.searchError}
        <p class="text-xs" style="color: var(--destructive);">{mapState.searchError}</p>
      {/if}
    </div>
  {/if}
</div>

