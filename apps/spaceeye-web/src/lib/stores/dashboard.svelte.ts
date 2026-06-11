import type { RegionProfile } from '$lib/api/types';
import { API_URL } from '$lib/config';

let _profiles = $state<RegionProfile[]>([]);
let _total = $state(0);
let _isLoading = $state(false);

export const dashboardState = {
  get profiles() { return _profiles; },
  get total() { return _total; },
  get isLoading() { return _isLoading; },
};

export async function loadProfiles() {
  _isLoading = true;
  try {
    const resp = await fetch(`${API_URL}/profiles?limit=100`);
    if (resp.ok) {
      const data = await resp.json();
      _profiles = data.profiles || [];
      _total = data.total || 0;
    }
  } catch (e) { console.warn('Dashboard load failed:', e); }
  _isLoading = false;
}

export async function deleteProfile(id: string) {
  try {
    await fetch(`${API_URL}/profiles/${id}`, { method: 'DELETE' });
    _profiles = _profiles.filter(p => p.id !== id);
    _total--;
  } catch (e) { console.warn('Profile delete failed:', e); }
}
