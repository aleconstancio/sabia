<script lang="ts">
  import { Badge } from '$lib/components/ui/badge';
  import ImageMetadata from '$lib/components/ImageMetadata.svelte';
  import type { ImageResult } from '$lib/api/types';

  let {
    images = [] as ImageResult[],
    selectedProduct = 'NDVI',
    processImage = (imageId: string) => {},
    selectionMode = false,
    selectedIds = [] as string[],
    onToggleSelect = (imageId: string) => {},
  }: {
    images: ImageResult[];
    selectedProduct: string;
    processImage: (imageId: string) => void;
    selectionMode?: boolean;
    selectedIds?: string[];
    onToggleSelect?: (imageId: string) => void;
  } = $props();

  let maxCloud = $state(100);
  let filteredImages = $derived(images.filter(i => (i.cloud_cover ?? 100) <= maxCloud));
  let selectedSet = $derived(new Set(selectedIds));

  let loadedIds = $state<Record<string, boolean>>({});
  let errorMap = $state<Record<string, boolean>>({});
  let hoveredImage = $state<ImageResult | null>(null);

  function onImgLoad(id: string) {
    loadedIds[id] = true;
  }
  function onImgError(id: string) {
    errorMap[id] = true;
    loadedIds[id] = true;
  }
</script>

<div class="flex items-center gap-3 px-2 py-2 border-b border-border mb-2">
  <label for="cloud-filter" class="text-xs text-muted-foreground whitespace-nowrap">Max cloud:</label>
  <input id="cloud-filter" type="range" min="0" max="100" bind:value={maxCloud} class="flex-1 accent-emerald-500" />
  <span class="text-xs font-mono w-8 text-right">{maxCloud}%</span>
  <span class="text-xs text-muted-foreground">({filteredImages.length}/{images.length})</span>
</div>

{#if filteredImages.length === 0 && images.length > 0}
  <div class="text-center py-8 text-muted-foreground">
    <p class="text-sm">No images with cloud cover below {maxCloud}%</p>
    <p class="text-xs mt-1">Adjust the filter to see more results</p>
  </div>
{:else}
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-h-[60vh] overflow-y-auto p-2">
    {#each filteredImages as img (img.id)}
      <button
        class="relative rounded-lg border border-border bg-card p-3 text-left transition-all hover:border-primary hover:shadow-md cursor-pointer"
        class:border-emerald-500={selectionMode && selectedSet.has(img.id)}
        class:ring-2={selectionMode && selectedSet.has(img.id)}
        class:ring-emerald-500={selectionMode && selectedSet.has(img.id)}
        onclick={() => selectionMode ? onToggleSelect(img.id) : processImage(img.id)}
        onmouseenter={() => hoveredImage = img}
        onmouseleave={() => hoveredImage = null}
      >
        {#if img.thumbnail_url && !errorMap[img.id]}
          {#if !loadedIds[img.id]}
            <div class="w-full h-40 bg-muted rounded-md mb-2 animate-pulse"></div>
          {/if}
          <img
            src={img.thumbnail_url}
            alt="Satellite {img.collection || 'image'} {new Date(img.acquired_at).toLocaleDateString()}"
            class="w-full h-40 object-cover rounded-md mb-2"
            class:hidden={!loadedIds[img.id]}
            loading="lazy"
            onload={() => onImgLoad(img.id)}
            onerror={() => onImgError(img.id)}
          />
        {:else}
          <div class="w-full h-40 bg-muted rounded-md mb-2 flex items-center justify-center text-muted-foreground text-sm">
            No thumbnail
          </div>
        {/if}
        {#if selectionMode && selectedSet.has(img.id)}
          <div class="absolute top-2 right-2 w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center text-white text-xs font-bold">✓</div>
        {/if}
        <p class="font-mono text-xs truncate mb-1">{img.id}</p>
        <div class="flex items-center justify-between">
          <Badge variant={(img.cloud_cover ?? 100) < 20 ? 'success' : (img.cloud_cover ?? 100) < 50 ? 'warning' : 'destructive'}>
            {img.cloud_cover?.toFixed(1) ?? '—'}% cloud
          </Badge>
          <span class="text-xs text-muted-foreground">
            {new Date(img.acquired_at).toLocaleDateString()}
          </span>
        </div>
        {#if hoveredImage === img}
          <div class="absolute left-0 right-0 bottom-full z-50">
            <ImageMetadata image={img} />
          </div>
        {/if}
      </button>
    {/each}
  </div>
{/if}
