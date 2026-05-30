import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('mapState store', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('provides default values', async () => {
    const { mapState } = await import('$lib/stores/map.svelte.ts');
    expect(mapState.selectedProduct).toBe('NDVI');
    expect(mapState.selectedCollection).toBe('cbers4a');
    expect(mapState.isLoading).toBe(false);
    expect(mapState.hasOverlay).toBe(false);
    expect(mapState.results).toEqual([]);
  });

  it('updates reactive state', async () => {
    const { mapState } = await import('$lib/stores/map.svelte.ts');
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
    const { addBookmark, getBookmarks } = await import('$lib/stores/bookmarks.svelte.ts');
    addBookmark('Test Farm', [[[-35, -6], [-34, -6], [-34, -5], [-35, -5], [-35, -6]]]);
    const bookmarks = getBookmarks();
    expect(bookmarks).toHaveLength(1);
    expect(bookmarks[0].name).toBe('Test Farm');
  });

  it('removes bookmarks', async () => {
    const { addBookmark, removeBookmark, getBookmarks } = await import('$lib/stores/bookmarks.svelte.ts');
    addBookmark('Farm A', [[[0, 0]]]);
    const bm = getBookmarks();
    removeBookmark(bm[0].id);
    expect(getBookmarks()).toHaveLength(0);
  });
});
