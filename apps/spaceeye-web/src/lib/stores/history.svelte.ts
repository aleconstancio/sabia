import type { AnalysisRecord } from '$lib/api/types';
import { saveAnalysis } from '$lib/api/client';

let _history = $state<AnalysisRecord[]>([]);

function load() {
  try {
    const raw = localStorage.getItem('spaceeye_history');
    const parsed = raw ? JSON.parse(raw) : [];
    _history = Array.isArray(parsed) ? parsed : [];
  } catch (e) { console.warn('History load failed:', e); _history = []; }
}

function persist() {
  try {
    localStorage.setItem('spaceeye_history', JSON.stringify(_history));
  } catch (e) {
    if (e instanceof DOMException && e.name === 'QuotaExceededError') {
      console.warn('History localStorage quota exceeded, trimming old entries');
      _history = _history.slice(0, 25);
      try { localStorage.setItem('spaceeye_history', JSON.stringify(_history)); } catch (e: unknown) { console.warn('History give-up persist:', e); }
    } else {
      console.warn('History persist failed:', e);
    }
  }
}

async function persistToBackend(rec: AnalysisRecord) {
  try {
    await saveAnalysis({
      image_id: rec.imageId,
      collection: rec.collection,
      product: rec.product,
      polygon: { type: 'Polygon', coordinates: rec.polygonCoords },
      centroid: rec.centroid ?? undefined,
      statistics: rec.stats,
    });
  } catch (e) { console.warn('History persist failed:', e); }
}

export const historyStore = {
  get all() { return _history; },
  add(rec: Omit<AnalysisRecord, 'id' | 'timestamp'>) {
    const r: AnalysisRecord = { id: crypto.randomUUID(), timestamp: new Date().toISOString(), ...rec };
    _history = [r, ..._history].slice(0, 50);
    persist();
    persistToBackend(r).catch(e => console.warn('Background backend persistence failed:', e));
    return r;
  },
  clear() {
    _history = [];
    localStorage.removeItem('spaceeye_history');
  },
  refresh() {
    load();
    return _history;
  },
};

load();
