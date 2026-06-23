<script lang="ts">
  import { onMount } from 'svelte';
  import { dashboardState } from '$lib/stores/dashboard.svelte';
  import { alertStore } from '$lib/stores/alerts.svelte';
  import { historyStore } from '$lib/stores/history.svelte';
  import { gpsState } from '$lib/stores/gps.svelte';
  import { getWeather } from '$lib/api/client';
  import { Sparkline } from '$lib/charts';
  import Badge from '$lib/components/ui/badge/badge.svelte';
  import type { WeatherApiResponse, WeatherExtendedData } from '$lib/api/types';

  let { avgNdvi, ndviTrendData, avgTemp }: {
    avgNdvi: number | null;
    ndviTrendData: number[];
    avgTemp: string | null;
  } = $props();

  let alertCount = $derived(alertStore.alerts.length);
  let ndviDisplay = $derived(avgNdvi != null ? `${(avgNdvi * 100).toFixed(0)}%` : '—');
  let tempDisplay = $derived(avgTemp != null ? `${avgTemp}°C` : '—');
  let analysesCount = $derived(historyStore.all.length);

  let uvDisplay = $derived.by(() => {
    if (!gpsWeatherExtended?.daily?.uv_index_max?.[0]) return null;
    const uv = gpsWeatherExtended.daily.uv_index_max[0];
    return { value: uv, color: uv <= 2 ? 'text-emerald-400' : uv <= 5 ? 'text-yellow-400' : uv <= 7 ? 'text-orange-400' : 'text-red-400' };
  });

  let windDisplay = $derived.by(() => {
    if (!gpsWeatherExtended?.current?.wind_speed_10m) return null;
    return {
      speed: gpsWeatherExtended.current.wind_speed_10m,
      direction: gpsWeatherExtended.current.wind_direction_10m ?? 0,
    };
  });

  let gpsWeather = $state<WeatherApiResponse | null>(null);
  let gpsWeatherLoading = $state(false);
  let gpsWeatherExtended = $state<WeatherExtendedData | null>(null);

  function weatherIcon(code: number | undefined): string {
    if (code == null) return '🌍';
    if (code === 0) return '☀️';
    if (code <= 3) return '🌤️';
    if (code >= 45 && code <= 48) return '🌫️';
    if (code >= 51 && code <= 67) return '🌧️';
    if (code >= 71 && code <= 77) return '❄️';
    if (code >= 80 && code <= 82) return '🌧️';
    if (code >= 95 && code <= 99) return '⛈️';
    return '🌍';
  }

  async function fetchGpsWeather() {
    if (!gpsState.hasLocation) return;
    gpsWeatherLoading = true;
    try {
      const data = await getWeather(gpsState.latitude!, gpsState.longitude!);
      gpsWeather = data;
      gpsWeatherExtended = data as WeatherExtendedData;
    } catch {
      gpsWeather = null;
      gpsWeatherExtended = null;
    } finally {
      gpsWeatherLoading = false;
    }
  }

  onMount(() => {
    gpsState.loadFromCache();
    if (gpsState.hasLocation) {
      fetchGpsWeather();
    }
  });

  $effect(() => {
    gpsState.latitude;
    gpsState.longitude;
    if (gpsState.hasLocation) {
      fetchGpsWeather();
    }
  });
</script>

<div class="grid grid-cols-2 lg:grid-cols-8 gap-2" aria-live="polite">
  <div class="glass-panel rounded-lg p-3 transition-all duration-300">
    <div class="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Regions</div>
    <div class="font-mono font-bold text-lg text-primary">{dashboardState.total}</div>
  </div>

  <div class="glass-panel rounded-lg p-3 transition-all duration-300">
    <div class="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">NDVI Health</div>
    <div class="font-mono font-bold text-lg text-emerald-400">{ndviDisplay}</div>
    {#if ndviTrendData.length > 1}
      <div class="mt-1"><Sparkline data={ndviTrendData} width={80} height={16} color="#34d399" /></div>
    {/if}
  </div>

  <div class="glass-panel rounded-lg p-3 transition-all duration-300">
    <div class="text-[10px] uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-1.5">
      Active Alerts
      {#if alertCount > 0}
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-destructive"></span>
        </span>
      {/if}
    </div>
    <div class="font-mono font-bold text-lg {alertCount > 0 ? 'text-destructive' : 'text-emerald-400'}">{alertCount}</div>
  </div>

  <div class="glass-panel rounded-lg p-3 transition-all duration-300">
    <div class="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Temperature</div>
    <div class="font-mono font-bold text-lg text-blue-400">{tempDisplay}</div>
  </div>

  <div class="glass-panel rounded-lg p-3 transition-all duration-300">
    <div class="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Analyses</div>
    <div class="font-mono font-bold text-lg text-violet-400">{analysesCount}</div>
  </div>

  {#if gpsState.hasLocation}
    <div class="glass-panel rounded-lg p-3 transition-all duration-300">
      <div class="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">📍 Nearby Weather</div>
      {#if gpsWeatherLoading}
        <div class="font-mono font-bold text-lg text-cyan-400 animate-pulse">...</div>
      {:else if gpsWeather?.current}
        <div class="flex items-center gap-1.5">
          <span class="text-lg">{weatherIcon(gpsWeather.current.weather_code)}</span>
          <span class="font-mono font-bold text-lg text-cyan-400">
            {gpsWeather.current.temperature_2m != null ? `${gpsWeather.current.temperature_2m}°C` : '—'}
          </span>
        </div>
        <div class="text-[10px] text-muted-foreground mt-0.5">
          💧 {gpsWeather.current.relative_humidity_2m ?? '—'}%
        </div>
      {:else}
        <div class="font-mono font-bold text-lg text-cyan-400">—</div>
      {/if}
    </div>
  {/if}

  {#if gpsState.hasLocation && uvDisplay}
    <div class="glass-panel rounded-lg p-3 transition-all duration-300">
      <div class="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">UV Index</div>
      <div class="font-mono font-bold text-lg {uvDisplay.color}">{uvDisplay.value.toFixed(1)}</div>
    </div>
  {/if}

  {#if gpsState.hasLocation && windDisplay}
    <div class="glass-panel rounded-lg p-3 transition-all duration-300">
      <div class="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Wind</div>
      <div class="flex items-center gap-1.5">
        <svg class="w-4 h-4 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
             style="transform: rotate({windDisplay.direction}deg)">
          <path d="M12 2v20M2 12l10-10 10 10"/>
        </svg>
        <span class="font-mono font-bold text-lg text-cyan-400">{windDisplay.speed.toFixed(1)}</span>
        <span class="text-[10px] text-muted-foreground">km/h</span>
      </div>
    </div>
  {/if}
</div>
