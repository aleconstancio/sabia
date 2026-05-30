import { describe, it, expect } from 'vitest';

// Test NDVI computation directly
function computeNdvi(nir: number, red: number): number {
  const denominator = nir + red;
  if (denominator === 0) return 0;
  return Math.max(-1, Math.min(1, (nir - red) / denominator));
}

describe('NDVI computation', () => {
  it('returns positive for healthy vegetation (NIR >> Red)', () => {
    const ndvi = computeNdvi(0.8, 0.1);
    expect(ndvi).toBeGreaterThan(0);
    expect(ndvi).toBeCloseTo(0.778, 2);
  });

  it('returns negative for bare soil (Red >> NIR)', () => {
    const ndvi = computeNdvi(0.1, 0.8);
    expect(ndvi).toBeLessThan(0);
    expect(ndvi).toBeCloseTo(-0.778, 2);
  });

  it('returns 0 when NIR equals Red', () => {
    const ndvi = computeNdvi(0.5, 0.5);
    expect(ndvi).toBe(0);
  });

  it('handles division by zero', () => {
    const ndvi = computeNdvi(0, 0);
    expect(ndvi).toBe(0);
  });

  it('clips values to [-1, 1] range', () => {
    const ndviHigh = computeNdvi(200, 1);
    expect(ndviHigh).toBeLessThanOrEqual(1);
    const ndviLow = computeNdvi(1, 200);
    expect(ndviLow).toBeGreaterThanOrEqual(-1);
  });
});

describe('NDWI computation', () => {
  function computeNdwi(green: number, nir: number): number {
    const denominator = green + nir;
    if (denominator === 0) return 0;
    return Math.max(-1, Math.min(1, (green - nir) / denominator));
  }

  it('returns positive for water (Green > NIR)', () => {
    const ndwi = computeNdwi(0.5, 0.1);
    expect(ndwi).toBeGreaterThan(0);
  });

  it('returns negative for vegetation (NIR > Green)', () => {
    const ndwi = computeNdwi(0.1, 0.5);
    expect(ndwi).toBeLessThan(0);
  });
});

describe('EVI formula structure', () => {
  function computeEvi(nir: number, red: number, blue: number): number {
    const denominator = nir + 6 * red - 7.5 * blue + 1;
    if (denominator === 0) return 0;
    return Math.max(-1, Math.min(1, 2.5 * (nir - red) / denominator));
  }

  it('is positive for dense vegetation', () => {
    const evi = computeEvi(0.9, 0.1, 0.05);
    expect(evi).toBeGreaterThan(0);
    expect(evi).toBeCloseTo(0.941, 2);
  });

  it('handles blue band correction with stable denominator', () => {
    const eviLowHaze = computeEvi(0.6, 0.2, 0.05);
    const eviHighHaze = computeEvi(0.6, 0.2, 0.2);
    expect(eviLowHaze).toBeGreaterThan(0);
    expect(eviHighHaze).toBeGreaterThan(0);
  });
});
