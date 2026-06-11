<script lang="ts">
  import ModuleKPI from './ModuleKPI.svelte';
  import AlertThresholds from './AlertThresholds.svelte';
  import { AreaChart } from '$lib/charts';
  import { mapState } from '$lib/stores/map.svelte';
  import { getCarbonStock, getFireRisk } from '$lib/api/client';
  import type { CarbonStock, FireRisk } from '$lib/api/types';

  let { module = 'vegetation' }: { module: string } = $props();

  let expanded = $state(true);
  let carbonStock = $state<CarbonStock | null>(null);
  let fireRisk = $state<FireRisk | null>(null);
  let timelineData = $state<{ date: string; value: number }[]>([]);

  // Fetch data when polygon changes
  $effect(() => {
    if (mapState.polygonCoords && module === 'vegetation') {
      getCarbonStock(mapState.polygonCoords).then(d => carbonStock = d).catch(() => {});
    }
    if (mapState.polygonCoords && module === 'fire') {
      getFireRisk(mapState.polygonCoords).then(d => fireRisk = d).catch(() => {});
    }
  });

  // Build timeline from results
  $effect(() => {
    if (mapState.results.length > 0) {
      timelineData = mapState.results.slice(0, 20).map(img => ({
        date: img.acquired_at,
        value: 0.5 + Math.random() * 0.3, // placeholder — would come from batch processing
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
      <ModuleKPI label="Water Area" value="—" trendData={[0.1, 0.12, 0.11, 0.13, 0.1]} />
      <ModuleKPI label="NDWI Trend" value="—" />
      <ModuleKPI label="Moisture" value="—" />
    {:else if module === 'fire'}
      <ModuleKPI label="Risk Level" value={fireRisk?.risk_level || '—'} color={fireRisk?.risk_level === 'high' ? '#ef4444' : '#10b981'} />
      <ModuleKPI label="Risk Score" value={fireRisk?.risk_score?.toFixed(0) || '—'} unit="/100" />
      <ModuleKPI label="NBR Trend" value={fireRisk?.nbr_trend?.toFixed(2) || '—'} />
    {:else if module === 'soil'}
      <ModuleKPI label="Soil Health" value="—" />
      <ModuleKPI label="pH Level" value="—" />
      <ModuleKPI label="Organic Carbon" value="—" unit="g/kg" />
    {:else if module === 'climate'}
      <ModuleKPI label="Temperature" value="—" unit="°C" />
      <ModuleKPI label="Precipitation" value="—" unit="mm" />
      <ModuleKPI label="Drought Index" value="—" />
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
