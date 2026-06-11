export interface Bookmark {
  id: string;
  name: string;
  coords: number[][][];
  created_at: string;
}

let _bookmarks = $state<Bookmark[]>([]);

function load() {
  try {
    const raw = localStorage.getItem('spaceeye_bookmarks');
    _bookmarks = raw ? JSON.parse(raw) : [];
  } catch (e) { console.warn('Bookmarks load failed:', e); _bookmarks = []; }
}

function persist() {
  localStorage.setItem('spaceeye_bookmarks', JSON.stringify(_bookmarks));
}

export function addBookmark(name: string, coords: number[][][]) {
  const b: Bookmark = { id: crypto.randomUUID(), name, coords, created_at: new Date().toISOString() };
  _bookmarks = [..._bookmarks, b];
  persist();
  return b;
}

export function removeBookmark(id: string) {
  _bookmarks = _bookmarks.filter(b => b.id !== id);
  persist();
}

export function getBookmarks() {
  load();
  return _bookmarks;
}

load();
