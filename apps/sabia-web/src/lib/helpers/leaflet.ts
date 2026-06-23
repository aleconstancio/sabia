/**
 * Shared Leaflet map initialization composable.
 * 
 * Provides consistent map setup across main map page and module pages.
 */
import { onMount, onDestroy } from 'svelte';
import { browser } from '$app/environment';
import L from 'leaflet';
import { mapState } from '$lib/stores/map.svelte';

export interface LeafletMapOptions {
  /** Initial center coordinates [lat, lng] */
  center?: [number, number];
  /** Initial zoom level */
  zoom?: number;
  /** Enable keyboard navigation */
  keyboard?: boolean;
  /** Enable drawing controls */
  enableDraw?: boolean;
  /** Enable mouse move tracking */
  enableMouseMove?: boolean;
  /** Callback when a polygon is drawn */
  onPolygonCreated?: (coords: number[][][]) => void;
}

export interface LeafletMapContext {
  /** The Leaflet map instance */
  map: L.Map | null;
  /** The drawn items feature group */
  drawnItems: L.FeatureGroup | null;
  /** Initialize the map */
  init: () => Promise<void>;
  /** Clean up the map */
  destroy: () => void;
}

/**
 * Creates a Leaflet map with consistent configuration.
 * 
 * @param container - HTML element to render the map into
 * @param options - Configuration options
 * @returns Map context with init/destroy lifecycle methods
 */
export function createLeafletMap(
  container: HTMLDivElement,
  options: LeafletMapOptions = {}
): LeafletMapContext {
  const {
    center = [-3.359202, -23.211370],
    zoom = 3,
    keyboard = true,
    enableDraw = true,
    enableMouseMove = false,
    onPolygonCreated,
  } = options;

  let map: L.Map | null = null;
  let drawnItems: L.FeatureGroup | null = null;
  let _rafId = 0;

  const init = async () => {
    if (!browser || !container) return;

    // Load Leaflet draw plugin
    await import('leaflet-draw');

    // Create tile layer
    const tileLayer = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      { attribution: 'Tiles &copy; Esri', maxZoom: 19 }
    );

    // Create map instance
    map = L.map(container, {
      center,
      zoom,
      layers: [tileLayer],
      keyboard,
    });

    // Store in global state
    mapState.map = map;

    // Create drawn items layer
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Add draw controls
    if (enableDraw) {
      const drawControl = new L.Control.Draw({
        edit: { featureGroup: drawnItems },
        draw: {
          polygon: {},
          rectangle: {},
          polyline: false,
          circle: false,
          circlemarker: false,
          marker: false,
        },
      });
      map.addControl(drawControl);
    }

    // Handle draw events
    map.on(L.Draw.Event.CREATED, ((e: L.DrawEvents.Created) => {
      drawnItems?.addLayer(e.layer);
      const coords = e.layer.toGeoJSON().geometry.coordinates;
      mapState.polygonCoords = coords;
      const center = (e.layer as L.Polygon).getCenter();
      mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
      
      if (onPolygonCreated) {
        onPolygonCreated(coords);
      }
    }) as unknown as L.LeafletEventHandlerFn);

    // Enable mouse move tracking (throttled via rAF)
    if (enableMouseMove) {
      map.on('mousemove', (e: L.LeafletMouseEvent) => {
        cancelAnimationFrame(_rafId);
        _rafId = requestAnimationFrame(() => {
          mapState.polygonCentroid = { lat: e.latlng.lat, lon: e.latlng.lng };
        });
      });
    }
  };

  const destroy = () => {
    if (map) {
      map.remove();
      map = null;
    }
  };

  return {
    get map() { return map; },
    get drawnItems() { return drawnItems; },
    init,
    destroy,
  };
}