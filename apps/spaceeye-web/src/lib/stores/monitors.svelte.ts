import type { Bookmark } from '$lib/api/types';
import { API_URL } from '$lib/config';

export interface Monitor {
  id: string;
  bookmarkId: string;
  bookmarkName: string;
  polygonCoords: number[][][];
  product: string;
  minCloudCover: number;
  active: boolean;
  lastChecked: string | null;
  lastResult: string | null;
}

let _monitors = $state<Monitor[]>([]);

function load() {
  try {
    const raw = localStorage.getItem('spaceeye_monitors');
    _monitors = raw ? JSON.parse(raw) : [];
  } catch { _monitors = []; }
}

function persist() {
  localStorage.setItem('spaceeye_monitors', JSON.stringify(_monitors));
}

export function addMonitor(bookmark: Bookmark, product: string = 'NDVI', minCloudCover: number = 30): Monitor {
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
  _monitors = [..._monitors, m];
  persist();
  return m;
}

export function removeMonitor(id: string) {
  _monitors = _monitors.filter(m => m.id !== id);
  persist();
}

export function getMonitors(): Monitor[] {
  load();
  return _monitors;
}

export async function checkMonitor(m: Monitor): Promise<string> {
  try {
    const resp = await fetch(`${API_URL}/images/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ coordinates: m.polygonCoords, max_cloud: m.minCloudCover, sort_by: 'acquired_at', sort_order: 'desc', limit: 1 }),
    });
    if (resp.ok) {
      const data = await resp.json();
      const newImages = data.images || [];
      const result = newImages.length > 0 ? `Nova imagem: ${newImages[0].id.slice(0, 20)}... (${newImages[0].acquired_at})` : 'Sem novidades';
      _monitors = _monitors.map(monitor =>
        monitor.id === m.id
          ? { ...monitor, lastChecked: new Date().toISOString(), lastResult: result }
          : monitor
      );
      persist();
      return result;
    }
  } catch { /* network error */ }
  return 'Falha na verificação';
}

load();
