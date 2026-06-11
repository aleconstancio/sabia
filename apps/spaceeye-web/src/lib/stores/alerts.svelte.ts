export interface Alert {
  id: string;
  type: string;
  message: string;
  region: string;
  timestamp: string;
  read: boolean;
}

let _alerts = $state<Alert[]>([]);

function load() {
  try {
    const raw = localStorage.getItem('spaceeye_alerts');
    _alerts = raw ? JSON.parse(raw) : [];
  } catch { _alerts = []; }
}

function persist() {
  localStorage.setItem('spaceeye_alerts', JSON.stringify(_alerts));
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
