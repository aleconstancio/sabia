<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { dashboardState } from '$lib/stores/dashboard.svelte';
  import { gpsState } from '$lib/stores/gps.svelte';
  import { getNdviColor } from '$lib/utils/dashboard';
  import L from 'leaflet';
  import 'leaflet/dist/leaflet.css';

  let container = $state<HTMLDivElement>();
  let map: L.Map | undefined;
  let markers: L.CircleMarker[] = [];
  let gpsMarker: L.CircleMarker | undefined;
  let _lastProfileIds = '';
  let _lastGpsKey = '';

  const DEFAULT_CENTER: [number, number] = [-14.235, -51.925];
  const DEFAULT_ZOOM = 4;
  const GPS_ZOOM = 10;

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

  function updateGpsMarker() {
    if (!map) return;

    const gpsKey = `${gpsState.latitude},${gpsState.longitude}`;
    if (gpsKey === _lastGpsKey) return;
    _lastGpsKey = gpsKey;

    if (gpsMarker) {
      gpsMarker.remove();
      gpsMarker = undefined;
    }

    if (gpsState.hasLocation) {
      gpsMarker = L.circleMarker([gpsState.latitude!, gpsState.longitude!], {
        radius: 8,
        fillColor: '#3b82f6',
        color: '#93c5fd',
        weight: 3,
        fillOpacity: 0.7,
        className: 'gps-pulse-marker',
      })
        .addTo(map!)
        .bindTooltip('Your location', {
          className: 'text-xs bg-card border border-border text-foreground',
        });
    }
  }

  function centerOnGps() {
    if (!map || !gpsState.hasLocation) return;
    map.flyTo([gpsState.latitude!, gpsState.longitude!], GPS_ZOOM, { duration: 1.5 });
  }

  async function handleLocate() {
    if (gpsState.hasLocation) {
      centerOnGps();
    } else {
      await gpsState.requestLocation();
      if (gpsState.hasLocation) {
        centerOnGps();
      }
    }
  }

  $effect(() => {
    dashboardState.profiles;
    if (map) updateMarkers();
  });

  $effect(() => {
    gpsState.latitude;
    gpsState.longitude;
    if (map) {
      updateGpsMarker();
      if (gpsState.hasLocation && _lastGpsKey !== '') {
        centerOnGps();
      }
    }
  });

  onMount(() => {
    if (!container) return;

    gpsState.loadFromCache();

    const initialCenter: [number, number] = gpsState.hasLocation
      ? [gpsState.latitude!, gpsState.longitude!]
      : DEFAULT_CENTER;
    const initialZoom = gpsState.hasLocation ? GPS_ZOOM : DEFAULT_ZOOM;

    map = L.map(container, {
      center: initialCenter,
      zoom: initialZoom,
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
    updateGpsMarker();
  });

  onDestroy(() => {
    if (map) {
      map.remove();
      map = undefined;
    }
  });
</script>

<div class="relative rounded-lg overflow-hidden border border-border h-full min-h-[280px]">
  <div bind:this={container} class="w-full h-full"></div>
  <button
    onclick={handleLocate}
    disabled={gpsState.isLoading}
    class="absolute bottom-2 right-2 z-[1000] w-8 h-8 rounded-md bg-card/90 backdrop-blur-sm border border-border flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-card transition-all disabled:opacity-50"
    title="Center on my location"
  >
    {#if gpsState.isLoading}
      <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
        <path d="M3 3v5h5"/>
      </svg>
    {:else}
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 2v4m0 12v4M2 12h4m12 0h4"/>
      </svg>
    {/if}
  </button>
</div>

<style>
  :global(.gps-pulse-marker) {
    animation: gps-pulse 2s ease-in-out infinite;
  }
  @keyframes gps-pulse {
    0%, 100% { opacity: 0.7; }
    50% { opacity: 1; }
  }
</style>
