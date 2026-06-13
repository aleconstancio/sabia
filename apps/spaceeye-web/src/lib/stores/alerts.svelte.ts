import type { Alert } from '$lib/api/types';

let _alerts = $state<Alert[]>([]);

function load() {
  try {
    const raw = localStorage.getItem('spaceeye_alerts');
    const parsed = raw ? JSON.parse(raw) : [];
    _alerts = Array.isArray(parsed) ? parsed : [];
  } catch (e) { console.warn('Alerts load failed:', e); _alerts = []; }
}

function persist() {
  try {
    localStorage.setItem('spaceeye_alerts', JSON.stringify(_alerts));
  } catch (e) {
    if (e instanceof DOMException && e.name === 'QuotaExceededError') {
      console.warn('Alerts localStorage quota exceeded, trimming old entries');
      _alerts = _alerts.slice(0, 25);
      try { localStorage.setItem('spaceeye_alerts', JSON.stringify(_alerts)); } catch { /* give up */ }
    } else {
      console.warn('Alerts persist failed:', e);
    }
  }
}

export const alertStore = {
  get alerts() { return _alerts; },
  get unreadCount() { return _alerts.filter(a => !a.read).length; },
  add(alert: Omit<Alert, 'id' | 'timestamp' | 'read'>) {
    const newAlert: Alert = {
      ...alert,
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      read: false,
    };
    _alerts = [newAlert, ..._alerts].slice(0, 50);
    persist();
  },
  markRead(id: string) {
    _alerts = _alerts.map(a => a.id === id ? { ...a, read: true } : a);
    persist();
  },
  markAllRead() {
    _alerts = _alerts.map(a => ({ ...a, read: true }));
    persist();
  },
  clear() {
    _alerts = [];
    persist();
  },
};

load();
