import type { AnalysisRecord } from '$lib/api/types';
import { saveAnalysis } from '$lib/api/client';
import { createLocalStorageStore } from '$lib/helpers/localStorage.svelte';
import { logger } from '$lib/utils/logger';

const store = createLocalStorageStore<AnalysisRecord>('horus_history', []);

async function persistToBackend(rec: AnalysisRecord) {
  try {
    await saveAnalysis({
      image_id: rec.imageId,
      collection: rec.collection,
      product: rec.product,
      polygon: { type: 'Polygon', coordinates: rec.polygonCoords },
      centroid: rec.centroid ?? undefined,
      statistics: rec.stats as Record<string, unknown>,
    });
  } catch (e) { logger.warn('History persist failed:', e); }
}

export const historyStore = {
  get all() { return store.data; },
  add(rec: Omit<AnalysisRecord, 'id' | 'timestamp'>) {
    const r: AnalysisRecord = { id: crypto.randomUUID(), timestamp: new Date().toISOString(), ...rec };
    store.data = [r, ...store.data].slice(0, 50);
    persistToBackend(r).catch(e => logger.warn('Background backend persistence failed:', e));
    return r;
  },
  clear() {
    store.data = [];
    localStorage.removeItem('horus_history');
  },
  refresh() {
    store.load();
    return store.data;
  },
};