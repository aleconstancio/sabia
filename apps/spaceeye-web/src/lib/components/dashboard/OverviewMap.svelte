<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { dashboardState } from '$lib/stores/dashboard.svelte';
  import { getNdviColor } from '$lib/utils/dashboard';
  import L from 'leaflet';
  import 'leaflet/dist/leaflet.css';

  let container = $state<HTMLDivElement>();
  let map: L.Map | undefined;
  let markers: L.CircleMarker[] = [];
  let _lastProfileIds = '';

  function updateMarkers() {
    if (!map) return;

    const currentIds = dashboardState.profiles.map(p => p.id).join(',');
    if (currentIds === _lastProfileIds) return;
    _lastProfileIds = currentIds;

    markers.forEach(m => m.remove());
    markers = [];

    const profiles = dashboardState.profiles;
    const bounds: [number, number][] = [];

    profiles.forEach(p => {
      const centroid = p.centroid as { lat: number; lon: number } | null;
      if (!centroid) return;

      const ndvi = (p.satellite_data?.stats?.mean as number) ?? null;
      const color = getNdviColor(ndvi);

      const marker = L.circleMarker([centroid.lat, centroid.lon], {
        radius: 8,
        fillColor: color,
        color: '#fff',
        weight: 2,
        fillOpacity: 0.8,
      })
        .addTo(map!)
        .bindTooltip(p.name || 'Unnamed Region', {
          className: 'text-xs bg-card border border-border text-foreground',
        })
        .on('click', () => goto(`/map?profile=${p.id}`));

      markers.push(marker);
      bounds.push([centroid.lat, centroid.lon]);
    });

    if (bounds.length > 0) {
      map!.fitBounds(bounds, { padding: [30, 30], maxZoom: 12 });
    }
  }

  $effect(() => {
    dashboardState.profiles;
    if (map) updateMarkers();
  });

  onMount(() => {
    if (!container) return;
    map = L.map(container, {
      center: [-14.235, -51.925],
      zoom: 4,
      zoomControl: false,
      scrollWheelZoom: false,
      dragging: false,
      keyboard: false,
      doubleClickZoom: false,
      boxZoom: false,
      trackResize: true,
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19,
    }).addTo(map);

    updateMarkers();
  });

  onDestroy(() => {
    if (map) {
      map.remove();
      map = undefined;
    }
  });
</script>

<div class="rounded-lg overflow-hidden border border-border h-full min-h-[280px]">
  <div bind:this={container} class="w-full h-full"></div>
</div>
