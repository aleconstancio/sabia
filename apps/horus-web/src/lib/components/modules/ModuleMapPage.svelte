<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { createLeafletMap } from '$lib/helpers/leaflet';
  import { mapState } from '$lib/stores/map.svelte';
  import { Spinner } from '$lib/components/ui/spinner';
  import ModuleSidebar from './ModuleSidebar.svelte';

  let { module, product }: { module: string; product: string } = $props();

  let mapContainer: HTMLDivElement;
  let leafletMap: ReturnType<typeof createLeafletMap> | null = null;
  let exporting = $state(false);
  let sidebarOpen = $state(true);

  const moduleTitle = $derived(
    module.charAt(0).toUpperCase() + module.slice(1).replace(/-/g, ' ')
  );

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

  async function handleExport() {
    exporting = true;
    try {
      window.print();
    } finally {
      exporting = false;
    }
  }
</script>

<div class="flex flex-1 min-h-0">
  {#if sidebarOpen}
    <ModuleSidebar {module} />
  {/if}
  <div class="relative flex-1 min-h-0">
    <div class="absolute top-3 left-3 right-3 z-[1000] flex items-center gap-3 rounded-lg border border-border bg-card/95 backdrop-blur px-3 py-2 shadow-md">
      <button
        onclick={() => sidebarOpen = !sidebarOpen}
        class="flex items-center justify-center w-6 h-6 rounded hover:bg-muted transition-colors text-muted-foreground"
        aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
      >
        <svg class="w-4 h-4 transition-transform {sidebarOpen ? '' : 'rotate-180'}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>
      <button
        onclick={() => goto('/dashboard')}
        class="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
      >
        <span class="text-sm leading-none">&larr;</span>
        Dashboard
      </button>
      <div class="h-4 w-px bg-border"></div>
      <h2 class="text-sm font-semibold text-foreground flex-1">{moduleTitle}</h2>
      <button
        onclick={handleExport}
        disabled={exporting}
        class="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground bg-muted border border-border rounded px-2.5 py-1 transition-colors disabled:opacity-50"
      >
        {#if exporting}
          <Spinner size="sm" />
          Exporting...
        {:else}
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          Export PDF
        {/if}
      </button>
    </div>
    <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
  </div>
</div>