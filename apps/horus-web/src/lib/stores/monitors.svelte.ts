import type { Bookmark, Monitor } from '$lib/api/types';
import { searchImages } from '$lib/api/client';
import { createLocalStorageStore } from '$lib/helpers/localStorage.svelte';
import { logger } from '$lib/utils/logger';

const store = createLocalStorageStore<Monitor>('horus_monitors', []);

function addMonitor(bookmark: Bookmark, product: string = 'NDVI', minCloudCover: number = 30): Monitor {
  const m: Monitor = {
    id: crypto.randomUUID(),
    bookmarkId: bookmark.id,
    bookmarkName: bookmark.name,
    polygonCoords: bookmark.coords,
    product,
    minCloudCover,
    active: true,
    lastChecked: null,
    lastResult: null,
  };
  store.data = [...store.data, m];
  return m;
}

function removeMonitor(id: string) {
  store.data = store.data.filter(m => m.id !== id);
}

function getMonitors(): Monitor[] {
  return store.data;
}

async function checkMonitor(m: Monitor): Promise<string> {
  try {
    const data = await searchImages(m.polygonCoords, undefined);
    const newImages = data.images || [];
    const result = newImages.length > 0 ? `New image: ${newImages[0].id.slice(0, 20)}... (${newImages[0].acquired_at})` : 'No updates';
    store.data = store.data.map(monitor =>
      monitor.id === m.id
        ? { ...monitor, lastChecked: new Date().toISOString(), lastResult: result }
        : monitor
    );
    return result;
  } catch (e) { logger.warn('Monitor check failed:', e); }
  return 'Check failed';
}

export const monitorsStore = {
  get all() { return store.data; },
  add: addMonitor,
  remove: removeMonitor,
  getAll: getMonitors,
  check: checkMonitor,
};