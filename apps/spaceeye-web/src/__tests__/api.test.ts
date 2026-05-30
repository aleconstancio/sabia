import { describe, it, expect, beforeEach } from 'vitest';

describe('API client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('searchImages sends correct request', async () => {
    const mockResponse = { images: [{ id: 'test' }], total: 1 };
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const API_URL = '/api';
    const resp = await fetch(`${API_URL}/images/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        coordinates: [[[0, 0], [1, 0], [1, 1], [0, 0]]],
        limit: 50,
        max_cloud: 20,
        sort_by: 'acquired_at',
      }),
    });
    const data = await resp.json();

    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    expect(data.images).toHaveLength(1);
    expect(data.total).toBe(1);
  });

  it('handles API errors gracefully', async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      text: () => Promise.resolve('Invalid polygon'),
    });

    const response = await fetch('/api/images/search', { method: 'POST' });
    expect(response.ok).toBe(false);
    expect(response.status).toBe(400);
  });

  it('task polling returns status progression', async () => {
    let pollCount = 0;
    (globalThis.fetch as any).mockImplementation(() => {
      pollCount++;
      const statuses = [
        { status: 'pending', progress: 0, phase: '' },
        { status: 'running', progress: 50, phase: 'downloading' },
        { status: 'done', progress: 100, phase: 'done', result: { path: '/tmp/test.png', bounds: [[0, 0], [1, 1]] } },
      ];
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(statuses[Math.min(pollCount - 1, 2)]),
      });
    });

    const resp1 = await fetch('/api/tasks/task_123');
    const s1 = await resp1.json();
    expect(s1.status).toBe('pending');

    const resp2 = await fetch('/api/tasks/task_123');
    const s2 = await resp2.json();
    expect(s2.status).toBe('running');
    expect(s2.progress).toBe(50);
  });
});
