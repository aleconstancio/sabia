import { API_URL } from '$lib/config';

interface PollOptions {
  maxAttempts?: number;
  intervalMs?: number;
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
 */
export async function pollTaskStatus(
  taskId: string,
  options: PollOptions = {}
): Promise<PollResult> {
  const { maxAttempts = 120, intervalMs = 2000, onProgress, signal } = options;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    if (signal?.aborted) {
      return { status: 'error', error: 'Aborted' };
    }

    await new Promise(r => setTimeout(r, intervalMs));

    if (signal?.aborted) {
      return { status: 'error', error: 'Aborted' };
    }

    try {
      const resp = await fetch(`${API_URL}/tasks/${taskId}`, { signal });
      if (!resp.ok) continue;

      const status = await resp.json();
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
      console.debug('Poll network error:', e);
    }
  }

  return { status: 'error', error: 'Timeout: task did not complete in time' };
}
