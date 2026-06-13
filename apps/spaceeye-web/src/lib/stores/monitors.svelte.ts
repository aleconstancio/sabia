import type { Bookmark, Monitor } from '$lib/api/types';
import { searchImages } from '$lib/api/client';

let _monitors = $state<Monitor[]>([]);

function load() {
  try {
    const raw = localStorage.getItem('spaceeye_monitors');
    _monitors = raw ? JSON.parse(raw) : [];
  } catch (e) { console.warn('Monitors load failed:', e); _monitors = []; }
}

function persist() {
  try {
    localStorage.setItem('spaceeye_monitors', JSON.stringify(_monitors));
  } catch (e) {
    if (e instanceof DOMException && e.name === 'QuotaExceededError') {
      console.warn('Monitors localStorage quota exceeded');
    } else {
      console.warn('Monitors persist failed:', e);
    }
  }
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
    const data = await searchImages(m.polygonCoords, undefined);
    const newImages = data.images || [];
    const result = newImages.length > 0 ? `Nova imagem: ${newImages[0].id.slice(0, 20)}... (${newImages[0].acquired_at})` : 'Sem novidades';
    _monitors = _monitors.map(monitor =>
      monitor.id === m.id
        ? { ...monitor, lastChecked: new Date().toISOString(), lastResult: result }
        : monitor
    );
    persist();
    return result;
  } catch (e) { console.warn('Monitor check failed:', e); }
  return 'Falha na verificação';
}

load();
