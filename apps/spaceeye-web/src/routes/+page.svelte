<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import L from 'leaflet';
  import 'leaflet-draw';
  import SpaceEyeShell from '$lib/layout/SpaceEyeShell.svelte';
  import Header from '$lib/layout/Header.svelte';
  import { SearchPanel, ResultsPanel, AnalyticsPanel, HistorySidebar } from '$lib/components/sidebar';
  import Button from '$lib/ui/components/Button.svelte';
  import Dialog from '$lib/ui/components/Dialog.svelte';
  import Spinner from '$lib/ui/components/Spinner.svelte';
  import Progress from '$lib/ui/components/Progress.svelte';
  import Badge from '$lib/ui/components/Badge.svelte';
  import Select from '$lib/ui/components/Select.svelte';
  import EmptyState from '$lib/ui/components/EmptyState.svelte';
  import ImageGallery from '$lib/components/ImageGallery.svelte';
  import WeatherPanel from '$lib/components/WeatherPanel.svelte';
  import SoilPanel from '$lib/components/SoilPanel.svelte';
  import MapToolbar from '$lib/components/MapToolbar.svelte';
  import RegionComparison from '$lib/components/RegionComparison.svelte';
  import LandCoverPanel from '$lib/components/LandCoverPanel.svelte';
  import TimeSlider from '$lib/components/TimeSlider.svelte';
  import NdviTimeline from '$lib/components/NdviTimeline.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import HistogramPanel from '$lib/components/HistogramPanel.svelte';
  import { mapState } from '$lib/stores/map.svelte';
  import { searchImages, processImage, exportPdf } from '$lib/api/processing';
  import { addBookmark } from '$lib/stores/bookmarks.svelte.ts';
  import TimelapsePlayer from '$lib/components/TimelapsePlayer.svelte';
  import SwipeComparison from '$lib/components/SwipeComparison.svelte';

  let mapContainer: HTMLDivElement;
  let map: L.Map | null = $state(null);
  let measureMode = $state(false);
  let mouseCoords = $state({ lat: 0, lng: 0 });
  let currentBasemap = $state('satellite');
  let layerOpacity = $state(0.8);
  let tileLayer: L.TileLayer | null = $state(null);
  let showTimelapse = $state(false);
  let timelapseOverlay = $state<any>(null);
  let useSwipe = $state(false);
  let drawnItemsGroup = $state<L.FeatureGroup | null>(null);

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

  onMount(() => {
    tileLayer = L.tileLayer(tileLayers.satellite, { attribution: tileAttributions.satellite, maxZoom: 19 });
    map = L.map(mapContainer, {
      center: [-3.359202, -23.211370],
      zoom: 3,
      layers: [tileLayer],
      keyboard: false,
    });

    mapState.map = map;

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    drawnItemsGroup = drawnItems;

    map.on('mousemove', (e: any) => {
      if (measureMode) {
        mouseCoords = { lat: e.latlng.lat.toFixed(4), lng: e.latlng.lng.toFixed(4) };
      }
    });

    const drawControl = new L.Control.Draw({
      edit: { featureGroup: drawnItems },
      draw: {
        polygon: true,
        polyline: false,
        rectangle: true,
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
      (mapState.rasterOverlay as any).setOpacity(o);
    }
  }

  function clearOverlay() {
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

  function handleToggleSelect(imageId: string) {
    const ids = mapState.selectedIds;
    if (ids.includes(imageId)) {
      mapState.selectedIds = ids.filter(id => id !== imageId);
    } else {
      if (ids.length >= 2) {
        mapState.selectedIds = [ids[1], imageId];
      } else {
        mapState.selectedIds = [...ids, imageId];
      }
    }
    if (mapState.selectedIds.length === 2) {
      mapState.comparisonFirst = mapState.results.find(i => i.id === mapState.selectedIds[0]);
      mapState.comparisonSecond = mapState.results.find(i => i.id === mapState.selectedIds[1]);
    } else {
      mapState.comparisonFirst = null;
      mapState.comparisonSecond = null;
    }
  }

  function onWeatherData(data: any) {
    mapState.lastWeatherData = data;
  }

  async function doExportPdf() {
    await exportPdf(mapState.taskId, null);
  }

  function updateShareUrl(imageId: string) {
    if (!browser || !mapState.polygonCoords) return;
    const params = new URLSearchParams();
    params.set('coords', JSON.stringify(mapState.polygonCoords));
    params.set('image', imageId);
    params.set('product', mapState.selectedProduct);
    const url = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', url);
  }

  function copyShareLink() {
    if (!browser || !mapState.polygonCoords || !mapState.taskId) return;
    const params = new URLSearchParams();
    params.set('coords', JSON.stringify(mapState.polygonCoords));
    params.set('image', mapState.taskId);
    params.set('product', mapState.selectedProduct);
    const url = `${window.location.origin}${window.location.pathname}?${params.toString()}`;
    navigator.clipboard.writeText(url);
  }

  function restoreBookmark(coords: number[][][], name: string) {
    mapState.polygonCoords = coords;
    if (map && mapState.polygonCoords) {
      const polygon = L.polygon(mapState.polygonCoords[0].map((c: number[]) => [c[1], c[0]]));
      map.addLayer(polygon);
      map.fitBounds(polygon.getBounds());
      const center = polygon.getCenter();
      mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
      mapState.showPolygonModal = true;
    }
  }

  function saveCurrentPolygon() {
    if (!mapState.polygonCoords) return;
    const name = prompt('Nome para este local:');
    if (name) addBookmark(name, mapState.polygonCoords);
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
    mapState.polygonCoords = geoJSON.geometry.coordinates;
    mapState.polygonCentroid = { lat: polygon.getCenter().lat, lon: polygon.getCenter().lng };
  }

  $effect(() => {
    if (!browser) return;
    const params = new URLSearchParams(window.location.search);
    const coords = params.get('coords');
    const image = params.get('image');
    const product = params.get('product');

    if (coords && image && product) {
      try {
        const parsed = JSON.parse(coords);
        mapState.polygonCoords = parsed;
        mapState.selectedProduct = product;
        if (map && mapState.polygonCoords) {
          const polygon = L.polygon(mapState.polygonCoords[0].map((c: number[]) => [c[1], c[0]]));
          map.addLayer(polygon);
          map.fitBounds(polygon.getBounds());
          const center = polygon.getCenter();
          mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
        }
        searchImages().then(() => {
          processImage(image);
        });
      } catch { /* invalid params */ }
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
    onToggleSidebar={() => {}}
    onToggleCompare={toggleCompare}
    onToggleTimelapse={() => showTimelapse = !showTimelapse}
    onClearOverlay={clearOverlay}
    onExportPdf={doExportPdf}
    showCompare={mapState.showComparison}
    showTimelapse={showTimelapse}
  />

  <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
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

{#if mapState.polygonCentroid && (mapState.showImageGallery || mapState.hasOverlay)}
  <div class="absolute right-4 top-20 z-[999] w-72 space-y-3">
    <WeatherPanel lat={mapState.polygonCentroid.lat} lon={mapState.polygonCentroid.lon} {onWeatherData} />
    <SoilPanel lat={mapState.polygonCentroid.lat} lon={mapState.polygonCentroid.lon} polygonCoords={mapState.polygonCoords} />
    <LandCoverPanel lat={mapState.polygonCentroid.lat} lon={mapState.polygonCentroid.lon} polygonCoords={mapState.polygonCoords} />
  </div>
{/if}

<Dialog bind:open={mapState.showPolygonModal} title="Buscar imagens deste local?">
  <div class="space-y-4">
    <div>
      <label class="text-sm font-medium">Produto</label>
      <Select bind:value={mapState.selectedProduct} options={[
  { value: 'NDVI', label: 'NDVI - Veg. Index' },
  { value: 'TCI', label: 'TCI - True Color' },
  { value: 'NDWI', label: 'NDWI - Water Index' },
  { value: 'SAVI', label: 'SAVI - Soil Adj. Veg.' },
  { value: 'EVI', label: 'EVI - Enhanced Veg.' },
  { value: 'MSAVI2', label: 'MSAVI2 - Mod. SAVI' },
  { value: 'VARI', label: 'VARI - Visible Atmos.' },
  { value: 'MNDWI', label: 'MNDWI - Mod. Water' },
  { value: 'CIR', label: 'CIR - Color Infrared' },
  { value: 'NBR', label: 'NBR - Burn Ratio' },
  { value: 'NDMI', label: 'NDMI - Moisture' },
]} />
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
  {#snippet actions()}
    <Button variant="ghost" onclick={() => mapState.showPolygonModal = false}>Cancelar</Button>
    <Button variant="ghost" onclick={saveCurrentPolygon}>Salvar local</Button>
    <Button onclick={searchImages} loading={mapState.isLoading}>Buscar imagens</Button>
  {/snippet}
</Dialog>

<Dialog bind:open={mapState.showImageGallery} title="Imagens relacionadas">
  {#if mapState.results.length === 0}
    <EmptyState title="Nenhuma imagem" description="Não encontramos imagens para esta localidade." />
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
</Dialog>

<Dialog bind:open={mapState.showProcessingViewer} title="Processando imagem">
  <div class="space-y-4 text-center py-8">
    <Spinner size="lg" />
    <p class="text-muted-foreground">{mapState.processingPhase || 'Iniciando...'}</p>
    <Progress value={mapState.processingProgress} />
      <p class="text-sm text-muted-foreground">{mapState.processingProgress}%</p>
    {#if mapState.lastStats}
      <HistogramPanel stats={mapState.lastStats} product={mapState.selectedProduct} />
    {/if}
  </div>
</Dialog>

{#if measureMode}
  <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-[1000] bg-black/80 text-white text-xs px-3 py-1 rounded-full font-mono">
    {mouseCoords.lat}, {mouseCoords.lng}
  </div>
{/if}

{#if mapState.showComparison && mapState.comparisonFirst && mapState.comparisonSecond}
  <div class="absolute left-4 right-4 bottom-20 z-[999]">
    <div class="flex justify-end mb-1">
      <Button variant="ghost" size="sm" onclick={() => useSwipe = !useSwipe}>
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
    <TimelapsePlayer images={mapState.results} polygonCoords={mapState.polygonCoords} product={mapState.selectedProduct} onFrameChange={(id) => {
      const img = mapState.results.find(i => i.id === id);
      if (img) processImage(img.id);
    }} />
  </div>
{/if}
