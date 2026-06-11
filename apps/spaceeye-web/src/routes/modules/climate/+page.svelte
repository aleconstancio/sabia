<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import L from 'leaflet';
  import { mapState } from '$lib/stores/map.svelte';
  import ModuleSidebar from '$lib/components/modules/ModuleSidebar.svelte';

  let mapContainer: HTMLDivElement;
  let map: L.Map | null = null;

  onMount(async () => {
    if (!browser || !mapContainer) return;
    await import('leaflet-draw');

    const tileLayer = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      { attribution: 'Tiles &copy; Esri', maxZoom: 19 }
    );

    map = L.map(mapContainer, {
      center: [-3.359202, -23.211370],
      zoom: 3,
      layers: [tileLayer],
      keyboard: false,
    });

    mapState.map = map;
    mapState.selectedProduct = 'TCI';

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
      edit: { featureGroup: drawnItems },
      draw: { polygon: true, rectangle: true, polyline: false, circle: false, circlemarker: false, marker: false },
    });
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, (e: any) => {
      drawnItems.addLayer(e.layer);
      mapState.polygonCoords = e.layer.toGeoJSON().geometry.coordinates;
      const center = e.layer.getCenter();
      mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
    });
  });
</script>

<div class="flex flex-1 min-h-0">
  <ModuleSidebar module="climate" />
  <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
</div>
