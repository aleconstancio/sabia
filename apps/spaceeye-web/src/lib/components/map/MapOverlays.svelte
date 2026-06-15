<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import RegionComparison from '$lib/components/RegionComparison.svelte';
  import SwipeComparison from '$lib/components/SwipeComparison.svelte';
  import TimeSlider from '$lib/components/TimeSlider.svelte';
  import NdviTimeline from '$lib/components/NdviTimeline.svelte';
  import TimelapsePlayer from '$lib/components/TimelapsePlayer.svelte';
  import { mapState } from '$lib/stores/map.svelte';
  import { processImage } from '$lib/api/processing';

  let {
    showTimelapse = false,
    measureMode = false,
    mouseCoords = { lat: 0, lng: 0 },
  }: {
    showTimelapse?: boolean;
    measureMode?: boolean;
    mouseCoords?: { lat: number; lng: number };
  } = $props();

  let useSwipe = $state(false);
</script>

{#if measureMode}
  <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-[1000] bg-black/80 text-white text-xs px-3 py-1 rounded-full font-mono">
    {mouseCoords.lat}, {mouseCoords.lng}
  </div>
{/if}

{#if mapState.showComparison && mapState.comparisonFirst && mapState.comparisonSecond}
  <div class="absolute left-4 right-4 bottom-20 z-[999]">
    <div class="flex justify-end mb-1">
      <Button variant="ghost" size="sm" onclick={() => useSwipe = !useSwipe} aria-label="Alternar modo de comparacao">
        {useSwipe ? 'Lado a lado' : 'Deslizar'}
      </Button>
    </div>
    {#if useSwipe}
      <SwipeComparison imageA={mapState.comparisonFirst} imageB={mapState.comparisonSecond} polygonCoords={mapState.polygonCoords} polygonCentroid={mapState.polygonCentroid} product={mapState.selectedProduct} />
    {:else}
      <RegionComparison imageA={mapState.comparisonFirst} imageB={mapState.comparisonSecond} polygonCoords={mapState.polygonCoords} polygonCentroid={mapState.polygonCentroid} product={mapState.selectedProduct} />
    {/if}
  </div>
{:else if mapState.showComparison}
  <div class="absolute left-4 right-4 bottom-20 z-[999]">
    <div class="rounded-lg border border-border bg-card p-4 text-center">
      <p class="text-sm text-muted-foreground">Selecione duas imagens na galeria para comparar</p>
    </div>
  </div>
{/if}

{#if mapState.results.length > 0 && !mapState.showImageGallery && !mapState.showProcessingViewer}
  <div class="absolute left-4 bottom-4 z-[999] w-72 space-y-2">
    <NdviTimeline images={mapState.results} polygonCoords={mapState.polygonCoords} product={mapState.selectedProduct} />
    <TimeSlider images={mapState.results} onSelect={(id) => {
      const img = mapState.results.find(i => i.id === id);
      if (img) processImage(img.id);
    }} />
  </div>
{/if}

{#if showTimelapse && mapState.results.length > 0 && !mapState.showImageGallery && !mapState.showProcessingViewer}
  <div class="absolute left-4 bottom-36 z-[999] w-72">
    <TimelapsePlayer images={mapState.results} polygonCoords={mapState.polygonCoords} product={mapState.selectedProduct} onFrameChange={(id: string) => {
      const img = mapState.results.find(i => i.id === id);
      if (img) processImage(img.id);
    }} />
  </div>
{/if}