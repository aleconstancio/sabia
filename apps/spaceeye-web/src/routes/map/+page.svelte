<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import SpaceEyeShell from '$lib/layout/SpaceEyeShell.svelte';
  import Header from '$lib/layout/Header.svelte';
  import { SearchPanel, ResultsPanel, AnalyticsPanel, HistorySidebar } from '$lib/components/sidebar';
  import MapToolbar from '$lib/components/MapToolbar.svelte';
  import OnboardingDialog from '$lib/components/OnboardingDialog.svelte';
  import ErrorBoundary from '$lib/ui/components/ErrorBoundary.svelte';
  import { mapState } from '$lib/stores/map.svelte';
  import { searchImages, exportPdf } from '$lib/api/processing';
  import { createProfile } from '$lib/api/client';
  import { bookmarksStore } from '$lib/stores/bookmarks.svelte';
  import { toast } from 'svelte-sonner';
  import { logger } from '$lib/utils/logger';
  import { MapView, MapDialogs, MapOverlays, PromptDialog } from '$lib/components/map';

  let mapView: MapView;
  let measureMode = $state(false);
  let mouseCoords = $state({ lat: 0, lng: 0 });
  let currentBasemap = $state('satellite');
  let layerOpacity = $state(0.8);
  let showTimelapse = $state(false);
  let showOnboarding = $state(false);
  let isSavingProfile = $state(false);

  const tileLayers: Record<string, string> = {
    satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    osm: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    dark: 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
  };
  const tileAttributions: Record<string, string> = {
    satellite: 'Tiles &copy; Esri',
    osm: '&copy; OpenStreetMap contributors',
    dark: '&copy; Stadia Maps',
  };

  let showPromptDialog = $state(false);
  let promptValue = $state('');
  let promptLabel = $state('');
  let onPromptSubmit: ((value: string) => void) | null = $state(null);

  function navigateToCity(lat: number, lng: number) {
    mapView?.getMap()?.flyTo([lat, lng], 15, { duration: 1.5 });
  }

  function toggleMeasure() {
    measureMode = !measureMode;
    const map = mapView?.getMap();
    if (map) {
      map.getContainer().style.cursor = measureMode ? 'crosshair' : '';
    }
  }

  function handleMeasure(coords: { lat: number; lng: number }) {
    mouseCoords = coords;
  }

  function switchBasemap(b: string) {
    currentBasemap = b;
    const map = mapView?.getMap();
    if (map) {
      // Remove the current tile layer by iterating through layers
      map.eachLayer((layer: L.Layer) => {
        if (layer instanceof L.TileLayer) {
          map.removeLayer(layer);
        }
      });
      // Add the new tile layer
      L.tileLayer(tileLayers[b], { attribution: tileAttributions[b], maxZoom: 19 }).addTo(map);
    }
  }

  function setOpacity(o: number) {
    layerOpacity = o;
    if (mapState.rasterOverlay) {
      mapState.rasterOverlay.setOpacity(o);
    }
  }

  function clearOverlay() {
    const map = mapView?.getMap();
    if (mapState.rasterOverlay && map) {
      map.removeLayer(mapState.rasterOverlay);
      mapState.rasterOverlay = null;
      mapState.hasOverlay = false;
    }
  }

  function toggleCompare() {
    mapState.showComparison = !mapState.showComparison;
    if (!mapState.showComparison) {
      mapState.selectedIds = [];
      mapState.comparisonFirst = null;
      mapState.comparisonSecond = null;
    }
  }

  async function doExportPdf() {
    await exportPdf(mapState.taskId, null);
  }

  async function saveAsProfile() {
    if (!mapState.polygonCoords || isSavingProfile) return;
    promptLabel = 'Nome para este perfil:';
    promptValue = '';
    showPromptDialog = true;
    onPromptSubmit = async (name: string) => {
      if (!name?.trim()) return;
      isSavingProfile = true;
      try {
        await createProfile({
          name: name.trim(),
          polygon: { type: 'Polygon', coordinates: mapState.polygonCoords! },
          satellite_data: mapState.lastStats ? {
            product: mapState.selectedProduct,
            stats: mapState.lastStats,
          } : undefined,
        });
        toast.success('Perfil salvo com sucesso!');
      } catch (e: unknown) {
        logger.error('saveAsProfile error:', e);
        toast.error('Falha ao salvar perfil');
      } finally {
        isSavingProfile = false;
      }
    };
  }

  function handlePromptSubmit(value: string) {
    if (onPromptSubmit) onPromptSubmit(value);
    onPromptSubmit = null;
  }

  function restoreBookmark(coords: number[][][], name: string) {
    mapState.polygonCoords = coords;
    const map = mapView?.getMap();
    const drawnItems = mapView?.getDrawnItems();
    if (map && mapState.polygonCoords) {
      if (drawnItems) {
        drawnItems.clearLayers();
      }
      const L = window.L;
      if (!L) return;
      const polygon = L.polygon(mapState.polygonCoords[0].map((c: number[]) => [c[1], c[0]]));
      map.addLayer(polygon);
      drawnItems?.addLayer(polygon);
      map.fitBounds(polygon.getBounds());
      const center = polygon.getCenter();
      mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
      mapState.showPolygonModal = true;
    }
  }

  function saveCurrentPolygon() {
    if (!mapState.polygonCoords) return;
    promptLabel = 'Nome para este local:';
    promptValue = '';
    showPromptDialog = true;
    onPromptSubmit = (name: string) => {
      if (name && mapState.polygonCoords) bookmarksStore.add(name, mapState.polygonCoords);
    };
  }

  onMount(() => {
    if (browser && !localStorage.getItem('spaceeye_onboarded')) {
      showOnboarding = true;
    }
  });
