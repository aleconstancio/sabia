import { api } from '$lib/api/client';
import { logger } from '$lib/utils/logger';

interface PollOptions {
  maxAttempts?: number;
  initialIntervalMs?: number;
  maxIntervalMs?: number;
  onProgress?: (progress: number, phase: string) => void;
  signal?: AbortSignal;
}

interface PollResult {
  status: 'done' | 'error';
  result?: Record<string, unknown>;
  error?: string;
}

/**
 * Poll a Celery task until completion or timeout.
 * Uses exponential backoff starting at initialIntervalMs, increasing to maxIntervalMs.
 */
export async function pollTaskStatus(
  taskId: string,
  options: PollOptions = {}
): Promise<PollResult> {
  const {
    maxAttempts = 120,
    initialIntervalMs = 500,
    maxIntervalMs = 3000,
    onProgress,
    signal,
  } = options;

  let currentInterval = initialIntervalMs;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    if (signal?.aborted) {
      return { status: 'error', error: 'Aborted' };
    }

    await new Promise(r => setTimeout(r, currentInterval));

    if (signal?.aborted) {
      return { status: 'error', error: 'Aborted' };
    }

    try {
      const status = await api.get(`/tasks/${taskId}`);
      onProgress?.(status.progress || 0, status.phase || '');

      if (status.status === 'done') {
        return { status: 'done', result: status.result };
      }
      if (status.status === 'error') {
        return { status: 'error', error: status.error };
      }
    } catch (e) {
      if (signal?.aborted) {
        return { status: 'error', error: 'Aborted' };
      }
      logger.debug('Poll network error:', e);
    }

    // Exponential backoff with cap
    currentInterval = Math.min(currentInterval * 1.5, maxIntervalMs);
  }

  return { status: 'error', error: 'Timeout: task did not complete in time' };
}