import { createApiClient } from '$lib/ui/utils/createApiClient';
import type { ImageResult, SavedAnalysis, RegionProfile, LandCoverStats, CarbonStock, FireRisk } from './types';
import { API_URL } from '$lib/config';
import { logger } from '$lib/utils/logger';

export const api = createApiClient({
  baseUrl: API_URL,
  getToken: () => {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem('spaceeye_api_key');
    }
    return null;
  },
  onError: (e: unknown, path?: string) => logger.warn('API error:', path, e),
});

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

export async function deleteProfile(id: string): Promise<{ deleted: boolean }> {
  return api.delete(`/profiles/${id}`);
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

export interface GeocodeResult {
  lat: string;
  lon: string;
  display_name: string;
}

export async function geocode(query: string): Promise<GeocodeResult[]> {
  return api.get('/geocode', { q: query });
}

export async function exportEsgCsv(data: { region: string; coordinates: number[][][]; module: string }): Promise<Blob> {
  return api.postBlob('/export/esg-csv', data);
}

export type { ImageResult, Bookmark, Monitor, AnalysisRecord, TaskStatus, SavedAnalysis, RegionProfile, LandCoverStats, CarbonStock, FireRisk, Alert, AlertThreshold } from './types';