</script>

<SpaceEyeShell>
  {#snippet sidebarContent()}
    <SearchPanel />
    <ResultsPanel />
    <AnalyticsPanel />
    <HistorySidebar />
  {/snippet}

  <Header
    {navigateToCity}
    onToggleCompare={toggleCompare}
    onToggleTimelapse={() => showTimelapse = !showTimelapse}
    onClearOverlay={clearOverlay}
    onExportPdf={doExportPdf}
    onSaveProfile={saveAsProfile}
    isSavingProfile={isSavingProfile}
    showCompare={mapState.showComparison}
    showTimelapse={showTimelapse}
  />

  <ErrorBoundary>
    <MapView
      bind:this={mapView}
      {measureMode}
      onMeasure={handleMeasure}
    />
  </ErrorBoundary>

  {#if !mapState.polygonCoords && !mapState.hasOverlay && !mapState.isLoading}
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none z-[100]">
      <div class="text-center space-y-3 bg-background/80 backdrop-blur-sm rounded-xl p-8 border border-border">
        <div class="text-4xl">🌍</div>
        <h2 class="text-lg font-semibold">Desenhe uma área no mapa</h2>
        <p class="text-sm text-muted-foreground max-w-xs">
          Use a ferramenta de polígono ou retângulo no canto superior esquerdo do mapa para selecionar uma região.
        </p>
        <div class="flex items-center justify-center gap-2 text-xs text-muted-foreground">
          <kbd class="px-1.5 py-0.5 rounded border border-border bg-muted text-[10px]">Draw Polygon</kbd>
          <span>ou</span>
          <kbd class="px-1.5 py-0.5 rounded border border-border bg-muted text-[10px]">Draw Rectangle</kbd>
        </div>
      </div>
    </div>
  {/if}
</SpaceEyeShell>

<MapToolbar
  bind:showLegend={mapState.showLegend}
  onZoomIn={() => mapView?.getMap()?.zoomIn()}
  onZoomOut={() => mapView?.getMap()?.zoomOut()}
  onClearOverlay={clearOverlay}
  onMeasure={toggleMeasure}
  hasOverlay={mapState.hasOverlay}
  product={mapState.selectedProduct}
  basemap={currentBasemap}
  onBasemapChange={switchBasemap}
  opacity={layerOpacity}
  onOpacityChange={setOpacity}
/>

<MapDialogs
  drawnItems={mapView?.getDrawnItems() ?? null}
  onSaveLocal={saveCurrentPolygon}
/>

<MapOverlays
  {showTimelapse}
  {measureMode}
  {mouseCoords}
/>

<PromptDialog
  bind:open={showPromptDialog}
  bind:value={promptValue}
  label={promptLabel}
  onSubmit={handlePromptSubmit}
/>

<OnboardingDialog bind:open={showOnboarding} />