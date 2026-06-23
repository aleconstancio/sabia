import { logger } from '$lib/utils/logger';

const STORAGE_KEY = 'sabia_gps_location';
const GPS_TIMEOUT_MS = 10_000;

let _latitude = $state<number | null>(null);
let _longitude = $state<number | null>(null);
let _isLoading = $state(false);
let _error = $state<string | null>(null);

export const gpsState = {
  get latitude() { return _latitude; },
  get longitude() { return _longitude; },
  get isLoading() { return _isLoading; },
  get error() { return _error; },
  get hasLocation() { return _latitude !== null && _longitude !== null; },

  loadFromCache() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const data = JSON.parse(raw);
        if (typeof data.lat === 'number' && typeof data.lon === 'number') {
          _latitude = data.lat;
          _longitude = data.lon;
        }
      }
    } catch (e) {
      logger.warn('Failed to load GPS cache:', e);
    }
  },

  requestLocation(): Promise<{ lat: number; lon: number } | null> {
    if (typeof navigator === 'undefined' || !navigator.geolocation) {
      _error = 'Geolocation not supported';
      return Promise.resolve(null);
    }

    _isLoading = true;
    _error = null;

    return new Promise((resolve) => {
      const timeoutId = setTimeout(() => {
        _isLoading = false;
        _error = 'Location request timed out';
        resolve(null);
      }, GPS_TIMEOUT_MS);

      navigator.geolocation.getCurrentPosition(
        (position) => {
          clearTimeout(timeoutId);
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          _latitude = lat;
          _longitude = lon;
          _isLoading = false;
          _error = null;
          try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({ lat, lon, timestamp: Date.now() }));
          } catch (e) {
            logger.warn('Failed to save GPS cache:', e);
          }
          resolve({ lat, lon });
        },
        (err) => {
          clearTimeout(timeoutId);
          _isLoading = false;
          if (err.code === 1) {
            _error = 'Location access denied';
          } else if (err.code === 2) {
            _error = 'Location unavailable';
          } else {
            _error = 'Location request timed out';
          }
          resolve(null);
        },
        { timeout: GPS_TIMEOUT_MS, enableHighAccuracy: false }
      );
    });
  },

  clearLocation() {
    _latitude = null;
    _longitude = null;
    _error = null;
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      logger.warn('Failed to clear GPS cache:', e);
    }
  },
};
