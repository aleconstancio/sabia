<script lang="ts">
  import Select from '$lib/ui/components/Select.svelte';
  import Button from '$lib/ui/components/Button.svelte';
  import { mapState } from '$lib/stores/map.svelte.ts';
  import { searchImages } from '$lib/api/processing';
  import ProductInfo from '$lib/components/ProductInfo.svelte';
  import { SPECTRAL_PRODUCTS } from '$lib/constants';

  let expanded = $state(true);
</script>

<div class="mb-4 sidebar-section">
  <button onclick={() => expanded = !expanded} class="flex items-center w-full p-2 rounded-[--radius] cursor-pointer transition-colors bg-transparent border-none text-inherit hover:bg-muted sidebar-section-header" aria-expanded={expanded} aria-label="Busca">
    <span class="text-lg mr-2">🔍</span>
    <span class="text-xs font-bold uppercase tracking-wider text-muted-foreground">Busca</span>
    <svg class="ml-auto w-3 h-3 transition-transform" class:rotate-180={expanded} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
  </button>
  {#if expanded}
    <div class="space-y-3 mt-2">
      <div class="text-xs text-muted-foreground">
        Desenhe um polígono no mapa para buscar imagens
      </div>
      <Select bind:value={mapState.selectedProduct} options={SPECTRAL_PRODUCTS} />
      <ProductInfo product={mapState.selectedProduct} />
      {#if mapState.polygonCoords}
        <Button onclick={searchImages} loading={mapState.isLoading} class="!w-full">Buscar imagens</Button>
      {/if}
      {#if mapState.searchError}
        <p class="text-xs text-destructive">{mapState.searchError}</p>
      {/if}
    </div>
  {/if}
</div>
