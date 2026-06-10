import { createApiClient } from '$lib/ui/utils/createApiClient';
import type { ImageResult, SavedAnalysis, RegionProfile } from './types';

const API_URL = import.meta.env.VITE_API_URL || '/api';

export const api = createApiClient({ baseUrl: API_URL });

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

export async function getTaskStatus(taskId: string): Promise<{ task_id: string; status: string; progress: number; phase: string; result?: any; error?: string }> {
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

export type { ImageResult, SoilData, WeatherData, LandCoverData, Bookmark, Monitor, AnalysisRecord, TaskStatus, SavedAnalysis, RegionProfile } from './types';
