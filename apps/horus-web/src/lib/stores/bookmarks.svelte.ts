import type { Bookmark } from '$lib/api/types';
import { createLocalStorageStore } from '$lib/helpers/localStorage.svelte';

const store = createLocalStorageStore<Bookmark>('horus_bookmarks', []);

export const bookmarksStore = {
  get all() { return store.data; },
  add(name: string, coords: number[][][]) {
    const b: Bookmark = { id: crypto.randomUUID(), name, coords, created_at: new Date().toISOString() };
    store.data = [...store.data, b];
    return b;
  },
  remove(id: string) {
    store.data = store.data.filter(b => b.id !== id);
  },
  refresh() {
    store.load();
    return store.data;
  },
};