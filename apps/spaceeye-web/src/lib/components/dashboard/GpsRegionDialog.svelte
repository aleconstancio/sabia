<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { toast } from 'svelte-sonner';
  import { createProfile, geocode } from '$lib/api/client';
  import { gpsState } from '$lib/stores/gps.svelte';
  import { Button } from '$lib/components/ui/button';
  import type { GeocodeResult } from '$lib/api/client';

  let { open = $bindable(false) }: { open: boolean } = $props();

  let regionName = $state('');
  let isCreating = $state(false);
  let mapEl = $state<HTMLDivElement>();
  let leafletMap: unknown = $state(null);

  const POLYGON_OFFSET = 0.0045;

  function gpsToPolygon(lat: number, lon: number) {
    const d = POLYGON_OFFSET;
    return {
      type: 'Polygon' as const,
      coordinates: [[
        [lon - d, lat - d],
        [lon + d, lat - d],
        [lon + d, lat + d],
        [lon - d, lat + d],
        [lon - d, lat - d],
      ]],
    };
  }

  async function reverseGeocode() {
    if (!gpsState.hasLocation) return;
    try {
      const results: GeocodeResult[] = await geocode(
        `${gpsState.latitude},${gpsState.longitude}`
      );
      if (results.length > 0 && results[0].display_name) {
        const parts = results[0].display_name.split(',');
        regionName = parts.slice(0, 2).join(',').trim();
      }
    } catch {
      regionName = 'New Region';
    }
  }

  async function handleCreate() {
    if (!gpsState.hasLocation) return;
    isCreating = true;
    try {
      const polygon = gpsToPolygon(gpsState.latitude!, gpsState.longitude!);
      const result = await createProfile({
        name: regionName || 'New Region',
        polygon,
      });
      toast.success(`Region "${regionName || 'New Region'}" created`);
      open = false;
      goto(`/map?profile=${result.id}`);
    } catch (e) {
      toast.error('Failed to create region');
    } finally {
      isCreating = false;
    }
  }

  onMount(() => {
    if (open && gpsState.hasLocation) {
      reverseGeocode();
    }
  });

  $effect(() => {
    if (open && gpsState.hasLocation && mapEl && !leafletMap) {
      import('leaflet').then((L) => {
        if (!mapEl || leafletMap) return;
        const map = L.map(mapEl, {
          center: [gpsState.latitude!, gpsState.longitude!],
          zoom: 14,
          zoomControl: false,
          dragging: false,
          scrollWheelZoom: false,
        });
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
          subdomains: 'abcd',
          maxZoom: 19,
        }).addTo(map);

        const polygon = gpsToPolygon(gpsState.latitude!, gpsState.longitude!);
        const latlngs = polygon.coordinates[0].map(([lng, lat]) => [lat, lng] as [number, number]);
        L.polygon(latlngs, { color: '#3b82f6', weight: 2, fillOpacity: 0.15 }).addTo(map);
        L.circleMarker([gpsState.latitude!, gpsState.longitude!], {
          radius: 6,
          fillColor: '#3b82f6',
          color: '#fff',
          weight: 2,
          fillOpacity: 0.9,
        }).addTo(map);

        map.fitBounds(L.latLngBounds(latlngs), { padding: [20, 20] });
        leafletMap = map;
      });
    }
  });
</script>

{#if open}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm" onclick={() => open = false}></div>
    <div class="relative z-50 bg-card border border-border rounded-xl shadow-2xl w-full max-w-md p-6 space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold">Quick Add Region from GPS</h2>
        <button class="text-muted-foreground hover:text-foreground" onclick={() => open = false}>✕</button>
      </div>

      {#if gpsState.hasLocation}
        <div class="text-xs text-muted-foreground font-mono">
          📍 {gpsState.latitude?.toFixed(4)}, {gpsState.longitude?.toFixed(4)}
        </div>

        <div bind:this={mapEl} class="w-full h-40 rounded-lg overflow-hidden border border-border"></div>

        <div class="space-y-2">
          <label class="text-xs font-medium text-muted-foreground">Region Name</label>
          <input
            type="text"
            bind:value={regionName}
            placeholder="Enter region name..."
            class="w-full px-3 py-2 rounded-lg bg-background border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>

        <div class="text-[10px] text-muted-foreground">
          Creates a ~1km × 1km polygon centered on your GPS location.
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <Button variant="outline" size="sm" onclick={() => open = false}>Cancel</Button>
          <Button size="sm" disabled={isCreating} onclick={handleCreate}>
            {isCreating ? 'Creating...' : 'Create Region'}
          </Button>
        </div>
      {:else}
        <div class="text-center py-8 text-muted-foreground">
          <p class="mb-2">No GPS location available.</p>
          <p class="text-xs">Click "Locate Me" on the map first.</p>
        </div>
      {/if}
    </div>
  </div>
{/if}
