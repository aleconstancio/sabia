import '@testing-library/jest-dom';

// Mock Leaflet
vi.mock('leaflet', () => ({
  default: {
    map: vi.fn().mockReturnValue({
      setView: vi.fn(),
      on: vi.fn(),
      remove: vi.fn(),
      addLayer: vi.fn(),
      fitBounds: vi.fn(),
      flyTo: vi.fn(),
      flyToBounds: vi.fn(),
      zoomIn: vi.fn(),
      zoomOut: vi.fn(),
      invalidateSize: vi.fn(),
      getCenter: vi.fn().mockReturnValue({ lat: 0, lng: 0 }),
      getBounds: vi.fn().mockReturnValue({ getCenter: vi.fn().mockReturnValue({ lat: 0, lng: 0 }) }),
      getContainer: vi.fn().mockReturnValue({ style: {} }),
    }),
    tileLayer: vi.fn().mockReturnValue({ addTo: vi.fn() }),
    featureGroup: vi.fn().mockReturnValue({ addTo: vi.fn(), getLayers: vi.fn().mockReturnValue([]), clearLayers: vi.fn(), addLayer: vi.fn(), getBounds: vi.fn(), toGeoJSON: vi.fn() }),
    control: { zoom: vi.fn() },
    imageOverlay: vi.fn().mockReturnValue({ addTo: vi.fn(), remove: vi.fn(), setOpacity: vi.fn(), getContainer: vi.fn().mockReturnValue({ style: {} }) }),
    polygon: vi.fn().mockReturnValue({ addTo: vi.fn(), getBounds: vi.fn(), getCenter: vi.fn().mockReturnValue({ lat: 0, lng: 0 }) }),
    Control: { Draw: vi.fn() },
  },
  Map: vi.fn(),
  TileLayer: vi.fn(),
  FeatureGroup: vi.fn(),
  ImageOverlay: vi.fn(),
  Polygon: vi.fn(),
  control: { zoom: vi.fn() },
  Draw: { Event: { CREATED: 'draw:created' } },
}));

// Mock leaflet-draw
vi.mock('leaflet-draw', () => ({}));

// Mock fetch
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

// Mock localStorage
const store: Record<string, string> = {};
globalThis.localStorage = {
  getItem: vi.fn((key: string) => store[key] || null),
  setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
  removeItem: vi.fn((key: string) => { delete store[key]; }),
  clear: vi.fn(() => { Object.keys(store).forEach(k => delete store[k]); }),
  get length() { return Object.keys(store).length; },
  key: vi.fn((i: number) => Object.keys(store)[i] || null),
};
