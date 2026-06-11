import type { AnalysisRecord } from '$lib/api/types';
import { API_URL } from '$lib/config';

let _history = $state<AnalysisRecord[]>([]);

function load() {
  try {
    const raw = localStorage.getItem('spaceeye_history');
    _history = raw ? JSON.parse(raw) : [];
  } catch { _history = []; }
}

function persist() {
  localStorage.setItem('spaceeye_history', JSON.stringify(_history));
}

async function persistToBackend(rec: AnalysisRecord) {
  try {
    await fetch(`${API_URL}/analyses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_id: rec.imageId,
        collection: rec.collection,
        product: rec.product,
        polygon: { type: 'Polygon', coordinates: rec.polygonCoords },
        centroid: rec.centroid,
        statistics: rec.stats,
        cloud_cover: rec.cloudCover,
      }),
    });
  } catch { /* offline — localStorage backup is fine */ }
}

export function addRecord(rec: Omit<AnalysisRecord, 'id' | 'timestamp'>) {
  const r: AnalysisRecord = { id: crypto.randomUUID(), timestamp: new Date().toISOString(), ...rec };
  _history = [r, ..._history].slice(0, 50);
  persist();
  persistToBackend(r);
  return r;
}

export function clearHistory() {
  _history = [];
  localStorage.removeItem('spaceeye_history');
}

export function getHistory(): AnalysisRecord[] {
  load();
  return _history;
}

load();
