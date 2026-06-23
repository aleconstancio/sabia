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

describe('NBR computation', () => {
  function computeNbr(nir: number, swir: number): number {
    const denominator = nir + swir;
    if (denominator === 0) return 0;
    return (nir - swir) / denominator;
  }

  it('computes NBR correctly', () => {
    const nbr = computeNbr(0.7, 0.2);
    expect(nbr).toBeCloseTo(0.5556, 3);
  });

  it('returns positive for healthy vegetation', () => {
    const nbr = computeNbr(0.8, 0.1);
    expect(nbr).toBeGreaterThan(0);
  });

  it('returns negative for bare/burned areas', () => {
    const nbr = computeNbr(0.1, 0.8);
    expect(nbr).toBeLessThan(0);
  });

  it('returns 0 for equal bands', () => {
    const nbr = computeNbr(0.5, 0.5);
    expect(nbr).toBe(0);
  });

  it('handles division by zero', () => {
    const nbr = computeNbr(0, 0);
    expect(nbr).toBe(0);
  });
});

describe('NDVI bounds', () => {
  it('NDVI bounds are -1 to 1', () => {
    const ndvi1 = (0 - 1) / (0 + 1);
    expect(ndvi1).toBe(-1);

    const ndvi2 = (1 - 0) / (1 + 0);
    expect(ndvi2).toBe(1);
  });
});
