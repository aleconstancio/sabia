/**
 * Map instance state — Leaflet map reference, polygon drawing, and overlay management.
 */
import L from 'leaflet';
import type { Map as LeafletMap } from 'leaflet';

let _map: LeafletMap | null = $state(null);
let _polygonCoords = $state<number[][][] | null>(null);
let _polygonCentroid = $state<{lat: number; lon: number} | null>(null);
let _rasterOverlay: L.ImageOverlay | null = $state(null);
let _hasOverlay = $state(false);
let _lastOverlayPath = $state('');

export const mapInstance = {
  get map() { return _map; },
  set map(v) { _map = v; },
  get polygonCoords() { return _polygonCoords; },
  set polygonCoords(v) { _polygonCoords = v; },
  get polygonCentroid() { return _polygonCentroid; },
  set polygonCentroid(v) { _polygonCentroid = v; },
  get rasterOverlay() { return _rasterOverlay; },
  set rasterOverlay(v) { _rasterOverlay = v; },
  get hasOverlay() { return _hasOverlay; },
  set hasOverlay(v) { _hasOverlay = v; },
  get lastOverlayPath() { return _lastOverlayPath; },
  set lastOverlayPath(v) { _lastOverlayPath = v; },
};
