import L from 'leaflet';
import { toast } from 'svelte-sonner';
import { mapState } from '$lib/stores/map.svelte';
import { addRecord } from '$lib/stores/history.svelte';
import { API_URL } from '$lib/config';
import { downloadBlob, downloadBlobPost } from '$lib/utils/download';
import { pollTaskStatus } from '$lib/utils/pollTask';
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

export async function searchImages() {
  if (!mapState.polygonCoords) return;
  if (mapState.isLoading) return;
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
    toast.error('Falha ao buscar imagens', { description: (e as Error).message });
  } finally {
    mapState.isLoading = false;
  }
}

export async function processImage(imageId: string) {
  if (mapState.isLoading) return;

  mapState.isLoading = true;
  mapState.showImageGallery = false;
  mapState.showProcessingViewer = true;

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

    const result = await pollTaskStatus(data.task_id, {
      intervalMs: 1000,
      onProgress: (progress, phase) => {
        if (!mapState.showProcessingViewer) return;
        mapState.processingProgress = progress;
        mapState.processingPhase = phase;
      },
    });

    if (!mapState.showProcessingViewer) {
      mapState.isLoading = false;
      return;
    }

    if (result.status === 'done') {
      mapState.isLoading = false;
      mapState.showProcessingViewer = false;
      showOverlayResult(result.result as unknown as ProcessResult);
      addRecord({
        imageId: imageId,
        product: mapState.selectedProduct,
        collection: mapState.selectedCollection || 'unknown',
        cloudCover: null,
        polygonCoords: mapState.polygonCoords || [],
        centroid: mapState.polygonCentroid,
        stats: result.result?.statistics as Record<string, unknown> | undefined,
      });
      // Auto-save to backend for dashboard
      try {
        await fetch(`${API_URL}/analyses`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_id: imageId,
            collection: mapState.selectedCollection || 'unknown',
            product: mapState.selectedProduct,
            polygon: { type: 'Polygon', coordinates: mapState.polygonCoords },
            centroid: mapState.polygonCentroid,
            statistics: result.result?.statistics,
            overlay_path: result.result?.path,
          }),
        });
      } catch { /* non-critical, history store has backup */ }
    } else {
      mapState.isLoading = false;
      mapState.processingPhase = 'Erro: ' + (result.error || 'Falha no processamento');
    }
  } catch {
    mapState.isLoading = false;
    mapState.processingPhase = 'Erro ao iniciar processamento';
    toast.error('Falha ao iniciar processamento');
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
  try {
    await downloadBlobPost(`${API_URL}/export/pdf`, body, `spaceeye-${imageId.slice(0, 20)}.pdf`);
  } catch {
    toast.error('Falha ao exportar PDF');
  }
}

export async function downloadGeotiff(taskId: string) {
  try {
    await downloadBlob(`${API_URL}/download/${taskId}/geotiff`, `spaceeye-${taskId.slice(0, 8)}.tif`);
  } catch {
    toast.error('Falha ao baixar GeoTIFF');
  }
}

export async function downloadBatch(taskIds: string[]) {
  try {
    await downloadBlobPost(`${API_URL}/download/batch`, { task_ids: taskIds }, 'spaceeye-batch.zip');
  } catch {
    toast.error('Falha ao baixar lote');
  }
}

export async function exportEsgCsv(module: string, coordinates: number[][][]) {
  try {
    await downloadBlobPost(`${API_URL}/export/esg-csv`, { coordinates }, `spaceeye-${module}-export.csv`);
  } catch {
    toast.error('Failed to export CSV');
  }
}

export async function exportEsgJson(region: string, coordinates: number[][][]) {
  try {
    await downloadBlobPost(`${API_URL}/export/esg-json`, { coordinates }, `spaceeye-esg-export.json`);
  } catch {
    toast.error('Failed to export JSON');
  }
}
