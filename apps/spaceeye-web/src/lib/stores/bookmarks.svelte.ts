import type { Bookmark } from '$lib/api/types';

let _bookmarks = $state<Bookmark[]>([]);

function load() {
  try {
    const raw = localStorage.getItem('spaceeye_bookmarks');
    _bookmarks = raw ? JSON.parse(raw) : [];
  } catch (e) { console.warn('Bookmarks load failed:', e); _bookmarks = []; }
}

function persist() {
  try {
    localStorage.setItem('spaceeye_bookmarks', JSON.stringify(_bookmarks));
  } catch (e) {
    if (e instanceof DOMException && e.name === 'QuotaExceededError') {
      console.warn('Bookmarks localStorage quota exceeded');
    } else {
      console.warn('Bookmarks persist failed:', e);
    }
  }
}

export const bookmarksStore = {
  get all() { return _bookmarks; },
  add(name: string, coords: number[][][]) {
    const b: Bookmark = { id: crypto.randomUUID(), name, coords, created_at: new Date().toISOString() };
    _bookmarks = [..._bookmarks, b];
    persist();
    return b;
  },
  remove(id: string) {
    _bookmarks = _bookmarks.filter(b => b.id !== id);
    persist();
  },
  refresh() {
    load();
    return _bookmarks;
  },
};

load();
