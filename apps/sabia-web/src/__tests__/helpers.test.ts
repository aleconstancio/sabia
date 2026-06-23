import { describe, it, expect } from 'vitest';
import { getNdviColor, formatTimeAgo } from '$lib/utils/dashboard';

describe('getNdviColor', () => {
  it('returns gray for null', () => {
    expect(getNdviColor(null)).toBe('#6b7280');
  });

  it('returns green for high NDVI (> 0.5)', () => {
    expect(getNdviColor(0.7)).toBe('#10b981');
    expect(getNdviColor(0.6)).toBe('#10b981');
  });

  it('returns yellow for medium NDVI (> 0.3, <= 0.5)', () => {
    expect(getNdviColor(0.5)).toBe('#eab308');
    expect(getNdviColor(0.4)).toBe('#eab308');
  });

  it('returns red for low NDVI (<= 0.3)', () => {
    expect(getNdviColor(0.3)).toBe('#ef4444');
    expect(getNdviColor(0.2)).toBe('#ef4444');
    expect(getNdviColor(0)).toBe('#ef4444');
  });
});

describe('formatTimeAgo', () => {
  it('returns empty string for null', () => {
    expect(formatTimeAgo(null)).toBe('');
  });

  it('returns "just now" for recent timestamps', () => {
    const now = new Date().toISOString();
    expect(formatTimeAgo(now)).toBe('just now');
  });

  it('returns minutes ago', () => {
    const fiveMinAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString();
    expect(formatTimeAgo(fiveMinAgo)).toBe('5m ago');
  });

  it('returns hours ago', () => {
    const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString();
    expect(formatTimeAgo(twoHoursAgo)).toBe('2h ago');
  });

  it('returns days ago', () => {
    const threeDaysAgo = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString();
    expect(formatTimeAgo(threeDaysAgo)).toBe('3d ago');
  });
});
