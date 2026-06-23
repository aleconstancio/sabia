import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('gpsState store', () => {
  beforeEach(() => {
    vi.resetModules();
    localStorage.clear();
  });

  it('has no location by default', async () => {
    const { gpsState } = await import('$lib/stores/gps.svelte');
    expect(gpsState.hasLocation).toBe(false);
    expect(gpsState.latitude).toBeNull();
    expect(gpsState.longitude).toBeNull();
    expect(gpsState.isLoading).toBe(false);
    expect(gpsState.error).toBeNull();
  });

  it('loads cached location from localStorage', async () => {
    localStorage.setItem('horus_gps_location', JSON.stringify({
      lat: -23.5505,
      lon: -46.6333,
      timestamp: Date.now(),
    }));
    const { gpsState } = await import('$lib/stores/gps.svelte');
    gpsState.loadFromCache();
    expect(gpsState.hasLocation).toBe(true);
    expect(gpsState.latitude).toBe(-23.5505);
    expect(gpsState.longitude).toBe(-46.6333);
  });

  it('clears location', async () => {
    localStorage.setItem('horus_gps_location', JSON.stringify({
      lat: -23.5505,
      lon: -46.6333,
      timestamp: Date.now(),
    }));
    const { gpsState } = await import('$lib/stores/gps.svelte');
    gpsState.loadFromCache();
    expect(gpsState.hasLocation).toBe(true);
    gpsState.clearLocation();
    expect(gpsState.hasLocation).toBe(false);
    expect(localStorage.getItem('horus_gps_location')).toBeNull();
  });

  it('handles geolocation permission denied', async () => {
    const mockGetCurrentPosition = vi.fn((_success, error) => {
      error({ code: 1, message: 'User denied Geolocation' });
    });
    Object.defineProperty(navigator, 'geolocation', {
      value: { getCurrentPosition: mockGetCurrentPosition },
      writable: true,
    });

    const { gpsState } = await import('$lib/stores/gps.svelte');
    const result = await gpsState.requestLocation();
    expect(result).toBeNull();
    expect(gpsState.error).toBe('Location access denied');
    expect(gpsState.hasLocation).toBe(false);
  });

  it('handles geolocation timeout', async () => {
    vi.useFakeTimers();
    const mockGetCurrentPosition = vi.fn((_success, _error) => {
      // Never calls success or error — simulates timeout
    });
    Object.defineProperty(navigator, 'geolocation', {
      value: { getCurrentPosition: mockGetCurrentPosition },
      writable: true,
    });

    const { gpsState } = await import('$lib/stores/gps.svelte');
    const promise = gpsState.requestLocation();
    vi.advanceTimersByTime(10001);
    const result = await promise;
    expect(result).toBeNull();
    expect(gpsState.error).toBe('Location request timed out');
    vi.useRealTimers();
  });

  it('successfully requests and caches location', async () => {
    const mockGetCurrentPosition = vi.fn((success) => {
      success({ coords: { latitude: -23.5505, longitude: -46.6333 } });
    });
    Object.defineProperty(navigator, 'geolocation', {
      value: { getCurrentPosition: mockGetCurrentPosition },
      writable: true,
    });

    const { gpsState } = await import('$lib/stores/gps.svelte');
    const result = await gpsState.requestLocation();
    expect(result).toEqual({ lat: -23.5505, lon: -46.6333 });
    expect(gpsState.hasLocation).toBe(true);
    expect(gpsState.latitude).toBe(-23.5505);
    expect(gpsState.longitude).toBe(-46.6333);
    const cached = JSON.parse(localStorage.getItem('horus_gps_location')!);
    expect(cached.lat).toBe(-23.5505);
    expect(cached.lon).toBe(-46.6333);
  });
});
