import type { RegionProfile } from '$lib/api/types';
import { listProfiles, deleteProfile as apiDeleteProfile } from '$lib/api/client';

let _profiles = $state<RegionProfile[]>([]);
let _total = $state(0);
let _isLoading = $state(false);

export const dashboardState = {
  get profiles() { return _profiles; },
  get total() { return _total; },
  get isLoading() { return _isLoading; },
  async loadProfiles() {
    _isLoading = true;
    try {
      const data = await listProfiles({ limit: 100 });
      _profiles = data.profiles || [];
      _total = data.total || 0;
    } catch (e) { console.warn('Dashboard load failed:', e); }
    _isLoading = false;
  },
  async deleteProfile(id: string) {
    try {
      await apiDeleteProfile(id);
      _profiles = _profiles.filter(p => p.id !== id);
      _total--;
    } catch (e) { console.warn('Profile delete failed:', e); }
  },
};
