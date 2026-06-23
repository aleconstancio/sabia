import L from 'leaflet';
import { toast } from 'svelte-sonner';
import { mapState } from '$lib/stores/map.svelte';
import { historyStore } from '$lib/stores/history.svelte';
import { searchImages as apiSearchImages, processImage as apiProcessImage, exportEsgCsv as apiExportEsgCsv } from '$lib/api/client';
import { API_URL } from '$lib/config';
import { downloadBlob, downloadBlobPost, triggerDownload } from '$lib/helpers/download';
import { pollTaskStatus } from '$lib/helpers/pollTask';
import { logger } from '$lib/utils/logger';
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

let _processAbort: AbortController | null = null;

export async function searchImages() {
  mapState.isLoading = true;
  if (!mapState.polygonCoords) return;
  mapState.searchError = '';
  try {
    const collections = mapState.selectedCollection ? [mapState.selectedCollection] : undefined;
    const data = await apiSearchImages(mapState.polygonCoords, collections);
    mapState.results = data.images || [];
    mapState.showPolygonModal = false;
    mapState.showImageGallery = true;
  } catch (e: unknown) {
    mapState.searchError = e instanceof Error ? e.message : String(e) || 'Error searching images';
    toast.error('Failed to search images', { description: e instanceof Error ? e.message : String(e) });
  } finally {
    mapState.isLoading = false;
  }
}

export async function processImage(imageId: string) {
  if (mapState.isLoading) return;
  if (!mapState.polygonCoords) return;

  if (_processAbort) _processAbort.abort();
  _processAbort = new AbortController();
  const signal = _processAbort.signal;

  mapState.isLoading = true;
  mapState.showImageGallery = false;
  mapState.showProcessingViewer = true;

  try {
    const data = await apiProcessImage(imageId, mapState.polygonCoords || [], mapState.selectedProduct);
    mapState.taskId = data.task_id;

    const result = await pollTaskStatus(data.task_id, {
      initialIntervalMs: 1000,
      signal,
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
      mapState.processingPhase = 'Error: ' + (result.error || 'Processing failed');
    }
  } catch (e: unknown) {
    logger.error('processImage error:', e);
    mapState.isLoading = false;
    mapState.processingPhase = 'Error starting processing';
    toast.error('Failed to start processing');
  }
}

function showOverlayResult(result: ProcessResult) {
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
    await downloadBlobPost(`${API_URL}/export/pdf`, body, `horus-${imageId.slice(0, 20)}.pdf`);
    toast.success('PDF exported');
  } catch (e: unknown) {
    logger.error('exportPdf error:', e);
    toast.error('Failed to export PDF');
  }
}

export async function downloadGeotiff(taskId: string) {
  try {
    await downloadBlob(`${API_URL}/download/${taskId}/geotiff`, `horus-${taskId.slice(0, 8)}.tif`);
    toast.success('GeoTIFF downloaded');
  } catch (e: unknown) {
    logger.error('downloadGeotiff error:', e);
    toast.error('Failed to download GeoTIFF');
  }
}

export async function exportEsgCsv(module: string, coordinates: number[][][]) {
  try {
    const blob = await apiExportEsgCsv({ region: module, coordinates, module });
    triggerDownload(blob, `horus-${module}-export.csv`);
  } catch (e: unknown) {
    logger.error('exportEsgCsv error:', e);
    toast.error('Failed to export CSV');
  }
}
