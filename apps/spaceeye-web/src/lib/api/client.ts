import { createApiClient } from '$lib/ui/utils/createApiClient';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

export const api = createApiClient({ baseUrl: API_URL });

export interface ImageResult {
  id: string;
  collection: string;
  cloud_cover: number | null;
  acquired_at: string;
  thumbnail_url: string | null;
  footprint: any;
}

export interface SearchResponse {
  images: ImageResult[];
  total: number;
}

export interface TaskResult {
  task_id: string;
  status: string;
  progress: number;
  phase: string;
  result?: any;
  error?: string;
}

export async function searchImages(coordinates: number[][][], collections?: string[]): Promise<SearchResponse> {
  return api.post('/images/search', { coordinates, collections, limit: 50 });
}

export async function processImage(imageId: string, coordinates: number[][][], product: string): Promise<{ task_id: string }> {
  return api.post('/process', { image_id: imageId, coordinates, product });
}

export async function getTaskStatus(taskId: string): Promise<TaskResult> {
  return api.get(`/tasks/${taskId}`);
}

export async function getUfs(): Promise<string[]> {
  return api.get('/ibge/uf');
}

export async function getCities(uf: string): Promise<string[]> {
  return api.get(`/ibge/cidades/${uf}`);
}
