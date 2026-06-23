<script lang="ts">
  import type { WeatherData } from '$lib/api/types';
  import { api } from '$lib/api/client';
  import { logger } from '$lib/utils/logger';
  import { Spinner } from '$lib/components/ui/spinner';

  interface WeatherApiResponse {
    current?: {
      temperature_2m?: number;
      apparent_temperature?: number;
      relative_humidity_2m?: number;
      precipitation?: number;
      soil_moisture_0_to_7cm?: number;
    };
    daily?: {
      precipitation_sum?: number[];
    };
  }

  let {
    lat = 0,
    lon = 0,
    onWeatherData = (_data: WeatherData) => {},
  }: { lat: number; lon: number; onWeatherData?: (data: WeatherData) => void } = $props();

  let data: WeatherApiResponse | null = $state(null);
  let loading = $state(false);
  let error = $state('');

  let controller: AbortController | null = null;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  $effect(() => {
    if (lat && lon) {
      if (controller) controller.abort();
      if (timeoutId) clearTimeout(timeoutId);

      timeoutId = setTimeout(async () => {
        controller = new AbortController();
        loading = true;
        error = '';
        try {
          data = await api.get(`/weather/${lat}/${lon}`);
        } catch (e: unknown) {
          if (e instanceof Error && e.name === 'AbortError') return;
          error = e instanceof Error ? e.message : String(e);
        } finally {
          loading = false;
        }
      }, 300);

      return () => {
        if (timeoutId) clearTimeout(timeoutId);
        controller?.abort();
      };
    }
  });

  $effect(() => {
    if (data?.current) {
      onWeatherData({
        temperature: data.current.temperature_2m ?? 0,
        precipitation: data.current.precipitation ?? 0,
        wind_speed: 0,
        humidity: data.current.relative_humidity_2m ?? 0,
      });
    }
  });
</script>

<div class="rounded-lg border border-border bg-card p-4">
  <h3 class="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Climate</h3>
  {#if loading}
    <div class="flex items-center gap-2 text-sm text-muted-foreground">
      <Spinner size="xs" />
      <span>Loading...</span>
    </div>
  {:else if error}
    <p class="text-sm text-destructive">{error}</p>
  {:else if data}
    <div class="grid grid-cols-2 gap-3">
      <div>
        <p class="text-xs text-muted-foreground">Temperature</p>
        <p class="text-lg font-bold">{data.current?.temperature_2m ?? '—'}°C</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Feels Like</p>
        <p class="text-lg font-bold">{data.current?.apparent_temperature ?? '—'}°C</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Humidity</p>
        <p class="text-lg font-bold">{data.current?.relative_humidity_2m ?? '—'}%</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Precipitation</p>
        <p class="text-lg font-bold">{data.current?.precipitation ?? '—'} mm</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Soil (7cm)</p>
        <p class="text-lg font-bold">{data.current?.soil_moisture_0_to_7cm?.toFixed(2) ?? '—'} m³/m³</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">7-day Forecast</p>
        <p class="text-lg font-bold">{data.daily?.precipitation_sum?.[0] ?? '—'} mm</p>
      </div>
    </div>
  {/if}
</div>