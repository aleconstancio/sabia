import type { Map as LeafletMap, Layer } from 'leaflet';
import { logger } from '$lib/utils/logger';

let _previousPolygon: Layer | null = null;

export async function restorePolygonOnMap(coords: number[][][]) {
  try {
    const L = await import('leaflet');
    const { mapState } = await import('$lib/stores/map.svelte');
    if (!mapState.map || !coords) return;
    if (_previousPolygon) {
      mapState.map.removeLayer(_previousPolygon);
      _previousPolygon = null;
    }
    const polygon = L.polygon(coords[0].map((c: number[]) => [c[1], c[0]]));
    _previousPolygon = polygon;
    const map = mapState.map as LeafletMap;
    map.addLayer(polygon);
    map.fitBounds(polygon.getBounds());
    const center = polygon.getCenter();
    mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
    return center;
  } catch (e) {
    logger.warn('Failed to restore polygon on map:', e);
  }
}
