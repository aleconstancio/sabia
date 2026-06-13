<script lang="ts">
  import ModuleKPI from './ModuleKPI.svelte';
  import AlertThresholds from './AlertThresholds.svelte';
  import { AreaChart } from '$lib/charts';
  import { mapState } from '$lib/stores/map.svelte';
  import { getCarbonStock, getFireRisk, getWeather, getSoil } from '$lib/api/client';
  import type { CarbonStock, FireRisk } from '$lib/api/types';

  let { module = 'vegetation' }: { module: string } = $props();

  let expanded = $state(true);
  let carbonStock = $state<CarbonStock | null>(null);
  let fireRisk = $state<FireRisk | null>(null);
  let weatherData = $state<Record<string, unknown> | null>(null);
  let soilData = $state<Record<string, unknown> | null>(null);
  let timelineData = $state<{ date: string; value: number }[]>([]);

  function computeCentroid(coords: number[][][]): { lat: number; lon: number } | null {
    if (!coords || coords.length === 0) return null;
    let totalLat = 0, totalLon = 0, count = 0;
    for (const ring of coords) {
      for (const [lon, lat] of ring) {
        totalLat += lat;
        totalLon += lon;
        count++;
      }
    }
    return count > 0 ? { lat: totalLat / count, lon: totalLon / count } : null;
  }

  $effect(() => {
    if (!mapState.polygonCoords) return;
    const centroid = computeCentroid(mapState.polygonCoords);
    if (!centroid) return;

    if (module === 'vegetation') {
      getCarbonStock(mapState.polygonCoords).then(d => carbonStock = d).catch(() => {});
    }
    if (module === 'fire') {
      getFireRisk(mapState.polygonCoords).then(d => fireRisk = d).catch(() => {});
    }
    if (module === 'water' || module === 'climate') {
      getWeather(centroid.lat, centroid.lon).then(d => weatherData = d).catch(() => {});
    }
    if (module === 'soil') {
      getSoil(centroid.lat, centroid.lon).then(d => soilData = d).catch(() => {});
    }
  });

  $effect(() => {
    if (mapState.results.length > 0) {
      timelineData = mapState.results.slice(0, 20).map(img => ({
        date: img.acquired_at,
        value: 0.0,
      }));
    }
  });

  const moduleConfig: Record<string, { title: string; product: string }> = {
    vegetation: { title: 'Vegetation Analysis', product: 'NDVI' },
    water: { title: 'Water Monitoring', product: 'NDWI' },
    fire: { title: 'Fire Risk Assessment', product: 'NBR' },
    soil: { title: 'Soil Analysis', product: 'TCI' },
    climate: { title: 'Climate Monitoring', product: 'TCI' },
  };

  let config = $derived(moduleConfig[module] || moduleConfig.vegetation);

  function getWeatherTemp(): string {
    const current = weatherData?.current as Record<string, unknown> | undefined;
    if (!current) return '—';
    const temp = current.temperature_2m;
    return typeof temp === 'number' ? temp.toFixed(1) : '—';
  }

  function getWeatherPrecip(): string {
    const daily = weatherData?.daily as Record<string, unknown> | undefined;
    if (!daily) return '—';
    const precip = daily.precipitation_sum as number[] | undefined;
    if (!precip || !Array.isArray(precip)) return '—';
    const total = precip.reduce((a, b) => a + b, 0);
    return total.toFixed(1);
  }

  function getWeatherHumidity(): string {
    const current = weatherData?.current as Record<string, unknown> | undefined;
    if (!current) return '—';
    const humidity = current.relative_humidity_2m;
    return typeof humidity === 'number' ? humidity.toFixed(0) : '—';
  }

  function getSoilPh(): string {
    const properties = soilData?.properties as Array<{ name: string; depths: Array<{ label: string; values: Record<string, number> }> }> | undefined;
    if (!properties) return '—';
    const phProp = properties.find(p => p.name === 'phh2o');
    if (!phProp) return '—';
    const depth = phProp.depths?.[0];
    if (!depth) return '—';
    const val = depth.values?.mean;
    return typeof val === 'number' ? val.toFixed(1) : '—';
  }

  function getSoilCarbon(): string {
    const properties = soilData?.properties as Array<{ name: string; depths: Array<{ label: string; values: Record<string, number> }> }> | undefined;
    if (!properties) return '—';
    const ocProp = properties.find(p => p.name === 'oc');
    if (!ocProp) return '—';
    const depth = ocProp.depths?.[0];
    if (!depth) return '—';
    const val = depth.values?.mean;
    return typeof val === 'number' ? val.toFixed(1) : '—';
  }
</script>

<aside class="w-72 border-r border-border bg-card shrink-0 flex flex-col overflow-y-auto p-4 space-y-4">
  <div>
    <h2 class="text-sm font-bold text-foreground">{config.title}</h2>
    <p class="text-[10px] text-muted-foreground mt-1">Product: {config.product}</p>
  </div>

  <!-- KPI Cards -->
  <div class="space-y-2">
    {#if module === 'vegetation'}
      <ModuleKPI label="NDVI Avg" value={carbonStock?.ndvi_avg?.toFixed(3) || '—'} trendData={[0.4, 0.42, 0.45, 0.48, 0.52]} />
      <ModuleKPI label="Carbon Stock" value={carbonStock?.carbon_stock_t_ha?.toFixed(1) || '—'} unit="t/ha" color="#10b981" />
      <ModuleKPI label="Biomass" value={carbonStock?.biomass_estimate?.toFixed(1) || '—'} unit="t/ha" color="#3b82f6" />
    {:else if module === 'water'}
      <ModuleKPI label="Humidity" value={getWeatherHumidity()} unit="%" color="#3b82f6" />
      <ModuleKPI label="Precipitation (7d)" value={getWeatherPrecip()} unit="mm" color="#06b6d4" />
      <ModuleKPI label="Temperature" value={getWeatherTemp()} unit="°C" color="#f97316" />
    {:else if module === 'fire'}
      <ModuleKPI label="Risk Level" value={fireRisk?.risk_level || '—'} color={fireRisk?.risk_level === 'high' ? '#ef4444' : '#10b981'} />
      <ModuleKPI label="Risk Score" value={fireRisk?.risk_score?.toFixed(0) || '—'} unit="/100" />
      <ModuleKPI label="NBR Trend" value={fireRisk?.nbr_trend?.toFixed(2) || '—'} />
    {:else if module === 'soil'}
      <ModuleKPI label="pH Level" value={getSoilPh()} />
      <ModuleKPI label="Organic Carbon" value={getSoilCarbon()} unit="g/kg" />
      <ModuleKPI label="Soil Health" value={soilData ? 'Available' : '—'} color="#84cc16" />
    {:else if module === 'climate'}
      <ModuleKPI label="Temperature" value={getWeatherTemp()} unit="°C" color="#f97316" />
      <ModuleKPI label="Precipitation" value={getWeatherPrecip()} unit="mm" color="#06b6d4" />
      <ModuleKPI label="Humidity" value={getWeatherHumidity()} unit="%" color="#3b82f6" />
    {/if}
  </div>

  <!-- Domain Chart -->
  {#if timelineData.length > 0}
    <div class="rounded-lg border border-border bg-card p-3">
      <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Time Series</h4>
      <AreaChart data={timelineData} height={150} />
    </div>
  {/if}

  <!-- Alert Thresholds -->
  <AlertThresholds {module} />
</aside>
