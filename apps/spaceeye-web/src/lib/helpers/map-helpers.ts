import type { Map as LeafletMap } from 'leaflet';

export async function restorePolygonOnMap(coords: number[][][]) {
  try {
    const L = await import('leaflet');
    const { mapState } = await import('$lib/stores/map.svelte');
    if (!mapState.map || !coords) return;
    const polygon = (L as any).polygon(coords[0].map((c: number[]) => [c[1], c[0]]));
    const map = mapState.map as LeafletMap;
    map.addLayer(polygon);
    map.fitBounds(polygon.getBounds());
    const center = polygon.getCenter();
    mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
    return center;
  } catch (e) {
    console.warn('Failed to restore polygon on map:', e);
  }
}
