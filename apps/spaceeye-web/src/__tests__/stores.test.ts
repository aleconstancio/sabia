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
