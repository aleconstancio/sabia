import L from 'leaflet';
import { toast } from 'svelte-sonner';
import { mapState } from '$lib/stores/map.svelte';
import { historyStore } from '$lib/stores/history.svelte';
import { searchImages as apiSearchImages, processImage as apiProcessImage } from '$lib/api/client';
import { API_URL } from '$lib/config';
import { downloadBlob, downloadBlobPost } from '$lib/helpers/download';
import { pollTaskStatus } from '$lib/helpers/pollTask';
import type { Map as LeafletMap } from 'leaflet';

interface ProcessResult {
  bounds: [[number, number], [number, number]];
  path: string;
  statistics?: Record<string, unknown>;
}

function isProcessResult(val: unknown): val is ProcessResult {
  return (
    typeof val === 'object' &&
    val !== null &&
    'bounds' in val &&
    'path' in val
  );
}

export async function searchImages() {
  if (!mapState.polygonCoords) return;
  if (mapState.isLoading) return;
  mapState.isLoading = true;
  mapState.searchError = '';
  try {
    const collections = mapState.selectedCollection ? [mapState.selectedCollection] : undefined;
    const data = await apiSearchImages(mapState.polygonCoords, collections);
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
    const data = await apiProcessImage(imageId, mapState.polygonCoords || [], mapState.selectedProduct);
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
      if (isProcessResult(result.result)) {
        showOverlayResult(result.result);
      }
      historyStore.add({
        imageId: imageId,
        product: mapState.selectedProduct,
        collection: mapState.selectedCollection || 'unknown',
        cloudCover: null,
        polygonCoords: mapState.polygonCoords || [],
        centroid: mapState.polygonCentroid,
        stats: result.result?.statistics as Record<string, unknown> | undefined,
      });
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
  const body = {
    image_id: imageId,
    product: mapState.selectedProduct,
    date: new Date().toISOString(),
    cloud_cover: cloudCover,
    weather: weather ? {
      temperature: weather.temperature,
      humidity: weather.humidity,
      precipitation: weather.precipitation,
    } : undefined,
    overlay_path: mapState.lastOverlayPath || undefined,
  };
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
