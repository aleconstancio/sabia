<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import L from 'leaflet';
  import 'leaflet-draw';
  import Button from '$lib/ui/components/Button.svelte';
  import Dialog from '$lib/ui/components/Dialog.svelte';
  import Spinner from '$lib/ui/components/Spinner.svelte';
  import Progress from '$lib/ui/components/Progress.svelte';
  import Badge from '$lib/ui/components/Badge.svelte';
  import Input from '$lib/ui/components/Input.svelte';
  import Select from '$lib/ui/components/Select.svelte';
  import EmptyState from '$lib/ui/components/EmptyState.svelte';
  import SearchMenu from '$lib/components/SearchMenu.svelte';
  import ImageGallery from '$lib/components/ImageGallery.svelte';
  import WeatherPanel from '$lib/components/WeatherPanel.svelte';
  import SoilPanel from '$lib/components/SoilPanel.svelte';
  import MapToolbar from '$lib/components/MapToolbar.svelte';
  import RegionComparison from '$lib/components/RegionComparison.svelte';
  import LandCoverPanel from '$lib/components/LandCoverPanel.svelte';
  import TimeSlider from '$lib/components/TimeSlider.svelte';

  let mapContainer: HTMLDivElement;
  let map: L.Map;
  let drawnPolygon: any = $state(null);
  let imageResults: any[] = $state([]);
  let selectedProduct = $state('NDVI');
  let showPolygonModal = $state(false);
  let showImageGallery = $state(false);
  let showProcessingViewer = $state(false);
  let isLoading = $state(false);
  let processingProgress = $state(0);
  let processingPhase = $state('');
  let taskId = $state('');
  let rasterOverlay: any = $state(null);
  let searchError = $state('');
  let polygonCentroid = $state<{lat: number, lon: number} | null>(null);
  let showLegend = $state(false);
  let hasOverlay = $state(false);
  let pollInterval: ReturnType<typeof setInterval>;
  let showComparison = $state(false);
  let selectedImages = $state<string[]>([]);
  let comparisonFirst: any = $state(null);
  let comparisonSecond: any = $state(null);
  let showLandCover = $state(false);

  const API_URL = import.meta.env.VITE_API_URL || '/api';

  onMount(() => {
    map = L.map(mapContainer, {
      center: [-3.359202, -23.211370],
      zoom: 3,
      layers: [
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
          attribution: 'Tiles &copy; Esri',
          maxZoom: 19,
        })
      ]
    });

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

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
      drawnItems.clearLayers();
      drawnItems.addLayer(e.layer);
      drawnPolygon = e.layer.toGeoJSON().geometry.coordinates;
      const center = e.layer.getCenter();
      polygonCentroid = { lat: center.lat, lon: center.lng };
      showPolygonModal = true;
    });
  });

  onDestroy(() => {
    if (pollInterval) clearInterval(pollInterval);
  });

  async function searchImages() {
    if (!drawnPolygon) return;
    isLoading = true;
    searchError = '';
    try {
      const resp = await fetch(`${API_URL}/images/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ coordinates: drawnPolygon, limit: 50 })
      });
      const data = await resp.json();
      imageResults = data.images || [];
      showPolygonModal = false;
      showImageGallery = true;
    } catch (e) {
      searchError = 'Erro ao buscar imagens';
    } finally {
      isLoading = false;
    }
  }

  async function processImage(imageId: string) {
    isLoading = true;
    showImageGallery = false;
    showProcessingViewer = true;
    try {
      const resp = await fetch(`${API_URL}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_id: imageId,
          coordinates: drawnPolygon,
          product: selectedProduct
        })
      });
      const data = await resp.json();
      taskId = data.task_id;

      pollInterval = setInterval(async () => {
        const statusResp = await fetch(`${API_URL}/tasks/${taskId}`);
        const status = await statusResp.json();
        processingProgress = status.progress || 0;
        processingPhase = status.phase || '';

        if (status.status === 'done') {
          clearInterval(pollInterval);
          isLoading = false;
          showOverlayResult(status.result);
        } else if (status.status === 'error') {
          clearInterval(pollInterval);
          isLoading = false;
          processingPhase = 'Erro: ' + (status.error || 'Falha no processamento');
        }
      }, 1000);
    } catch (e) {
      isLoading = false;
      processingPhase = 'Erro ao iniciar processamento';
    }
  }

  function showOverlayResult(result: any) {
    if (!result || !map) return;
    const imageBounds = result.bounds as [[number, number], [number, number]];
    const filename = result.path.split('/').pop();
    const overlayUrl = `${API_URL}/overlay/${filename}`;
    const overlay = L.imageOverlay(overlayUrl, imageBounds, { opacity: 0.8 });
    map.addLayer(overlay);
    rasterOverlay = overlay;
    hasOverlay = true;
    map.fitBounds(imageBounds);
    showProcessingViewer = false;
  }

  function navigateToCity(lat: number, lng: number) {
    map.setView([lat, lng], 15);
  }

  function clearOverlay() {
    if (rasterOverlay) {
      map.removeLayer(rasterOverlay);
      rasterOverlay = null;
      hasOverlay = false;
    }
  }

  function toggleCompare() {
    showComparison = !showComparison;
    if (!showComparison) {
      selectedImages = [];
      comparisonFirst = null;
      comparisonSecond = null;
    }
  }

  function handleToggleSelect(imageId: string) {
    if (selectedImages.includes(imageId)) {
      selectedImages = selectedImages.filter(id => id !== imageId);
    } else {
      if (selectedImages.length >= 2) {
        selectedImages = [selectedImages[1], imageId];
      } else {
        selectedImages = [...selectedImages, imageId];
      }
    }
    if (selectedImages.length === 2) {
      comparisonFirst = imageResults.find(i => i.id === selectedImages[0]);
      comparisonSecond = imageResults.find(i => i.id === selectedImages[1]);
    } else {
      comparisonFirst = null;
      comparisonSecond = null;
    }
  }

  async function exportPdf(imageId: string, cloudCover: number | null) {
    const resp = await fetch(`${API_URL}/export/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_id: imageId,
        product: selectedProduct,
        date: new Date().toISOString(),
        cloud_cover: cloudCover,
        weather: { temperature: '', humidity: '', precipitation: '' },
      }),
    });
    if (resp.ok) {
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `spaceeye-${imageId.slice(0, 20)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    }
  }
</script>

<div class="absolute top-0 left-0 z-[1000] w-full">
  <div class="flex items-center justify-between bg-white/95 backdrop-blur-sm px-4 py-2 shadow-sm">
    <div class="flex items-center gap-4">
      <h1 class="text-xl font-bold text-emerald-800">SpaceEye</h1>
      <SearchMenu {navigateToCity} />
    </div>
    <div class="flex items-center gap-2">
      {#if rasterOverlay}
        <Button variant="ghost" size="sm" onclick={clearOverlay}>Limpar overlay</Button>
      {/if}
      {#if imageResults.length > 0}
        <Button variant={showComparison ? 'default' : 'ghost'} size="sm" onclick={toggleCompare}>
          {showComparison ? 'Sair' : 'Comparar'}
        </Button>
      {/if}
      {#if hasOverlay}
        <Button variant="ghost" size="sm" onclick={() => exportPdf(taskId, null)}>Exportar PDF</Button>
      {/if}
      <Badge>CBERS-4A</Badge>
    </div>
  </div>
</div>

<div bind:this={mapContainer} id="map"></div>

<MapToolbar
  bind:showLegend
  onZoomIn={() => map.zoomIn()}
  onZoomOut={() => map.zoomOut()}
  onClearOverlay={clearOverlay}
  {hasOverlay}
/>

{#if polygonCentroid && (showImageGallery || hasOverlay)}
  <div class="absolute right-4 top-20 z-[999] w-72 space-y-3">
    <WeatherPanel lat={polygonCentroid.lat} lon={polygonCentroid.lon} />
    <SoilPanel lat={polygonCentroid.lat} lon={polygonCentroid.lon} />
    <LandCoverPanel lat={polygonCentroid.lat} lon={polygonCentroid.lon} />
  </div>
{/if}

<Dialog bind:open={showPolygonModal} title="Buscar imagens deste local?">
  <div class="space-y-4">
    <div>
      <label class="text-sm font-medium">Produto</label>
      <Select bind:value={selectedProduct} options={[
        { value: 'NDVI', label: 'NDVI' },
        { value: 'TCI', label: 'TCI' },
        { value: 'NDWI', label: 'NDWI' }
      ]} />
    </div>
    {#if searchError}
      <p class="text-destructive text-sm">{searchError}</p>
    {/if}
  </div>
  {#snippet actions()}
    <Button variant="ghost" onclick={() => showPolygonModal = false}>Cancelar</Button>
    <Button onclick={searchImages} loading={isLoading}>Buscar imagens</Button>
  {/snippet}
</Dialog>

<Dialog bind:open={showImageGallery} title="Imagens relacionadas">
  {#if imageResults.length === 0}
    <EmptyState title="Nenhuma imagem" description="Não encontramos imagens para esta localidade." />
  {:else}
    <div class="space-y-2">
      {#if showComparison}
        <p class="text-xs text-muted-foreground px-2">Selecione duas imagens para comparar</p>
      {/if}
      <ImageGallery
        images={imageResults}
        {selectedProduct}
        {processImage}
        selectionMode={showComparison}
        selectedIds={selectedImages}
        onToggleSelect={handleToggleSelect}
      />
    </div>
  {/if}
</Dialog>

<Dialog bind:open={showProcessingViewer} title="Processando imagem">
  <div class="space-y-4 text-center py-8">
    <Spinner size="lg" />
    <p class="text-muted-foreground">{processingPhase || 'Iniciando...'}</p>
    <Progress value={processingProgress} />
      <p class="text-sm text-muted-foreground">{processingProgress}%</p>
    </div>
  </div>
</Dialog>

{#if showComparison && comparisonFirst && comparisonSecond}
  <div class="absolute left-4 right-4 bottom-20 z-[999]">
    <RegionComparison imageA={comparisonFirst} imageB={comparisonSecond} polygonCoords={drawnPolygon} polygonCentroid={polygonCentroid} />
  </div>
{:else if showComparison}
  <div class="absolute left-4 right-4 bottom-20 z-[999]">
    <div class="rounded-lg border border-border bg-card p-4 text-center">
      <p class="text-sm text-muted-foreground">Selecione duas imagens na galeria para comparar</p>
    </div>
  </div>
{/if}

{#if imageResults.length > 0 && !showImageGallery && !showProcessingViewer}
  <div class="absolute left-4 bottom-4 z-[999] w-72">
    <TimeSlider images={imageResults} onSelect={(id) => {
      const img = imageResults.find(i => i.id === id);
      if (img) processImage(img.id);
    }} />
  </div>
{/if}
