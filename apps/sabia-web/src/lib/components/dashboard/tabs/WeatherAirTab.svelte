<script lang="ts">
  import type { WeatherApiResponse, AirQualityData } from '$lib/api/types';

  let { weather, airQuality, loading }: {
    weather: WeatherApiResponse | null;
    airQuality: AirQualityData | null;
    loading: boolean;
  } = $props();

  function aqiColor(aqi: number): string {
    if (aqi <= 50) return 'text-emerald-400';
    if (aqi <= 100) return 'text-yellow-400';
    if (aqi <= 150) return 'text-orange-400';
    if (aqi <= 200) return 'text-red-400';
    return 'text-purple-400';
  }

  function aqiLabel(aqi: number): string {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy for Sensitive';
    if (aqi <= 200) return 'Unhealthy';
    return 'Very Unhealthy';
  }
</script>

{#if loading}
  <div class="space-y-3">
    <div class="h-20 bg-muted/30 rounded-lg animate-pulse"></div>
    <div class="h-20 bg-muted/30 rounded-lg animate-pulse"></div>
  </div>
{:else}
  <div class="space-y-4">
    {#if weather?.current}
      <div class="space-y-2">
        <h4 class="text-xs font-semibold text-muted-foreground uppercase">Current Conditions</h4>
        <div class="grid grid-cols-2 gap-2">
          <div class="glass-panel rounded-lg p-2">
            <div class="text-[10px] text-muted-foreground">Temp</div>
            <div class="font-mono font-bold text-sm">{weather.current.temperature_2m ?? '—'}°C</div>
          </div>
          <div class="glass-panel rounded-lg p-2">
            <div class="text-[10px] text-muted-foreground">Humidity</div>
            <div class="font-mono font-bold text-sm">{weather.current.relative_humidity_2m ?? '—'}%</div>
          </div>
          <div class="glass-panel rounded-lg p-2">
            <div class="text-[10px] text-muted-foreground">Wind</div>
            <div class="font-mono font-bold text-sm">{weather.current.wind_speed_10m ?? '—'} km/h</div>
          </div>
          <div class="glass-panel rounded-lg p-2">
            <div class="text-[10px] text-muted-foreground">Precipitation</div>
            <div class="font-mono font-bold text-sm">{weather.current.precipitation ?? 0} mm</div>
          </div>
        </div>
      </div>
    {/if}

    {#if airQuality?.current}
      <div class="space-y-2">
        <h4 class="text-xs font-semibold text-muted-foreground uppercase">Air Quality</h4>
        <div class="glass-panel rounded-lg p-3">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium">US AQI</span>
            <span class="font-mono font-bold {aqiColor(airQuality.current.us_aqi)}">
              {airQuality.current.us_aqi} — {aqiLabel(airQuality.current.us_aqi)}
            </span>
          </div>
          <div class="grid grid-cols-3 gap-2 text-[10px]">
            <div><span class="text-muted-foreground">PM2.5:</span> {airQuality.current.pm2_5} μg/m³</div>
            <div><span class="text-muted-foreground">PM10:</span> {airQuality.current.pm10} μg/m³</div>
            <div><span class="text-muted-foreground">O₃:</span> {airQuality.current.ozone} μg/m³</div>
          </div>
        </div>
      </div>
    {/if}

    {#if weather?.daily?.sunrise?.[0]}
      <div class="space-y-2">
        <h4 class="text-xs font-semibold text-muted-foreground uppercase">Sun Schedule</h4>
        <div class="glass-panel rounded-lg p-2 flex items-center gap-4">
          <div class="text-[10px]">
            <span class="text-muted-foreground">☀️ Sunrise:</span>
            <span class="font-mono">{new Date(weather.daily.sunrise[0]).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
          <div class="text-[10px]">
            <span class="text-muted-foreground">🌙 Sunset:</span>
            <span class="font-mono">{new Date(weather.daily.sunset![0]).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        </div>
      </div>
    {/if}
  </div>
{/if}