import { createApiClient } from '$lib/ui/utils/createApiClient';
import type { ImageResult } from './types';

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

export type { ImageResult, SoilData, WeatherData, LandCoverData, Bookmark, Monitor, AnalysisRecord, TaskStatus } from './types';
