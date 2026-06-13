<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import L from 'leaflet';
  import SpaceEyeShell from '$lib/layout/SpaceEyeShell.svelte';
  import Header from '$lib/layout/Header.svelte';
  import { SearchPanel, ResultsPanel, AnalyticsPanel, HistorySidebar } from '$lib/components/sidebar';
  import { Button } from '$lib/components/ui/button';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Badge } from '$lib/components/ui/badge';
  import { Progress } from '$lib/components/ui/progress';
  import * as Select from '$lib/components/ui/select';
  import ImageGallery from '$lib/components/ImageGallery.svelte';
  import MapToolbar from '$lib/components/MapToolbar.svelte';
  import RegionComparison from '$lib/components/RegionComparison.svelte';
  import TimeSlider from '$lib/components/TimeSlider.svelte';
  import NdviTimeline from '$lib/components/NdviTimeline.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import HistogramPanel from '$lib/components/HistogramPanel.svelte';
  import OnboardingDialog from '$lib/components/OnboardingDialog.svelte';
  import ProductInfo from '$lib/components/ProductInfo.svelte';
  import ErrorBoundary from '$lib/ui/components/ErrorBoundary.svelte';
  import { toast } from 'svelte-sonner';
  import { mapState } from '$lib/stores/map.svelte';
  import { searchImages, processImage, exportPdf } from '$lib/api/processing';
  import { createProfile } from '$lib/api/client';
  import { bookmarksStore } from '$lib/stores/bookmarks.svelte';
  import { handleToggleSelect } from '$lib/helpers/comparison';
  import TimelapsePlayer from '$lib/components/TimelapsePlayer.svelte';
  import SwipeComparison from '$lib/components/SwipeComparison.svelte';
  import { SPECTRAL_PRODUCTS } from '$lib/constants';

  let mapContainer: HTMLDivElement;
  let map: L.Map | null = $state(null);
  let measureMode = $state(false);
  let mouseCoords = $state({ lat: 0, lng: 0 });
  let currentBasemap = $state('satellite');
  let layerOpacity = $state(0.8);
  let tileLayer: L.TileLayer | null = $state(null);
  let showTimelapse = $state(false);
  let useSwipe = $state(false);
  let drawnItemsGroup = $state<L.FeatureGroup | null>(null);
  let showOnboarding = $state(false);
  let isSavingProfile = $state(false);
  let showPromptDialog = $state(false);
  let promptValue = $state('');
  let promptLabel = $state('');
  let onPromptSubmit: ((value: string) => void) | null = $state(null);

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

  onMount(async () => {
    await import('leaflet-draw');
    tileLayer = L.tileLayer(tileLayers.satellite, { attribution: tileAttributions.satellite, maxZoom: 19 });
    map = L.map(mapContainer, {
      center: [-3.359202, -23.211370],
      zoom: 3,
      layers: [tileLayer],
    });

    mapState.map = map;

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    drawnItemsGroup = drawnItems;

    if (browser) {
      const params = new URLSearchParams(window.location.search);
      const coords = params.get('coords');
      const image = params.get('image');
      const product = params.get('product');

      if (coords && image && product) {
        try {
          const parsed = JSON.parse(coords);
          if (!Array.isArray(parsed) || !parsed.every((ring: unknown) =>
            Array.isArray(ring) && ring.every((coord: unknown) =>
              Array.isArray(coord) && coord.length >= 2 && coord.every((v: unknown) => typeof v === 'number')
            )
          )) {
            toast.error('Coordenadas inválidas no link compartilhado');
            return;
          }
          const allowedProducts = SPECTRAL_PRODUCTS.map(p => p.value);
          if (!allowedProducts.includes(product)) {
            toast.error('Produto inválido no link compartilhado');
            return;
          }
          mapState.polygonCoords = parsed;
          mapState.selectedProduct = product;
          const polygon = L.polygon(parsed[0].map((c: number[]) => [c[1], c[0]]));
          map.addLayer(polygon);
          map.fitBounds(polygon.getBounds());
          const center = polygon.getCenter();
          mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
          searchImages().then(() => {
            processImage(image);
          }).catch((e) => {
            console.warn('Share URL auto-process failed:', e);
          });
        } catch(e) { console.warn('Invalid share URL params:', e); }
      }
    }

    map.on('mousemove', (e: any) => {
      if (measureMode) {
        mouseCoords = { lat: e.latlng.lat.toFixed(4), lng: e.latlng.lng.toFixed(4) };
      }
    });

    const drawControl = new L.Control.Draw({
      edit: { featureGroup: drawnItems },
      draw: {
        polygon: {},
        polyline: false,
        rectangle: {},
        circle: false,
        circlemarker: false,
        marker: false,
      }
    });
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, (e: any) => {
      drawnItems.addLayer(e.layer);
      mapState.polygonCoords = e.layer.toGeoJSON().geometry.coordinates;
      const center = e.layer.getCenter();
      mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
      mapState.showPolygonModal = true;
    });
  });

  onDestroy(() => {
    if (map) {
      map.remove();
      map = null;
    }
  });

  function navigateToCity(lat: number, lng: number) {
    map?.flyTo([lat, lng], 15, { duration: 1.5 });
  }

  function toggleMeasure() {
    measureMode = !measureMode;
    if (map) {
      map.getContainer().style.cursor = measureMode ? 'crosshair' : '';
    }
  }

  function switchBasemap(b: string) {
    currentBasemap = b;
    if (map && tileLayer) {
      map.removeLayer(tileLayer);
      tileLayer = L.tileLayer(tileLayers[b], { attribution: tileAttributions[b], maxZoom: 19 }).addTo(map);
    }
  }

  function setOpacity(o: number) {
    layerOpacity = o;
    if (mapState.rasterOverlay) {
      mapState.rasterOverlay.setOpacity(o);
    }
  }

  function clearOverlay() {
    if (mapState.rasterOverlay && map) {
      map.removeLayer(mapState.rasterOverlay as L.Layer);
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
        console.error('saveAsProfile error:', e);
        toast.error('Falha ao salvar perfil');
      } finally {
        isSavingProfile = false;
      }
    };
  }

  function restoreBookmark(coords: number[][][], name: string) {
    mapState.polygonCoords = coords;
    if (map && mapState.polygonCoords) {
      if (drawnItemsGroup) {
        drawnItemsGroup.clearLayers();
      }
      const polygon = L.polygon(mapState.polygonCoords[0].map((c: number[]) => [c[1], c[0]]));
      map.addLayer(polygon);
      drawnItemsGroup?.addLayer(polygon);
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

  function handlePromptSubmit(e: Event) {
    e.preventDefault();
    if (onPromptSubmit) onPromptSubmit(promptValue);
    showPromptDialog = false;
    onPromptSubmit = null;
    promptValue = '';
  }

  function unionPolygons() {
    if (!drawnItemsGroup) return;
    const layers = drawnItemsGroup.getLayers();
    if (layers.length < 2) return;

    const bounds = drawnItemsGroup.getBounds();
    const polygon = L.rectangle(bounds);

    drawnItemsGroup.clearLayers();
    drawnItemsGroup.addLayer(polygon);

    const geoJSON = polygon.toGeoJSON();
    mapState.polygonCoords = geoJSON.geometry.coordinates as number[][][];
    mapState.polygonCentroid = { lat: polygon.getCenter().lat, lon: polygon.getCenter().lng };
  }

  $effect(() => {
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
    <div bind:this={mapContainer} id="map" class="flex-1 min-h-0" role="application" aria-label="Mapa interativo SpaceEye"></div>
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
  onZoomIn={() => map?.zoomIn()}
  onZoomOut={() => map?.zoomOut()}
  onClearOverlay={clearOverlay}
  onMeasure={toggleMeasure}
  hasOverlay={mapState.hasOverlay}
  product={mapState.selectedProduct}
  basemap={currentBasemap}
  onBasemapChange={switchBasemap}
  opacity={layerOpacity}
  onOpacityChange={setOpacity}
/>

<Dialog.Root bind:open={mapState.showPolygonModal}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" />
    <Dialog.Content class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card border border-border p-6 shadow-lg">
      <Dialog.Title>Buscar imagens deste local?</Dialog.Title>
      <div class="space-y-4">
        <div>
          <label for="product-select" class="text-sm font-medium">Produto</label>
          <Select.Root type="single" bind:value={mapState.selectedProduct}>
            <Select.Trigger class="w-full">
              Produto...
            </Select.Trigger>
            <Select.Content>
              {#each SPECTRAL_PRODUCTS as option}
                <Select.Item value={option.value}>{option.label}</Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
          <ProductInfo product={mapState.selectedProduct} />
        </div>
        {#if drawnItemsGroup && drawnItemsGroup.getLayers().length > 1}
          <Button variant="ghost" onclick={unionPolygons}>Unir áreas</Button>
        {/if}
        {#if mapState.searchError}
          <div class="flex items-center gap-2 mt-2">
            <p class="text-destructive text-sm flex-1">{mapState.searchError}</p>
            <Button size="sm" variant="outline" onclick={searchImages}>Tentar novamente</Button>
          </div>
        {/if}
      </div>
      <Dialog.Footer>
        <Button variant="ghost" onclick={() => mapState.showPolygonModal = false}>Cancelar</Button>
        <Button variant="ghost" onclick={saveCurrentPolygon}>Salvar local</Button>
        <Button onclick={searchImages}>
          {#if mapState.isLoading}<span class="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full"></span>{/if}
          Buscar imagens
        </Button>
      </Dialog.Footer>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={mapState.showImageGallery}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" />
    <Dialog.Content class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card border border-border p-6 shadow-lg">
      <Dialog.Title>Imagens relacionadas</Dialog.Title>
      {#if mapState.results.length === 0}
        <div class="flex flex-col items-center justify-center py-16 text-center">
          <h3 class="text-lg font-semibold text-foreground mb-1">Nenhuma imagem</h3>
          <p class="text-sm text-muted-foreground max-w-sm">Não encontramos imagens para esta localidade.</p>
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
            <p class="text-xs text-muted-foreground px-2">Selecione duas imagens para comparar</p>
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
    <Dialog.Content class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card border border-border p-6 shadow-lg">
      <Dialog.Title>Processando imagem</Dialog.Title>
      <div class="space-y-4 text-center py-8">
        <span class="animate-spin h-10 w-10 border-[3px] border-primary border-t-transparent rounded-full inline-block"></span>
        <p class="text-muted-foreground" aria-live="polite">{mapState.processingPhase || 'Iniciando...'}</p>
        <Progress value={mapState.processingProgress} />
        <p class="text-sm text-muted-foreground">{mapState.processingProgress}%</p>
        {#if mapState.lastStats}
          <HistogramPanel stats={mapState.lastStats} product={mapState.selectedProduct} />
        {/if}
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

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

{#if showPromptDialog}
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <div class="fixed inset-0 z-[2000] flex items-center justify-center bg-black/50" role="dialog" aria-modal="true" tabindex="-1" onkeydown={(e) => { if (e.key === 'Escape') { showPromptDialog = false; onPromptSubmit = null; } }}>
    <form onsubmit={handlePromptSubmit} class="bg-card border border-border rounded-lg p-6 shadow-xl w-80 space-y-4">
      <label class="text-sm font-medium" for="prompt-input">{promptLabel}</label>
      <input
        id="prompt-input"
        type="text"
        bind:value={promptValue}
        class="w-full px-3 py-2 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
      />
      <div class="flex justify-end gap-2">
        <Button type="button" variant="ghost" onclick={() => { showPromptDialog = false; onPromptSubmit = null; }}>Cancelar</Button>
        <Button type="submit">OK</Button>
      </div>
    </form>
  </div>
{/if}

<OnboardingDialog bind:open={showOnboarding} />
