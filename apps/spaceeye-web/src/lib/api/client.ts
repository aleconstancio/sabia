import { createApiClient } from '$lib/ui/utils/createApiClient';
import type { ImageResult, SavedAnalysis, RegionProfile, LandCoverStats, CarbonStock, FireRisk, ESGExportData } from './types';
import { API_URL } from '$lib/config';

export const api = createApiClient({ baseUrl: API_URL, onError: (e: unknown, path?: string) => console.warn('API error:', path, e) });

export interface SearchResponse {
  images: ImageResult[];
  total: number;
}

export async function searchImages(coordinates: number[][][], collections?: string[]): Promise<SearchResponse> {
  return api.post('/images/search', { coordinates, collections, limit: 50 });
}

export async function processImage(imageId: string, coordinates: number[][][], product: string): Promise<{ task_id: string }> {
  return api.post('/process', { image_id: imageId, coordinates, product });
}

export async function processBatch(imageIds: string[], coordinates: number[][][], product: string): Promise<{ tasks: { image_id: string; task_id: string }[] }> {
  return api.post('/process/batch', { image_ids: imageIds, coordinates, product });
}

export async function getTaskStatus(taskId: string): Promise<{ task_id: string; status: string; progress: number; phase: string; result?: Record<string, unknown>; error?: string }> {
  return api.get(`/tasks/${taskId}`);
}

export async function getUfs(): Promise<string[]> {
  return api.get('/ibge/uf');
}

export async function getCities(uf: string): Promise<string[]> {
  return api.get(`/ibge/cidades/${uf}`);
}

export async function saveAnalysis(data: {
  image_id: string;
  collection: string;
  product: string;
  polygon: { type: string; coordinates: number[][][] };
  centroid?: { lat: number; lon: number };
  statistics?: Record<string, unknown>;
  overlay_path?: string;
}): Promise<{ id: string }> {
  return api.post('/analyses', data);
}

export async function listAnalyses(params?: {
  product?: string;
  collection?: string;
  limit?: number;
  offset?: number;
}): Promise<{ analyses: SavedAnalysis[]; total: number }> {
  const query: Record<string, string> = {};
  if (params?.product) query.product = params.product;
  if (params?.collection) query.collection = params.collection;
  if (params?.limit) query.limit = String(params.limit);
  if (params?.offset) query.offset = String(params.offset);
  return api.get('/analyses', query);
}

export async function deleteAnalysis(id: string): Promise<{ deleted: boolean }> {
  return api.delete(`/analyses/${id}`);
}

export async function createProfile(data: {
  name?: string;
  polygon: { type: string; coordinates: number[][][] };
  satellite_data?: { product: string; stats: Record<string, unknown> };
  notes?: string;
}): Promise<{ id: string }> {
  return api.post('/profiles', data);
}

export async function listProfiles(params?: {
  limit?: number;
  offset?: number;
}): Promise<{ profiles: RegionProfile[]; total: number }> {
  const query: Record<string, string> = {};
  if (params?.limit) query.limit = String(params.limit);
  if (params?.offset) query.offset = String(params.offset);
  return api.get('/profiles', query);
}

export async function getProfile(id: string): Promise<RegionProfile> {
  return api.get(`/profiles/${id}`);
}

export async function refreshProfile(id: string): Promise<{ updated: boolean }> {
  return api.put(`/profiles/${id}/refresh`);
}

export async function deleteProfile(id: string): Promise<{ deleted: boolean }> {
  return api.delete(`/profiles/${id}`);
}

export async function getLandCoverStats(coordinates: number[][][]): Promise<LandCoverStats> {
  return api.post('/landcover/zonal-stats', { coordinates });
}

export async function getCarbonStock(coordinates: number[][][]): Promise<CarbonStock> {
  return api.post('/carbon-stock', { coordinates });
}

export async function getFireRisk(coordinates: number[][][]): Promise<FireRisk> {
  return api.post('/fire-risk', { coordinates });
}

export async function getWeather(lat: number, lon: number): Promise<Record<string, unknown>> {
  return api.get(`/weather/${lat}/${lon}`);
}

export async function getSoil(lat: number, lon: number): Promise<Record<string, unknown>> {
  return api.get(`/soil/${lat}/${lon}`);
}

export async function exportEsgJson(data: { region: string; coordinates: number[][][] }): Promise<ESGExportData> {
  return api.post('/export/esg-json', data);
}

export async function exportEsgCsv(data: { region: string; coordinates: number[][][]; module: string }): Promise<Blob> {
  const resp = await fetch(`${API_URL}/export/esg-csv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!resp.ok) {
    const text = await resp.text().catch(() => 'Unknown error');
    throw new Error(`ESG CSV export failed (${resp.status}): ${text}`);
  }
  return resp.blob();
}

export type { ImageResult, SoilData, WeatherData, LandCoverData, Bookmark, Monitor, AnalysisRecord, TaskStatus, SavedAnalysis, RegionProfile, LandCoverStats, CarbonStock, FireRisk, Alert, AlertThreshold, ESGExportData } from './types';
