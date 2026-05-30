<script lang="ts">
  import { toggleMode } from 'mode-watcher';
  import { browser } from '$app/environment';
  import SearchMenu from '$lib/components/SearchMenu.svelte';
  import HistoryPanel from '$lib/components/HistoryPanel.svelte';
  import MonitoringPanel from '$lib/components/MonitoringPanel.svelte';
  import Bookmarks from '$lib/components/Bookmarks.svelte';
  import Select from '$lib/ui/components/Select.svelte';
  import Button from '$lib/ui/components/Button.svelte';
  import { mapState } from '$lib/stores/map.svelte.ts';
  import { downloadGeotiff } from '$lib/api/processing';

  let {
    navigateToCity = (lat: number, lng: number) => {},
    onToggleCompare = () => {},
    onToggleTimelapse = () => {},
    onClearOverlay = () => {},
    onExportPdf = () => {},
    showCompare = false,
    showTimelapse = false,
  } = $props();

  function copyShareLink() {
    if (!browser) return;
    const params = new URLSearchParams();
    if (mapState.polygonCoords) params.set('coords', JSON.stringify(mapState.polygonCoords));
    if (mapState.taskId) params.set('image', mapState.taskId);
    params.set('product', mapState.selectedProduct);
    navigator.clipboard.writeText(`${window.location.origin}${window.location.pathname}?${params.toString()}`);
  }

  function handleRestore(r: any) {
    if (mapState.map && r.polygonCoords) {
      mapState.polygonCoords = r.polygonCoords;
      import('leaflet').then(L => {
        const polygon = L.default.polygon(r.polygonCoords[0].map((c: number[]) => [c[1], c[0]]));
        (mapState.map as any).addLayer(polygon);
        (mapState.map as any).fitBounds(polygon.getBounds());
        mapState.polygonCentroid = r.centroid;
      });
    }
  }
</script>

<header
  class="sticky top-0 shrink-0 z-30 transition-all duration-300"
  style="background: oklch(from var(--background) l c h / 0.55); backdrop-filter: blur(16px); border-bottom: 1px solid var(--border)"
>
  <div class="flex items-center justify-between gap-4 px-4 py-2">
    <div class="flex items-center gap-3 min-w-0">
      <button
        onclick={() => mapState.sidebarOpen = !mapState.sidebarOpen}
        class="inline-flex items-center justify-center rounded-[--radius] p-2 transition-colors cursor-pointer bg-transparent border-none"
        style="color: var(--muted-foreground);"
        aria-label="Abrir menu lateral"
        aria-expanded={mapState.sidebarOpen}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
      <h1 class="text-lg font-bold" style="color: var(--primary);">SpaceEye</h1>
      <SearchMenu {navigateToCity} />
    </div>

    <div class="flex items-center gap-2">
      {#if mapState.results.length > 0}
        <Button variant={showCompare ? 'default' : 'ghost'} size="sm" onclick={onToggleCompare}>
          {showCompare ? 'Sair' : 'Comparar'}
        </Button>
        <Button variant={showTimelapse ? 'default' : 'ghost'} size="sm" onclick={onToggleTimelapse}>
          {showTimelapse ? 'Sair' : 'Timelapse'}
        </Button>
      {/if}
      {#if mapState.rasterOverlay}
        <Button variant="ghost" size="sm" onclick={onClearOverlay}>Limpar</Button>
      {/if}
      {#if mapState.hasOverlay}
        <Button variant="ghost" size="sm" onclick={copyShareLink}>Link</Button>
        <Button variant="ghost" size="sm" onclick={() => downloadGeotiff(mapState.taskId)}>GeoTIFF</Button>
        <Button variant="ghost" size="sm" onclick={onExportPdf}>PDF</Button>
      {/if}
      <Select bind:value={mapState.selectedCollection} options={[
        { value: 'cbers4a', label: 'CBERS-4A' },
        { value: 'sentinel2', label: 'Sentinel-2' },
        { value: 'landsat8', label: 'Landsat 8' },
        { value: 'landsat9', label: 'Landsat 9' },
      ]} class="!w-28 !text-xs" />
      <HistoryPanel onRestore={handleRestore} />
      <MonitoringPanel />
      <Bookmarks currentCoords={mapState.polygonCoords} />
      <button
        onclick={toggleMode}
        class="inline-flex items-center justify-center rounded-[--radius] p-2 transition-colors cursor-pointer bg-transparent border-none"
        style="color: var(--muted-foreground);"
        aria-label="Alternar tema"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
    </div>
  </div>
</header>
