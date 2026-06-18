<script lang="ts">
  import L from 'leaflet';
  import { Button } from '$lib/components/ui/button';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Progress } from '$lib/components/ui/progress';
  import * as Select from '$lib/components/ui/select';
  import ImageGallery from '$lib/components/ImageGallery.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import HistogramPanel from '$lib/components/HistogramPanel.svelte';
  import ProductInfo from '$lib/components/ProductInfo.svelte';
  import { mapState } from '$lib/stores/map.svelte';
  import { searchImages, processImage } from '$lib/api/processing';
  import { handleToggleSelect } from '$lib/helpers/comparison';
  import { SPECTRAL_PRODUCTS } from '$lib/constants';
  import { Spinner } from '$lib/components/ui/spinner';

  let {
    drawnItems,
    onSaveLocal = () => {},
  }: {
    drawnItems: L.FeatureGroup | null;
    onSaveLocal?: () => void;
  } = $props();
</script>

<Dialog.Root bind:open={mapState.showPolygonModal}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" />
    <Dialog.Content class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card border border-border p-6 shadow-lg">
      <Dialog.Title>Search images from this location?</Dialog.Title>
      <div class="space-y-4">
        <div>
          <label for="product-select" class="text-sm font-medium">Product</label>
          <Select.Root type="single" bind:value={mapState.selectedProduct}>
            <Select.Trigger class="w-full">
              Product...
            </Select.Trigger>
            <Select.Content>
              {#each SPECTRAL_PRODUCTS as option}
                <Select.Item value={option.value}>{option.label}</Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
          <ProductInfo product={mapState.selectedProduct} />
        </div>
        {#if drawnItems && drawnItems.getLayers().length > 1}
          <Button variant="ghost" onclick={() => {
            if (!drawnItems) return;
            const layers = drawnItems.getLayers();
            if (layers.length < 2) return;
            const bounds = drawnItems.getBounds();
            const polygon = L.rectangle(bounds);
            drawnItems.clearLayers();
            drawnItems.addLayer(polygon);
            const geoJSON = polygon.toGeoJSON();
            mapState.polygonCoords = geoJSON.geometry.coordinates as number[][][];
            mapState.polygonCentroid = { lat: polygon.getCenter().lat, lon: polygon.getCenter().lng };
          }}>Merge areas</Button>
        {/if}
        {#if mapState.searchError}
          <div class="flex items-center gap-2 mt-2">
            <p class="text-destructive text-sm flex-1">{mapState.searchError}</p>
            <Button size="sm" variant="outline" onclick={searchImages}>Try again</Button>
          </div>
        {/if}
      </div>
      <Dialog.Footer>
        <Button variant="ghost" onclick={() => mapState.showPolygonModal = false}>Cancel</Button>
        <Button variant="ghost" onclick={onSaveLocal}>Save location</Button>
        <Button onclick={searchImages}>
          {#if mapState.isLoading}<Spinner size="sm" />{/if}
          Search images
        </Button>
      </Dialog.Footer>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={mapState.showImageGallery}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" />
    <Dialog.Content class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card border border-border p-6 shadow-lg">
      <Dialog.Title>Related Images</Dialog.Title>
      {#if mapState.results.length === 0}
        <div class="flex flex-col items-center justify-center py-16 text-center">
          <h3 class="text-lg font-semibold text-foreground mb-1">No images</h3>
          <p class="text-sm text-muted-foreground max-w-sm">We couldn't find images for this location.</p>
        </div>
      {:else}
        <div class="space-y-2">
          <FilterBar
            bind:dateFrom={mapState.filterDateFrom}
            bind:dateTo={mapState.filterDateTo}
            bind:maxCloud={mapState.filterMaxCloud}
            bind:sortBy={mapState.filterSortBy}
            bind:sortOrder={mapState.filterSortOrder}
          />
          {#if mapState.showComparison}
            <p class="text-xs text-muted-foreground px-2">Select two images to compare</p>
          {/if}
          <ImageGallery
            images={mapState.results}
            selectedProduct={mapState.selectedProduct}
            processImage={processImage}
            selectionMode={mapState.showComparison}
            selectedIds={mapState.selectedIds}
            onToggleSelect={handleToggleSelect}
          />
        </div>
      {/if}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={mapState.showProcessingViewer}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card border border-border p-6 shadow-lg"
      onkeydown={(e) => { if (e.key === 'Escape') mapState.showProcessingViewer = false; }}
    >
      <Dialog.Title>Processing image</Dialog.Title>
      <div class="space-y-4 text-center py-8">
        <Spinner size="lg" />
        <p class="text-muted-foreground" aria-live="polite">{mapState.processingPhase || 'Starting...'}</p>
        <Progress value={mapState.processingProgress} />
        <p class="text-sm text-muted-foreground">{mapState.processingProgress}%</p>
        {#if mapState.lastStats}
          <HistogramPanel stats={mapState.lastStats} product={mapState.selectedProduct} />
        {/if}
      </div>
      <Dialog.Footer>
        <Button variant="outline" onclick={() => mapState.showProcessingViewer = false} autofocus>Close</Button>
      </Dialog.Footer>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>