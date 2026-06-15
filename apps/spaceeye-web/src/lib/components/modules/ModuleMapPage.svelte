<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import { createLeafletMap } from '$lib/helpers/leaflet';
  import { mapState } from '$lib/stores/map.svelte';
  import ModuleSidebar from './ModuleSidebar.svelte';

  let { module, product }: { module: string; product: string } = $props();

  let mapContainer: HTMLDivElement;
  let leafletMap: ReturnType<typeof createLeafletMap> | null = null;

  onMount(async () => {
    if (!browser || !mapContainer) return;

    leafletMap = createLeafletMap(mapContainer, {
      keyboard: false,
      onPolygonCreated: (coords) => {
        mapState.polygonCoords = coords;
      },
    });

    await leafletMap.init();
    mapState.selectedProduct = product;
  });

  onDestroy(() => {
    leafletMap?.destroy();
  });
</script>

<div class="flex flex-1 min-h-0">
  <ModuleSidebar {module} />
  <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
</div>