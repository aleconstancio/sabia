<script lang="ts">
  import { onMount } from 'svelte';
  import { gpsState } from '$lib/stores/gps.svelte';
  import { getWeather, getAirQuality, getDisasterAlerts, getDeforestationAlerts } from '$lib/api/client';
  import type { WeatherApiResponse, AirQualityData, DisasterAlertsResponse, DeforestationAlertsResponse } from '$lib/api/types';
  import WeatherAirTab from './tabs/WeatherAirTab.svelte';
  import DisastersTab from './tabs/DisastersTab.svelte';
  import DeforestationTab from './tabs/DeforestationTab.svelte';

  let activeTab = $state<'weather' | 'disasters' | 'deforestation'>('weather');

  let weather = $state<WeatherApiResponse | null>(null);
  let airQuality = $state<AirQualityData | null>(null);
  let disasters = $state<DisasterAlertsResponse | null>(null);
  let deforestation = $state<DeforestationAlertsResponse | null>(null);

  let loadingWeather = $state(false);
  let loadingAir = $state(false);
  let loadingDisasters = $state(false);
  let loadingDeforestation = $state(false);

  async function fetchAllData() {
    if (!gpsState.hasLocation) return;
    const lat = gpsState.latitude!;
    const lon = gpsState.longitude!;

    loadingWeather = true;
    loadingAir = true;
    loadingDisasters = true;
    loadingDeforestation = true;

    const [w, a, d, def] = await Promise.allSettled([
      getWeather(lat, lon),
      getAirQuality(lat, lon),
      getDisasterAlerts(lat, lon),
      getDeforestationAlerts(lat, lon),
    ]);

    if (w.status === 'fulfilled') weather = w.value as WeatherApiResponse;
    if (a.status === 'fulfilled') airQuality = a.value as AirQualityData;
    if (d.status === 'fulfilled') disasters = d.value as DisasterAlertsResponse;
    if (def.status === 'fulfilled') deforestation = def.value as DeforestationAlertsResponse;

    loadingWeather = false;
    loadingAir = false;
    loadingDisasters = false;
    loadingDeforestation = false;
  }

  onMount(() => {
    gpsState.loadFromCache();
    if (gpsState.hasLocation) fetchAllData();
  });

  $effect(() => {
    gpsState.latitude;
    gpsState.longitude;
    if (gpsState.hasLocation) fetchAllData();
  });
</script>

{#if gpsState.hasLocation}
  <div class="glass-panel rounded-lg border border-border overflow-hidden">
    <div class="flex items-center border-b border-border">
      {#each [
        { id: 'weather', label: '🌤️ Weather/Air' },
        { id: 'disasters', label: '⚠️ Disasters' },
        { id: 'deforestation', label: '🪓 Deforestation' },
      ] as tab}
        <button
          class="flex-1 px-3 py-2 text-xs font-medium transition-colors {activeTab === tab.id ? 'bg-primary/10 text-primary border-b-2 border-primary' : 'text-muted-foreground hover:text-foreground'}"
          onclick={() => activeTab = tab.id as typeof activeTab}
        >
          {tab.label}
        </button>
      {/each}
    </div>

    <div class="p-3 max-h-[300px] overflow-y-auto">
      {#if activeTab === 'weather'}
        <WeatherAirTab {weather} {airQuality} loading={loadingWeather || loadingAir} />
      {:else if activeTab === 'disasters'}
        <DisastersTab data={disasters} loading={loadingDisasters} />
      {:else if activeTab === 'deforestation'}
        <DeforestationTab data={deforestation} loading={loadingDeforestation} />
      {/if}
    </div>
  </div>
{/if}