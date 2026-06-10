import L from 'leaflet';
import { mapState } from '$lib/stores/map.svelte';
import { addRecord } from '$lib/stores/history.svelte';
import type { Map as LeafletMap } from 'leaflet';

interface SearchRequestBody {
  coordinates: number[][][];
  limit: number;
  collections?: string[];
  date_from?: string;
  date_to?: string;
  max_cloud?: number;
  sort_by?: string;
  sort_order?: string;
}

interface ExportPdfRequestBody {
  image_id: string;
  product: string;
  date: string;
  cloud_cover: number | null;
  weather?: Record<string, unknown>;
  overlay_path?: string;
}

interface ProcessResult {
  bounds: [[number, number], [number, number]];
  path: string;
  statistics?: Record<string, unknown>;
}

const API_URL = import.meta.env.VITE_API_URL || '/api';

export async function searchImages() {
  if (!mapState.polygonCoords) return;
  mapState.isLoading = true;
  mapState.searchError = '';
  try {
    const body: SearchRequestBody = { coordinates: mapState.polygonCoords, limit: 50 };
    if (mapState.selectedCollection) body.collections = [mapState.selectedCollection];
    if (mapState.filterDateFrom) body.date_from = mapState.filterDateFrom;
    if (mapState.filterDateTo) body.date_to = mapState.filterDateTo;
    if (mapState.filterMaxCloud !== undefined) body.max_cloud = mapState.filterMaxCloud;
    body.sort_by = mapState.filterSortBy || 'acquired_at';
    body.sort_order = mapState.filterSortOrder || 'desc';

    const resp = await fetch(`${API_URL}/images/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    mapState.results = data.images || [];
    mapState.showPolygonModal = false;
    mapState.showImageGallery = true;
  } catch (e: unknown) {
    mapState.searchError = (e as Error).message || 'Erro ao buscar imagens';
  } finally {
    mapState.isLoading = false;
  }
}

export async function processImage(imageId: string) {
  mapState.isLoading = true;
  mapState.showImageGallery = false;
  mapState.showProcessingViewer = true;

  let pollInterval: ReturnType<typeof setInterval>;
  let attempts = 0;
  const MAX = 120;

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
      if (++attempts >= MAX) {
        clearInterval(pollInterval);
        mapState.isLoading = false;
        mapState.processingPhase = 'Timeout';
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
          addRecord({
            imageId: imageId,
            product: mapState.selectedProduct,
            collection: mapState.selectedCollection || 'unknown',
            cloudCover: null,
            polygonCoords: mapState.polygonCoords || [],
            centroid: mapState.polygonCentroid,
            stats: status.result?.statistics,
          });
        } else if (status.status === 'error') {
          clearInterval(pollInterval);
          mapState.isLoading = false;
          mapState.processingPhase = 'Erro: ' + (status.error || 'Falha no processamento');
        }
      } catch {
        clearInterval(pollInterval);
        mapState.isLoading = false;
        mapState.processingPhase = 'Falha na conexao';
      }
    }, 1000);
  } catch {
    mapState.isLoading = false;
    mapState.processingPhase = 'Erro ao iniciar processamento';
  }
}

export function showOverlayResult(result: ProcessResult) {
  if (!result || !mapState.map) return;
  const bounds = result.bounds;
  const map = mapState.map as LeafletMap;
  const filename = result.path.split('/').pop();
  const overlay = L.imageOverlay(`${API_URL}/overlay/${filename}`, bounds, { opacity: 0.8 });
  map.addLayer(overlay);
  mapState.rasterOverlay = overlay;
  mapState.hasOverlay = true;
  mapState.lastOverlayPath = result.path;
  mapState.lastStats = result.statistics || null;
  map.flyToBounds(bounds, { duration: 1.5 });
}

export async function exportPdf(imageId: string, cloudCover: number | null) {
  const weather = mapState.lastWeatherData;
  const body: ExportPdfRequestBody = {
    image_id: imageId,
    product: mapState.selectedProduct,
    date: new Date().toISOString(),
    cloud_cover: cloudCover,
    weather: weather ? {
      temperature: weather.temperature,
      humidity: weather.humidity,
      precipitation: weather.precipitation,
    } : undefined,
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

export async function downloadBatch(taskIds: string[]) {
  const API_URL = import.meta.env.VITE_API_URL || '/api';
  const resp = await fetch(`${API_URL}/download/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(taskIds),
  });
  if (resp.ok) {
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'spaceeye-batch.zip';
    a.click();
    URL.revokeObjectURL(url);
  }
}
