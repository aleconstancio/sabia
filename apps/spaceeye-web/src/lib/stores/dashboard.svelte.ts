import type { RegionProfile } from '$lib/api/types';
import { listProfiles, deleteProfile as apiDeleteProfile } from '$lib/api/client';

let _profiles = $state<RegionProfile[]>([]);
let _total = $state(0);
let _isLoading = $state(false);
let _error = $state('');

export const dashboardState = {
  get profiles() { return _profiles; },
  get total() { return _total; },
  get isLoading() { return _isLoading; },
  get error() { return _error; },
  async loadProfiles() {
    _isLoading = true;
    _error = '';
    try {
      const data = await listProfiles({ limit: 100 });
      _profiles = data.profiles || [];
      _total = data.total || 0;
    } catch (e) { _error = (e as Error).message || 'Failed to load profiles'; console.error('Dashboard load failed:', e); }
    _isLoading = false;
  },
  async deleteProfile(id: string) {
    try {
      await apiDeleteProfile(id);
      _profiles = _profiles.filter(p => p.id !== id);
      _total--;
    } catch (e) { _error = (e as Error).message || 'Failed to delete profile'; console.error('Profile delete failed:', e); }
  },
};
