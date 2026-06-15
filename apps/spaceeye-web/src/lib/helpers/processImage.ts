/**
 * Shared helper for processing images and creating overlays.
 * Used by SwipeComparison, RegionComparison, and other components.
 */
import { API_URL } from '$lib/config';
import { api } from '$lib/api/client';
import { pollTaskStatus } from '$lib/helpers/pollTask';
import { logger } from '$lib/utils/logger';

export interface ProcessImageOptions {
  imageId: string;
  coordinates: number[][][];
  product: string;
}

export interface ProcessImageResult {
  status: 'done' | 'error';
  overlayUrl?: string;
  bounds?: [[number, number], [number, number]];
  error?: string;
}

/**
 * Get the URL for an overlay image from a task result path.
 */
export function getOverlayUrl(taskPath: string): string {
  const filename = taskPath.split('/').pop();
  return `${API_URL}/overlay/${filename}`;
}

/**
 * Process an image and poll until completion.
 */
export async function processImageAndPoll(
  options: ProcessImageOptions
): Promise<ProcessImageResult> {
  try {
    const data = await api.post('/process', {
      image_id: options.imageId,
      coordinates: options.coordinates,
      product: options.product,
    });

    const result = await pollTaskStatus(data.task_id, { intervalMs: 2000 });

    if (result.status === 'done') {
      const bounds = result.result?.bounds as [[number, number], [number, number]];
      const overlayUrl = getOverlayUrl(result.result?.path as string);
      return { status: 'done', overlayUrl, bounds };
    }

    return { status: 'error', error: result.error || 'Processing failed' };
  } catch (e: unknown) {
    logger.warn('processImageAndPoll error:', e);
    return { status: 'error', error: e instanceof Error ? e.message : String(e) };
  }
}