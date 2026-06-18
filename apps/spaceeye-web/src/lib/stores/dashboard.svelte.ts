import type { RegionProfile } from '$lib/api/types';
import { listProfiles, deleteProfile as apiDeleteProfile } from '$lib/api/client';
import { logger } from '$lib/utils/logger';

let _profiles = $state<RegionProfile[]>([]);
let _total = $state(0);
let _isLoading = $state(false);
let _error = $state('');
let _lastUpdated = $state(0);
let _autoRefreshTimer: ReturnType<typeof setInterval> | null = null;

export const dashboardState = {
  get profiles() { return _profiles; },
  get total() { return _total; },
  get isLoading() { return _isLoading; },
  get error() { return _error; },
  get lastUpdated() { return _lastUpdated; },
  async loadProfiles() {
    _isLoading = true;
    _error = '';
    try {
      const data = await listProfiles({ limit: 100 });
      _profiles = data.profiles || [];
      _total = data.total || 0;
      _lastUpdated = Date.now();
      _isLoading = false;
    } catch (e: unknown) {
      _error = e instanceof Error ? e.message : String(e) || 'Failed to load profiles';
      logger.error('Dashboard load failed:', e);
      _isLoading = false;
    }
  },
  startAutoRefresh(intervalMs = 30000) {
    this.stopAutoRefresh();
    _autoRefreshTimer = setInterval(() => this.loadProfiles(), intervalMs);
  },
  stopAutoRefresh() {
    if (_autoRefreshTimer !== null) {
      clearInterval(_autoRefreshTimer);
      _autoRefreshTimer = null;
    }
  },
  async deleteProfile(id: string) {
    try {
      await apiDeleteProfile(id);
      _profiles = _profiles.filter(p => p.id !== id);
      _total = Math.max(0, _total - 1);
    } catch (e: unknown) { _error = e instanceof Error ? e.message : String(e) || 'Failed to delete profile'; logger.error('Profile delete failed:', e); }
  },
};
