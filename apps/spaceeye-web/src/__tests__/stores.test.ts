import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('mapState store', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('provides default values', async () => {
    const { mapState } = await import('$lib/stores/map.svelte');
    expect(mapState.selectedProduct).toBe('NDVI');
    expect(mapState.selectedCollection).toBe('cbers4a');
    expect(mapState.isLoading).toBe(false);
    expect(mapState.hasOverlay).toBe(false);
    expect(mapState.results).toEqual([]);
  });

  it('updates reactive state', async () => {
    const { mapState } = await import('$lib/stores/map.svelte');
    mapState.selectedProduct = 'SAVI';
    expect(mapState.selectedProduct).toBe('SAVI');
    mapState.isLoading = true;
    expect(mapState.isLoading).toBe(true);
  });
});

describe('bookmarks store', () => {
  beforeEach(() => {
    vi.resetModules();
    localStorage.clear();
  });

  it('adds and retrieves bookmarks', async () => {
    const { bookmarksStore } = await import('$lib/stores/bookmarks.svelte');
    bookmarksStore.add('Test Farm', [[[-35, -6], [-34, -6], [-34, -5], [-35, -5], [-35, -6]]]);
    const bookmarks = bookmarksStore.all;
    expect(bookmarks).toHaveLength(1);
    expect(bookmarks[0].name).toBe('Test Farm');
  });

  it('removes bookmarks', async () => {
    const { bookmarksStore } = await import('$lib/stores/bookmarks.svelte');
    bookmarksStore.add('Farm A', [[[0, 0]]]);
    const bm = bookmarksStore.all;
    bookmarksStore.remove(bm[0].id);
    expect(bookmarksStore.all).toHaveLength(0);
  });
});

describe('alertStore', () => {
  beforeEach(async () => {
    vi.resetModules();
    localStorage.clear();
    const { alertStore } = await import('$lib/stores/alerts.svelte');
    alertStore.clear();
  });

  it('starts with empty alerts', async () => {
    const { alertStore } = await import('$lib/stores/alerts.svelte');
    expect(alertStore.alerts).toEqual([]);
    expect(alertStore.unreadCount).toBe(0);
  });

  it('adds alerts with auto-generated id and timestamp', async () => {
    const { alertStore } = await import('$lib/stores/alerts.svelte');
    alertStore.add({ type: 'info', message: 'Test alert', region: 'Test Region' });
    expect(alertStore.alerts).toHaveLength(1);
    expect(alertStore.alerts[0].message).toBe('Test alert');
    expect(alertStore.alerts[0].id).toBeDefined();
    expect(alertStore.alerts[0].timestamp).toBeDefined();
    expect(alertStore.alerts[0].read).toBe(false);
  });

  it('tracks unread count', async () => {
    const { alertStore } = await import('$lib/stores/alerts.svelte');
    alertStore.add({ type: 'info', message: 'Alert 1', region: 'R1' });
    alertStore.add({ type: 'info', message: 'Alert 2', region: 'R2' });
    expect(alertStore.unreadCount).toBe(2);

    alertStore.markRead(alertStore.alerts[0].id);
    expect(alertStore.unreadCount).toBe(1);
  });

  it('marks all as read', async () => {
    const { alertStore } = await import('$lib/stores/alerts.svelte');
    alertStore.add({ type: 'info', message: 'Alert 1', region: 'R1' });
    alertStore.add({ type: 'info', message: 'Alert 2', region: 'R2' });
    alertStore.markAllRead();
    expect(alertStore.unreadCount).toBe(0);
  });

  it('clears all alerts', async () => {
    const { alertStore } = await import('$lib/stores/alerts.svelte');
    alertStore.add({ type: 'info', message: 'Alert 1', region: 'R1' });
    alertStore.clear();
    expect(alertStore.alerts).toEqual([]);
  });

  it('caps at 50 alerts', async () => {
    const { alertStore } = await import('$lib/stores/alerts.svelte');
    for (let i = 0; i < 60; i++) {
      alertStore.add({ type: 'info', message: `Alert ${i}`, region: 'R' });
    }
    expect(alertStore.alerts.length).toBeLessThanOrEqual(50);
  });
});

describe('historyStore', () => {
  beforeEach(async () => {
    vi.resetModules();
    localStorage.clear();
    const { historyStore } = await import('$lib/stores/history.svelte');
    historyStore.clear();
  });

  it('starts with empty history', async () => {
    const { historyStore } = await import('$lib/stores/history.svelte');
    expect(historyStore.all).toEqual([]);
  });

  it('adds analysis records with auto-generated id and timestamp', async () => {
    const { historyStore } = await import('$lib/stores/history.svelte');
    historyStore.add({
      imageId: 'img-123',
      collection: 'cbers4a',
      product: 'NDVI',
      polygonCoords: [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
      cloudCover: 10,
      centroid: null,
      stats: { mean: 0.5 },
    });
    expect(historyStore.all).toHaveLength(1);
    expect(historyStore.all[0].imageId).toBe('img-123');
    expect(historyStore.all[0].id).toBeDefined();
    expect(historyStore.all[0].timestamp).toBeDefined();
  });

  it('clears history', async () => {
    const { historyStore } = await import('$lib/stores/history.svelte');
    historyStore.add({
      imageId: 'img-1',
      collection: 'cbers4a',
      product: 'NDVI',
      polygonCoords: [],
      cloudCover: null,
      centroid: null,
    });
    historyStore.clear();
    expect(historyStore.all).toEqual([]);
  });
});

describe('dashboardState', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('has correct initial state', async () => {
    const { dashboardState } = await import('$lib/stores/dashboard.svelte');
    expect(dashboardState.isLoading).toBe(false);
    expect(dashboardState.error).toBe('');
  });
});
