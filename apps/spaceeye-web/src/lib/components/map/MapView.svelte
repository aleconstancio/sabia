<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import L from 'leaflet';
  import { createLeafletMap } from '$lib/helpers/leaflet';
  import { mapState } from '$lib/stores/map.svelte';
  import { SPECTRAL_PRODUCTS } from '$lib/constants';
  import { searchImages, processImage } from '$lib/api/processing';
  import { toast } from 'svelte-sonner';
  import { logger } from '$lib/utils/logger';

  let {
    measureMode = false,
    onPolygonCreated = () => {},
    onMeasure = () => {},
  }: {
    measureMode?: boolean;
    onPolygonCreated?: () => void;
    onMeasure?: (coords: { lat: number; lng: number }) => void;
  } = $props();

  let mapContainer: HTMLDivElement;
  let leafletMap: ReturnType<typeof createLeafletMap> | null = null;
  let _rafId = 0;

  onMount(async () => {
    if (!browser || !mapContainer) return;

    leafletMap = createLeafletMap(mapContainer, {
      enableMouseMove: true,
      onPolygonCreated: (coords) => {
        mapState.polygonCoords = coords;
        mapState.showPolygonModal = true;
        onPolygonCreated();
      },
    });

    await leafletMap.init();

    // Handle share URL parameters
    if (browser) {
      const params = new URLSearchParams(window.location.search);
      const coords = params.get('coords');
      const image = params.get('image');
      const product = params.get('product');

      if (coords && image && product) {
        try {
          const parsed = JSON.parse(coords);
          if (!Array.isArray(parsed) || !parsed.every((ring: unknown) =>
            Array.isArray(ring) && ring.every((coord: unknown) =>
              Array.isArray(coord) && coord.length >= 2 && coord.every((v: unknown) => typeof v === 'number')
            )
          )) {
            toast.error('Invalid coordinates in shared link');
            return;
          }
          const allowedProducts = SPECTRAL_PRODUCTS.map(p => p.value);
          if (!allowedProducts.includes(product)) {
            toast.error('Invalid product in shared link');
            return;
          }
          mapState.polygonCoords = parsed;
          mapState.selectedProduct = product;
          const polygon = L.polygon(parsed[0].map((c: number[]) => [c[1], c[0]]));
          leafletMap?.map?.addLayer(polygon);
          leafletMap?.map?.fitBounds(polygon.getBounds());
          const center = polygon.getCenter();
          mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
          searchImages().then(() => {
            processImage(image);
          }).catch((e) => {
            logger.warn('Share URL auto-process failed:', e);
          });
        } catch(e) { logger.warn('Invalid share URL params:', e); }
      }
    }

    // Handle mouse move for measurement (throttled via rAF)
    leafletMap?.map?.on('mousemove', (e: L.LeafletMouseEvent) => {
      cancelAnimationFrame(_rafId);
      _rafId = requestAnimationFrame(() => {
        if (measureMode) {
          onMeasure({ lat: parseFloat(e.latlng.lat.toFixed(4)), lng: parseFloat(e.latlng.lng.toFixed(4)) });
        }
      });
    });
  });

  onDestroy(() => {
    cancelAnimationFrame(_rafId);
    leafletMap?.destroy();
  });

  export function getMap() {
    return leafletMap?.map ?? null;
  }

  export function getDrawnItems() {
    return leafletMap?.drawnItems ?? null;
  }
</script>

<div bind:this={mapContainer} id="map" class="flex-1 min-h-0" role="application" aria-label="SpaceEye Interactive Map"></div>