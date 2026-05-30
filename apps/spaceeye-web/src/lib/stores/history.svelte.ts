export interface AnalysisRecord {
  id: string;
  timestamp: string;
  imageId: string;
  product: string;
  collection: string;
  cloudCover: number | null;
  polygonCoords: number[][][];
  centroid: { lat: number; lon: number } | null;
  stats?: any;
}

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

export function addRecord(rec: Omit<AnalysisRecord, 'id' | 'timestamp'>) {
  const r: AnalysisRecord = { id: crypto.randomUUID(), timestamp: new Date().toISOString(), ...rec };
  _history = [r, ..._history].slice(0, 50);
  persist();
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
