import type { Alert } from '$lib/api/types';
import { createLocalStorageStore } from '$lib/helpers/localStorage.svelte';

const store = createLocalStorageStore<Alert>('horus_alerts', []);

let _unreadCache = 0;
let _lastSeenLength = -1;
let _lastSeenReadVersion = '';

export const alertStore = {
  get alerts() { return store.data; },
  get unreadCount() {
    const data = store.data;
    const readVersion = data.length + ':' + data.filter(a => a.read).length;
    if (readVersion !== _lastSeenReadVersion) {
      _unreadCache = data.filter(a => !a.read).length;
      _lastSeenReadVersion = readVersion;
    }
    return _unreadCache;
  },
  add(alert: Omit<Alert, 'id' | 'timestamp' | 'read'>) {
    const newAlert: Alert = {
      ...alert,
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      read: false,
    };
    store.data = [newAlert, ...store.data].slice(0, 50);
  },
  markRead(id: string) {
    store.data = store.data.map(a => a.id === id ? { ...a, read: true } : a);
  },
  markAllRead() {
    store.data = store.data.map(a => ({ ...a, read: true }));
  },
  clear() {
    store.data = [];
  },
};