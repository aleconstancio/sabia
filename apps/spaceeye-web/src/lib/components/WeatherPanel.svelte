<script lang="ts">
  let {
    lat = 0,
    lon = 0,
    onWeatherData = (_data: any) => {},
  }: { lat: number; lon: number; onWeatherData?: (data: any) => void } = $props();
  let weather: any = $state(null);
  let loading = $state(false);
  let error = $state('');

  const API_URL = import.meta.env.VITE_API_URL || '/api';

  $effect(() => {
    if (lat && lon) {
      const timer = setTimeout(() => {
        fetchWeather();
      }, 300);
      return () => clearTimeout(timer);
    }
  });


  async function fetchWeather() {
    loading = true; error = '';
    try {
      const resp = await fetch(`${API_URL}/weather/${lat}/${lon}`);
      if (!resp.ok) throw new Error('Weather fetch failed');
      weather = await resp.json();
      onWeatherData(weather);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="rounded-lg border border-border bg-card p-4">
  <h3 class="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Clima</h3>
  {#if loading}
    <div class="flex items-center gap-2 text-sm text-muted-foreground">
      <span class="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      <span>Carregando...</span>
    </div>
  {:else if error}
    <p class="text-sm text-destructive">{error}</p>
  {:else if weather}
    <div class="grid grid-cols-2 gap-3">
      <div>
        <p class="text-xs text-muted-foreground">Temperatura</p>
        <p class="text-lg font-bold">{weather.current?.temperature_2m ?? '—'}°C</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Sensação</p>
        <p class="text-lg font-bold">{weather.current?.apparent_temperature ?? '—'}°C</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Umidade</p>
        <p class="text-lg font-bold">{weather.current?.relative_humidity_2m ?? '—'}%</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Precipitação</p>
        <p class="text-lg font-bold">{weather.current?.precipitation ?? '—'} mm</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Solo (7cm)</p>
        <p class="text-lg font-bold">{weather.current?.soil_moisture_0_to_7cm?.toFixed(2) ?? '—'} m³/m³</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Previsão 7d</p>
        <p class="text-lg font-bold">{weather.daily?.precipitation_sum?.[0] ?? '—'} mm</p>
      </div>
    </div>
  {/if}
</div>
