import L from 'leaflet';
import { mapState } from '$lib/stores/map.svelte';

const API_URL = import.meta.env.VITE_API_URL || '/api';

export async function searchImages() {
  if (!mapState.polygonCoords) return;
  mapState.isLoading = true;
  mapState.searchError = '';
  try {
    const resp = await fetch(`${API_URL}/images/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        coordinates: mapState.polygonCoords,
        limit: 50,
        collections: mapState.selectedCollection ? [mapState.selectedCollection] : undefined,
      })
    });
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    mapState.results = data.images || [];
    mapState.showPolygonModal = false;
    mapState.showImageGallery = true;
  } catch (e: any) {
    mapState.searchError = e.message || 'Erro ao buscar imagens';
  } finally {
    mapState.isLoading = false;
  }
}

export async function processImage(imageId: string) {
  mapState.isLoading = true;
  mapState.showImageGallery = false;
  mapState.showProcessingViewer = true;

  let pollInterval: ReturnType<typeof setInterval>;

  try {
    const resp = await fetch(`${API_URL}/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_id: imageId,
        coordinates: mapState.polygonCoords,
        product: mapState.selectedProduct,
      })
    });
    if (!resp.ok) throw new Error('Process request failed');
    const data = await resp.json();
    mapState.taskId = data.task_id;

    pollInterval = setInterval(async () => {
      if (!mapState.showProcessingViewer) {
        clearInterval(pollInterval);
        mapState.isLoading = false;
        return;
      }
      try {
        const sr = await fetch(`${API_URL}/tasks/${data.task_id}`);
        const status = await sr.json();
        mapState.processingProgress = status.progress || 0;
        mapState.processingPhase = status.phase || '';

        if (status.status === 'done') {
          clearInterval(pollInterval);
          mapState.isLoading = false;
          mapState.showProcessingViewer = false;
          showOverlayResult(status.result);
        } else if (status.status === 'error') {
          clearInterval(pollInterval);
          mapState.isLoading = false;
          mapState.processingPhase = 'Erro: ' + (status.error || 'Falha no processamento');
        }
      } catch {
        clearInterval(pollInterval);
        mapState.isLoading = false;
      }
    }, 1000);
  } catch (e: any) {
    mapState.isLoading = false;
    mapState.processingPhase = 'Erro ao iniciar processamento';
  }
}

export function showOverlayResult(result: any) {
  if (!result || !mapState.map) return;
  const bounds = result.bounds as [[number, number], [number, number]];
  const map = mapState.map as any;
  const filename = result.path.split('/').pop();
  const overlay = L.imageOverlay(`${API_URL}/overlay/${filename}`, bounds, { opacity: 0.8 });
  map.addLayer(overlay);
  mapState.rasterOverlay = overlay;
  mapState.hasOverlay = true;
  mapState.lastOverlayPath = result.path;
  map.flyToBounds(bounds, { duration: 1.5 });
}

export async function exportPdf(imageId: string, cloudCover: number | null) {
  const weather = mapState.lastWeatherData;
  const body: any = {
    image_id: imageId,
    product: mapState.selectedProduct,
    date: new Date().toISOString(),
    cloud_cover: cloudCover,
    weather: weather ? {
      temperature: weather.current?.temperature_2m,
      humidity: weather.current?.relative_humidity_2m,
      precipitation: weather.current?.precipitation,
    } : {},
  };
  if (mapState.lastOverlayPath) body.overlay_path = mapState.lastOverlayPath;
  const resp = await fetch(`${API_URL}/export/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
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

export async function downloadGeotiff(taskId: string) {
  const API_URL = import.meta.env.VITE_API_URL || '/api';
  const resp = await fetch(`${API_URL}/download/${taskId}/geotiff`);
  if (resp.ok) {
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `spaceeye-${taskId.slice(0, 8)}.tif`;
    a.click();
    URL.revokeObjectURL(url);
  }
}
