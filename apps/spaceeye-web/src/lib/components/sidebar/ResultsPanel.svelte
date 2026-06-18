<script lang="ts">
  import ImageGallery from '$lib/components/ImageGallery.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import { mapState } from '$lib/stores/map.svelte';
  import { processImage } from '$lib/api/processing';
  import { handleToggleSelect } from '$lib/helpers/comparison';
  import SidebarSection from './SidebarSection.svelte';

  function handleProcess(id: string) {
    mapState.showImageGallery = false;
    processImage(id);
  }

  let hasResults = $derived(mapState.results.length > 0);
</script>

<SidebarSection title="Results" icon="🖼">
  {#if hasResults}
    <div class="space-y-2">
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
          onToggleSelect={handleToggleSelect}
        />
      </div>
    </div>
  {:else}
    <p class="text-xs text-muted-foreground">No images found. Draw a polygon on the map, select a satellite collection, and click Search.</p>
  {/if}
</SidebarSection>
