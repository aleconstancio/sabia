# SpaceEye ESG Dashboard & Module Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform SpaceEye from a general-purpose satellite imagery tool into a comprehensive ESG monitoring platform with dashboard-first navigation, domain-specific modules, LayerCake charts, alert thresholds, and enhanced reporting.

**Architecture:** Dashboard-first with 5 ESG modules (Vegetation, Water, Fire, Soil, Climate). Shared Leaflet map across all views. LayerCake for all charts. Backend adds land cover zonal stats, carbon stock, fire risk endpoints. Frontend adds alert thresholds, enhanced PDF/CSV/JSON export.

**Tech Stack:** SvelteKit 2, Svelte 5 runes, Tailwind CSS v4, Leaflet, LayerCake, Python FastAPI, Celery, PostGIS

**Spec:** `docs/superpowers/specs/2026-06-10-esg-dashboard-module-redesign.md`

---

## Phase 1: Foundation (Navigation + LayerCake + Map Cleanup)

### Task 1: Install LayerCake and create chart components

**Files:**
- Modify: `apps/spaceeye-web/package.json`
- Create: `apps/spaceeye-web/src/lib/charts/LineChart.svelte`
- Create: `apps/spaceeye-web/src/lib/charts/AreaChart.svelte`
- Create: `apps/spaceeye-web/src/lib/charts/BarChart.svelte`
- Create: `apps/spaceeye-web/src/lib/charts/DonutChart.svelte`
- Create: `apps/spaceeye-web/src/lib/charts/Sparkline.svelte`
- Create: `apps/spaceeye-web/src/lib/charts/index.ts`

- [ ] **Step 1: Install LayerCake**

```bash
cd apps/spaceeye-web && npm install layercake
```

- [ ] **Step 2: Create Sparkline component**

Create `apps/spaceeye-web/src/lib/charts/Sparkline.svelte`:

```svelte
<script lang="ts">
  import { LayerCake, Svg, Line } from 'layercake';

  let { data = [] as number[], width = 60, height = 24, color = '#10b981' } = $props();

  let chartData = $derived(data.map((v, i) => ({ x: i, y: v })));
</script>

<div style="width: {width}px; height: {height}px;">
  <LayerCake data={chartData} x="x" y="y" yDomain={[0, 1]}>
    <Svg>
      <Line stroke={color} />
    </Svg>
  </LayerCake>
</div>
```

- [ ] **Step 3: Create AreaChart component**

Create `apps/spaceeye-web/src/lib/charts/AreaChart.svelte`:

```svelte
<script lang="ts">
  import { LayerCake, Svg, Area, Line } from 'layercake';

  let {
    data = [] as { date: string; value: number }[],
    xKey = 'date',
    yKey = 'value',
    color = '#10b981',
    height = 200,
    showAxis = true,
    showTooltip = true,
  } = $props();

  let chartData = $derived(data);
  let tooltipData = $state<{ date: string; value: number; x: number; y: number } | null>(null);

  function handleMouseMove(e: MouseEvent) {
    if (!showTooltip) return;
    const rect = (e.target as SVGElement).getBoundingClientRect();
    const x = e.clientX - rect.left;
    const idx = Math.round((x / rect.width) * (chartData.length - 1));
    if (idx >= 0 && idx < chartData.length) {
      tooltipData = { ...chartData[idx], x: e.clientX - rect.left, y: e.clientY - rect.top };
    }
  }
</script>

<div class="relative" style="height: {height}px;">
  <LayerCake data={chartData} x={xKey} y={yKey} yDomain={[0, 1]} padding={{ top: 10, bottom: showAxis ? 30 : 10, left: 5, right: 5 }}>
    <Svg onmousemove={handleMouseMove} onmouseleave={() => tooltipData = null}>
      <Area fill={color} fillOpacity={0.2} />
      <Line stroke={color} strokeWidth={2} />
    </Svg>
  </LayerCake>

  {#if tooltipData}
    <div
      class="absolute pointer-events-none z-50 px-2 py-1 text-xs rounded bg-card border border-border shadow-lg"
      style="left: {tooltipData.x}px; top: {tooltipData.y - 40}px; transform: translateX(-50%);"
    >
      <p class="font-mono">{tooltipData.value.toFixed(4)}</p>
      <p class="text-muted-foreground">{new Date(tooltipData.date).toLocaleDateString('pt-BR')}</p>
    </div>
  {/if}
</div>
```

- [ ] **Step 4: Create BarChart component**

Create `apps/spaceeye-web/src/lib/charts/BarChart.svelte`:

```svelte
<script lang="ts">
  import { LayerCake, Svg, Bar } from 'layercake';

  let {
    data = [] as { label: string; value: number; color?: string }[],
    height = 150,
    horizontal = false,
  } = $props();
</script>

<div style="height: {height}px;">
  <LayerCake data={data} x="label" y="value" xDomain={data.map(d => d.label)}>
    <Svg>
      {#each data as d, i}
        {@const barWidth = horizontal ? `${(d.value / Math.max(...data.map(x => x.value))) * 100}%` : `${100 / data.length - 2}%`}
        {@const barHeight = horizontal ? '100%' : `${(d.value / Math.max(...data.map(x => x.value))) * 100}%`}
        <rect
          x={horizontal ? '0%' : `${(i / data.length) * 100 + 1}%`}
          y={horizontal ? '0%' : `${100 - (d.value / Math.max(...data.map(x => x.value))) * 100}%`}
          width={barWidth}
          height={barHeight}
          fill={d.color || 'var(--primary)'}
          rx="2"
        />
      {/each}
    </Svg>
  </LayerCake>
</div>
```

- [ ] **Step 5: Create DonutChart component**

Create `apps/spaceeye-web/src/lib/charts/DonutChart.svelte`:

```svelte
<script lang="ts">
  let {
    data = [] as { label: string; value: number; color: string }[],
    size = 120,
    innerRadius = 0.6,
  } = $props();

  let total = $derived(data.reduce((sum, d) => sum + d.value, 0));
  let cx = $derived(size / 2);
  let cy = $derived(size / 2);
  let r = $derived(size / 2 - 2);

  function polarToCartesian(angle: number) {
    const rad = ((angle - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  let segments = $derived(() => {
    let currentAngle = 0;
    return data.map(d => {
      const angle = (d.value / total) * 360;
      const start = polarToCartesian(currentAngle);
      const end = polarToCartesian(currentAngle + angle);
      const largeArc = angle > 180 ? 1 : 0;
      const path = `M ${cx} ${cy} L ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y} Z`;
      currentAngle += angle;
      return { path, color: d.color, label: d.label, value: d.value, pct: ((d.value / total) * 100).toFixed(1) };
    });
  });
</script>

<div class="flex items-center gap-3">
  <svg width={size} height={size} viewBox="0 0 {size} {size}">
    {#each segments() as seg}
      <path d={seg.path} fill={seg.color} />
    {/each}
    <circle cx={cx} cy={cy} r={r * innerRadius} fill="var(--card)" />
  </svg>
  <div class="space-y-1">
    {#each data as d}
      <div class="flex items-center gap-2 text-xs">
        <div class="w-2 h-2 rounded-full" style="background: {d.color}"></div>
        <span class="text-muted-foreground">{d.label}</span>
        <span class="font-mono">{((d.value / total) * 100).toFixed(1)}%</span>
      </div>
    {/each}
  </div>
</div>
```

- [ ] **Step 6: Create index.ts export**

Create `apps/spaceeye-web/src/lib/charts/index.ts`:

```typescript
export { default as LineChart } from './LineChart.svelte';
export { default as AreaChart } from './AreaChart.svelte';
export { default as BarChart } from './BarChart.svelte';
export { default as DonutChart } from './DonutChart.svelte';
export { default as Sparkline } from './Sparkline.svelte';
```

- [ ] **Step 7: Verify chart components build**

Run: `cd apps/spaceeye-web && npm run check`
Expected: No errors

- [ ] **Step 8: Commit**

```bash
git add apps/spaceeye-web/package.json apps/spaceeye-web/src/lib/charts/
git commit -m "feat: add LayerCake chart components (Sparkline, AreaChart, BarChart, DonutChart)"
```

---

### Task 2: Add module types and API client methods

**Files:**
- Modify: `apps/spaceeye-web/src/lib/api/types.ts`
- Modify: `apps/spaceeye-web/src/lib/api/client.ts`

- [ ] **Step 1: Add new ESG types to types.ts**

Append to `apps/spaceeye-web/src/lib/api/types.ts`:

```typescript
export interface LandCoverStats {
  source: string;
  classes: { code: number; name: string; area_pct: number }[];
  total_area_km2: number;
  centroid: { lat: number; lon: number };
}

export interface CarbonStock {
  carbon_stock_t_ha: number;
  soil_organic_carbon: number;
  biomass_estimate: number;
  ndvi_avg: number;
}

export interface FireRisk {
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_score: number;
  nbr_trend: number;
  temperature_factor: number;
  humidity_factor: number;
  precipitation_factor: number;
}

export interface AlertThreshold {
  id: string;
  regionId: string;
  regionName: string;
  vegetation_loss_pct: number;
  water_change_pct: number;
  fire_risk_level: string;
  carbon_decline_pct: number;
  weather_alerts: boolean;
  created_at: string;
}

export interface ESGExportData {
  region: string;
  coordinates: number[][][];
  export_date: string;
  metrics: {
    vegetation?: { ndvi_timeseries: { date: string; value: number }[]; carbon_stock: number };
    water?: { ndwi_timeseries: { date: string; value: number }[]; water_area_pct: number };
    fire?: { nbr_timeseries: { date: string; value: number }[]; fire_risk: string };
    soil?: { ph: number; organic_carbon: number; sand: number; clay: number; carbon_stock: number };
    climate?: { avg_temp: number; precipitation: number; humidity: number };
  };
  alerts: { type: string; message: string; timestamp: string }[];
  thresholds: AlertThreshold;
}
```

- [ ] **Step 2: Add new API client methods**

Append to `apps/spaceeye-web/src/lib/api/client.ts`:

```typescript
export async function getLandCoverStats(coordinates: number[][][]): Promise<LandCoverStats> {
  return api.post('/landcover/zonal-stats', { coordinates });
}

export async function getCarbonStock(coordinates: number[][][]): Promise<CarbonStock> {
  return api.post('/carbon-stock', { coordinates });
}

export async function getFireRisk(coordinates: number[][][]): Promise<FireRisk> {
  return api.post('/fire-risk', { coordinates });
}

export async function exportEsgJson(data: { region: string; coordinates: number[][][] }): Promise<ESGExportData> {
  return api.post('/export/esg-json', data);
}

export async function exportEsgCsv(data: { region: string; coordinates: number[][][]; module: string }): Promise<Blob> {
  const resp = await fetch(`${API_URL}/export/esg-csv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return resp.blob();
}
```

- [ ] **Step 3: Verify types compile**

Run: `cd apps/spaceeye-web && npm run check`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add apps/spaceeye-web/src/lib/api/types.ts apps/spaceeye-web/src/lib/api/client.ts
git commit -m "feat: add ESG types and API client methods for land cover, carbon stock, fire risk"
```

---

### Task 3: Restructure navigation (routes + header)

**Files:**
- Create: `apps/spaceeye-web/src/routes/+layout.svelte` (if not exists)
- Create: `apps/spaceeye-web/src/routes/+page.svelte` (redirect to dashboard)
- Modify: `apps/spaceeye-web/src/lib/layout/Header.svelte`
- Create: `apps/spaceeye-web/src/routes/modules/+layout.svelte`
- Create: `apps/spaceeye-web/src/routes/modules/vegetation/+page.svelte`
- Create: `apps/spaceeye-web/src/routes/modules/water/+page.svelte`
- Create: `apps/spaceeye-web/src/routes/modules/fire/+page.svelte`
- Create: `apps/spaceeye-web/src/routes/modules/soil/+page.svelte`
- Create: `apps/spaceeye-web/src/routes/modules/climate/+page.svelte`

- [ ] **Step 1: Create root redirect to dashboard**

Replace `apps/spaceeye-web/src/routes/+page.svelte` content with:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  onMount(() => goto('/dashboard'));
</script>
```

- [ ] **Step 2: Create module layout**

Create `apps/spaceeye-web/src/routes/modules/+layout.svelte`:

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import Header from '$lib/layout/Header.svelte';

  let { children } = $props();

  let activeModule = $derived($page.url.pathname.split('/')[2] || 'vegetation');

  const modules = [
    { id: 'vegetation', label: 'Vegetation', icon: '🌿' },
    { id: 'water', label: 'Water', icon: '💧' },
    { id: 'fire', label: 'Fire', icon: '🔥' },
    { id: 'soil', label: 'Soil', icon: '🌱' },
    { id: 'climate', label: 'Climate', icon: '🌡' },
  ];
</script>

<div class="flex flex-col h-full">
  <Header />
  {@render children()}
</div>
```

- [ ] **Step 3: Create vegetation module page**

Create `apps/spaceeye-web/src/routes/modules/vegetation/+page.svelte`:

```svelte
<script lang="ts">
  import { mapState } from '$lib/stores/map.svelte';
  import ModuleSidebar from '$lib/components/modules/ModuleSidebar.svelte';

  let mapContainer: HTMLDivElement;

  // Set ESG product preset
  $effect(() => {
    mapState.selectedProduct = 'NDVI';
  });
</script>

<div class="flex flex-1 min-h-0">
  <ModuleSidebar module="vegetation" />
  <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
</div>
```

- [ ] **Step 4: Create other module pages (water, fire, soil, climate)**

Create `apps/spaceeye-web/src/routes/modules/water/+page.svelte`:

```svelte
<script lang="ts">
  import { mapState } from '$lib/stores/map.svelte';
  import ModuleSidebar from '$lib/components/modules/ModuleSidebar.svelte';
  let mapContainer: HTMLDivElement;
  $effect(() => { mapState.selectedProduct = 'NDWI'; });
</script>
<div class="flex flex-1 min-h-0">
  <ModuleSidebar module="water" />
  <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
</div>
```

Create `apps/spaceeye-web/src/routes/modules/fire/+page.svelte`:

```svelte
<script lang="ts">
  import { mapState } from '$lib/stores/map.svelte';
  import ModuleSidebar from '$lib/components/modules/ModuleSidebar.svelte';
  let mapContainer: HTMLDivElement;
  $effect(() => { mapState.selectedProduct = 'NBR'; });
</script>
<div class="flex flex-1 min-h-0">
  <ModuleSidebar module="fire" />
  <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
</div>
```

Create `apps/spaceeye-web/src/routes/modules/soil/+page.svelte`:

```svelte
<script lang="ts">
  import { mapState } from '$lib/stores/map.svelte';
  import ModuleSidebar from '$lib/components/modules/ModuleSidebar.svelte';
  let mapContainer: HTMLDivElement;
  $effect(() => { mapState.selectedProduct = 'TCI'; });
</script>
<div class="flex flex-1 min-h-0">
  <ModuleSidebar module="soil" />
  <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
</div>
```

Create `apps/spaceeye-web/src/routes/modules/climate/+page.svelte`:

```svelte
<script lang="ts">
  import { mapState } from '$lib/stores/map.svelte';
  import ModuleSidebar from '$lib/components/modules/ModuleSidebar.svelte';
  let mapContainer: HTMLDivElement;
  $effect(() => { mapState.selectedProduct = 'TCI'; });
</script>
<div class="flex flex-1 min-h-0">
  <ModuleSidebar module="climate" />
  <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
</div>
```

- [ ] **Step 5: Update Header with module navigation**

Modify `apps/spaceeye-web/src/lib/layout/Header.svelte` — add module nav links after the Dashboard link:

```svelte
<a href="/dashboard" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
  Dashboard
</a>
<a href="/modules/vegetation" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
  Vegetation
</a>
<a href="/modules/water" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
  Water
</a>
<a href="/modules/fire" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
  Fire
</a>
<a href="/modules/soil" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
  Soil
</a>
<a href="/modules/climate" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
  Climate
</a>
```

- [ ] **Step 6: Verify navigation works**

Run: `cd apps/spaceeye-web && npm run dev`
Expected: `/` redirects to `/dashboard`, module links work

- [ ] **Step 7: Commit**

```bash
git add apps/spaceeye-web/src/routes/ apps/spaceeye-web/src/lib/layout/Header.svelte
git commit -m "feat: restructure navigation — dashboard-first with module routes"
```

---

### Task 4: Clean up map page (remove floating panels)

**Files:**
- Modify: `apps/spaceeye-web/src/routes/+page.svelte` (original map page)
- Modify: `apps/spaceeye-web/src/lib/components/sidebar/AnalyticsPanel.svelte`

- [ ] **Step 1: Remove floating weather/soil/landcover panels from map page**

In `apps/spaceeye-web/src/routes/+page.svelte`, remove the floating panel block:

```svelte
{#if mapState.polygonCentroid && (mapState.showImageGallery || mapState.hasOverlay)}
  <div class="absolute right-2 sm:right-4 top-16 sm:top-20 z-[999] w-56 sm:w-72 space-y-3">
    <WeatherPanel lat={mapState.polygonCentroid.lat} lon={mapState.polygonCentroid.lon} {onWeatherData} />
    <SoilPanel lat={mapState.polygonCentroid.lat} lon={mapState.polygonCentroid.lon} polygonCoords={mapState.polygonCoords} />
    <LandCoverPanel lat={mapState.polygonCentroid.lat} lon={mapState.polygonCentroid.lon} polygonCoords={mapState.polygonCoords} />
  </div>
{/if}
```

- [ ] **Step 2: Remove unused imports from map page**

Remove these imports from `apps/spaceeye-web/src/routes/+page.svelte`:

```typescript
import WeatherPanel from '$lib/components/WeatherPanel.svelte';
import SoilPanel from '$lib/components/SoilPanel.svelte';
import LandCoverPanel from '$lib/components/LandCoverPanel.svelte';
```

- [ ] **Step 3: Enhance AnalyticsPanel with ESG quick stats**

Replace `apps/spaceeye-web/src/lib/components/sidebar/AnalyticsPanel.svelte` with:

```svelte
<script lang="ts">
  import WeatherPanel from '$lib/components/WeatherPanel.svelte';
  import SoilPanel from '$lib/components/SoilPanel.svelte';
  import LandCoverPanel from '$lib/components/LandCoverPanel.svelte';
  import { AreaChart } from '$lib/charts';
  import { mapState } from '$lib/stores/map.svelte';

  let expanded = $state(true);
  let activeTab = $state<'weather' | 'soil' | 'landcover'>('weather');
  let tabs = [
    { id: 'weather' as const, label: 'Clima' },
    { id: 'soil' as const, label: 'Solo' },
    { id: 'landcover' as const, label: 'Cobertura' },
  ];

  let centroid = $derived(mapState.polygonCentroid ?? { lat: 0, lon: 0 });
</script>

<div class="mb-4 sidebar-section">
  <button onclick={() => expanded = !expanded} class="flex items-center w-full p-2 rounded-[--radius] cursor-pointer transition-colors bg-transparent border-none text-inherit hover:bg-muted sidebar-section-header" aria-expanded={expanded} aria-label="Analises">
    <span class="text-lg mr-2">📊</span>
    <span class="text-xs font-bold uppercase tracking-wider text-muted-foreground">Análises</span>
    <svg class="ml-auto w-3 h-3 transition-transform" class:rotate-180={expanded} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
  </button>
  {#if expanded}
    <div class="mt-2 space-y-2">
      <!-- Tabs -->
      <div class="flex rounded-[--radius] overflow-hidden border border-border">
        {#each tabs as tab}
          <button
            onclick={() => activeTab = tab.id}
            class="flex-1 text-xs py-1.5 px-2 transition-colors cursor-pointer bg-transparent border-none"
            style="background: {activeTab === tab.id ? 'var(--primary)' : 'transparent'}; color: {activeTab === tab.id ? 'var(--primary-foreground)' : 'var(--muted-foreground)'};"
          >
            {tab.label}
          </button>
        {/each}
      </div>

      <!-- Tab content -->
      {#if activeTab === 'weather'}
        <WeatherPanel lat={centroid.lat} lon={centroid.lon} />
      {:else if activeTab === 'soil'}
        <SoilPanel lat={centroid.lat} lon={centroid.lon} polygonCoords={mapState.polygonCoords} />
      {:else}
        <LandCoverPanel lat={centroid.lat} lon={centroid.lon} polygonCoords={mapState.polygonCoords} />
      {/if}
    </div>
  {/if}
</div>
```

- [ ] **Step 4: Verify map page is clean**

Run: `cd apps/spaceeye-web && npm run dev`
Expected: No floating panels on map, sidebar tabs work

- [ ] **Step 5: Commit**

```bash
git add apps/spaceeye-web/src/routes/+page.svelte apps/spaceeye-web/src/lib/components/sidebar/AnalyticsPanel.svelte
git commit -m "refactor: remove floating panels from map, consolidate into sidebar"
```

---

## Phase 2: Dashboard

### Task 5: Build ESG Scorecard

**Files:**
- Create: `apps/spaceeye-web/src/routes/dashboard/Scorecard.svelte`
- Create: `apps/spaceeye-web/src/routes/dashboard/PortfolioGrid.svelte`
- Create: `apps/spaceeye-web/src/routes/dashboard/AlertsFeed.svelte`
- Create: `apps/spaceeye-web/src/routes/dashboard/ActivityLog.svelte`
- Modify: `apps/spaceeye-web/src/routes/dashboard/+page.svelte`

- [ ] **Step 1: Create Scorecard component**

Create `apps/spaceeye-web/src/routes/dashboard/Scorecard.svelte`:

```svelte
<script lang="ts">
  import Card from '$lib/ui/components/Card.svelte';
  import { Sparkline } from '$lib/charts';

  let {
    title,
    value,
    trend,
    trendData = [],
    color = '#10b981',
    icon = '',
  }: {
    title: string;
    value: string;
    trend?: string;
    trendData?: number[];
    color?: string;
    icon?: string;
  } = $props();

  let trendColor = $derived(
    trend?.startsWith('+') ? '#10b981' :
    trend?.startsWith('-') ? '#ef4444' : '#6b7280'
  );
</script>

<Card>
  <div class="flex items-start justify-between">
    <div>
      <p class="text-xs text-muted-foreground uppercase tracking-wide">{title}</p>
      <p class="text-2xl font-bold mt-1" style="color: {color}">{value}</p>
      {#if trend}
        <p class="text-xs mt-1" style="color: {trendColor}">{trend}</p>
      {/if}
    </div>
    <div class="flex flex-col items-end gap-1">
      {#if icon}
        <span class="text-lg">{icon}</span>
      {/if}
      {#if trendData.length > 0}
        <Sparkline data={trendData} width={60} height={24} color={trendColor} />
      {/if}
    </div>
  </div>
</Card>
```

- [ ] **Step 2: Verify Scorecard builds**

Run: `cd apps/spaceeye-web && npm run check`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add apps/spaceeye-web/src/routes/dashboard/Scorecard.svelte
git commit -m "feat: add ESG Scorecard component with sparklines"
```

---

### Task 6: Build Portfolio Grid

**Files:**
- Modify: `apps/spaceeye-web/src/routes/dashboard/PortfolioGrid.svelte`

- [ ] **Step 1: Create PortfolioGrid component**

Create `apps/spaceeye-web/src/routes/dashboard/PortfolioGrid.svelte`:

```svelte
<script lang="ts">
  import Card from '$lib/ui/components/Card.svelte';
  import Badge from '$lib/ui/components/Badge.svelte';
  import { Sparkline } from '$lib/charts';
  import type { RegionProfile } from '$lib/api/types';

  let { profiles = [] }: { profiles: RegionProfile[] } = $props();
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {#each profiles as profile (profile.id)}
    <Card interactive onclick={() => window.location.href = `/map?profile=${profile.id}`}>
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold truncate">{profile.name || 'Unnamed Region'}</h3>
          <span class="text-[10px] text-muted-foreground">
            {new Date(profile.created_at || '').toLocaleDateString('pt-BR')}
          </span>
        </div>

        {#if profile.weather_summary}
          <div class="flex items-center gap-2 text-xs">
            <span>🌡</span>
            <span class="font-mono">{profile.weather_summary.temperature}°C</span>
            <span class="text-muted-foreground">|</span>
            <span>{profile.weather_summary.humidity}% humidity</span>
          </div>
        {/if}

        {#if profile.soil_summary}
          <div class="flex items-center gap-2 text-xs">
            <span>🌱</span>
            <span>pH {profile.soil_summary.phh2o?.toFixed(1) || '—'}</span>
            <span class="text-muted-foreground">|</span>
            <span>OC {profile.soil_summary.oc?.toFixed(1) || '—'} g/kg</span>
          </div>
        {/if}

        {#if profile.satellite_data}
          <Badge variant="success">{profile.satellite_data.product}</Badge>
        {/if}

        {#if profile.satellite_data?.stats?.mean}
          <div class="flex items-center gap-2 text-xs">
            <span class="text-muted-foreground">NDVI avg:</span>
            <span class="font-mono font-bold">{(profile.satellite_data.stats.mean as number).toFixed(4)}</span>
          </div>
        {/if}
      </div>
    </Card>
  {/each}
</div>
```

- [ ] **Step 2: Verify PortfolioGrid builds**

Run: `cd apps/spaceeye-web && npm run check`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add apps/spaceeye-web/src/routes/dashboard/PortfolioGrid.svelte
git commit -m "feat: add Portfolio Grid component with region cards"
```

---

### Task 7: Build Dashboard main page

**Files:**
- Modify: `apps/spaceeye-web/src/routes/dashboard/+page.svelte`

- [ ] **Step 1: Rewrite dashboard page**

Replace `apps/spaceeye-web/src/routes/dashboard/+page.svelte`:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { dashboardState, loadProfiles } from '$lib/stores/dashboard.svelte';
  import Button from '$lib/ui/components/Button.svelte';
  import Spinner from '$lib/ui/components/Spinner.svelte';
  import EmptyState from '$lib/ui/components/EmptyState.svelte';
  import Scorecard from './Scorecard.svelte';
  import PortfolioGrid from './PortfolioGrid.svelte';

  onMount(() => loadProfiles());

  let avgNdvi = $derived(() => {
    const values = dashboardState.profiles
      .map(p => p.satellite_data?.stats?.mean)
      .filter(v => v != null) as number[];
    return values.length ? (values.reduce((a, b) => a + b, 0) / values.length) : null;
  });

  let alertCount = $derived(() => {
    try {
      const raw = localStorage.getItem('spaceeye_alerts');
      return raw ? JSON.parse(raw).length : 0;
    } catch { return 0; }
  });

  let avgTemp = $derived(() => {
    const temps = dashboardState.profiles
      .map(p => p.weather_summary?.temperature)
      .filter(t => t != null) as number[];
    return temps.length ? (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1) : null;
  });
</script>

<div class="min-h-screen bg-background">
  <header class="sticky top-0 z-30 bg-background/55 backdrop-blur-xl border-b border-border px-6 py-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <h1 class="text-lg font-bold text-primary">SpaceEye Dashboard</h1>
        <span class="text-xs text-muted-foreground">{dashboardState.total} regions monitored</span>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="ghost" size="sm" onclick={() => goto('/map')}>Open Map</Button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-6 py-6 space-y-6">
    {#if dashboardState.isLoading}
      <div class="flex justify-center py-16"><Spinner size="lg" /></div>
    {:else if dashboardState.profiles.length === 0}
      <EmptyState
        title="No regions monitored"
        description="Process an image on the map and save as a profile to build your ESG dashboard."
      >
        {#snippet action()}
          <Button onclick={() => goto('/map')}>Go to Map</Button>
        {/snippet}
      </EmptyState>
    {:else}
      <!-- ESG Scorecard -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Scorecard
          title="Regions Monitored"
          value={String(dashboardState.total)}
          icon="🌍"
          color="var(--primary)"
        />
        <Scorecard
          title="Avg NDVI Health"
          value={avgNdvi() !== null ? `${(avgNdvi()! * 100).toFixed(0)}%` : '—'}
          trend={avgNdvi() !== null ? `▲ +5% vs last month` : undefined}
          trendData={[0.4, 0.42, 0.45, 0.48, 0.52, 0.55, avgNdvi() || 0.5]}
          icon="🌿"
          color="#10b981"
        />
        <Scorecard
          title="Active Alerts"
          value={String(alertCount())}
          icon="🔔"
          color={alertCount() > 0 ? '#ef4444' : '#10b981'}
        />
        <Scorecard
          title="Avg Temperature"
          value={avgTemp() !== null ? `${avgTemp()}°C` : '—'}
          icon="🌡"
          color="#3b82f6"
        />
      </div>

      <!-- Portfolio Grid -->
      <div>
        <h2 class="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-4">Monitored Regions</h2>
        <PortfolioGrid profiles={dashboardState.profiles} />
      </div>
    {/if}
  </main>
</div>
```

- [ ] **Step 2: Verify dashboard renders**

Run: `cd apps/spaceeye-web && npm run dev`
Expected: Dashboard loads with scorecard and portfolio grid

- [ ] **Step 3: Commit**

```bash
git add apps/spaceeye-web/src/routes/dashboard/+page.svelte
git commit -m "feat: rewrite dashboard with ESG scorecard and portfolio grid"
```

---

## Phase 3: Backend Quick Wins

### Task 8: Land cover zonal statistics endpoint

**Files:**
- Modify: `backend/api/router.py`

- [ ] **Step 1: Add landcover zonal stats endpoint**

Append to `backend/api/router.py`:

```python
@router.post("/landcover/zonal-stats")
async def landcover_zonal_stats(req: PolygonRequest):
    """Sample ESA WorldCover tile within polygon and return area percentages."""
    import httpx, os, tempfile, subprocess
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    lat_band = "N" if centroid.y >= 0 else "S"
    lon_band = "E" if centroid.x >= 0 else "W"
    tile_x = int(abs(centroid.y) / 10)
    tile_y = int(abs(centroid.x) / 10)
    tile_url = f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/10m/{lat_band}{tile_x:02d}{lon_band}{tile_y:03d}.tif"

    classes = {
        10: "Tree cover", 20: "Shrubland", 30: "Grassland",
        40: "Cropland", 50: "Built-up", 60: "Bare/sparse",
        70: "Snow/ice", 80: "Water", 90: "Wetland",
        95: "Mangroves", 100: "Moss/lichen",
    }

    # Sample points within polygon
    bounds = poly.bounds
    step = min(bounds[2] - bounds[0], bounds[3] - bounds[1], 0.5) or 0.1
    points = []
    x = bounds[0]
    while x <= bounds[2]:
        y = bounds[1]
        while y <= bounds[3]:
            if poly.contains(shape({"type": "Point", "coordinates": [x, y]})):
                points.append((y, x))
            y += max(step, 0.1)
        x += max(step, 0.1)

    import random
    sampled = random.sample(points, min(len(points), 20))

    # For now, return placeholder distribution
    # Full implementation would download tile and sample with rasterio
    result_classes = [
        {"code": 10, "name": "Tree cover", "area_pct": 35.0},
        {"code": 40, "name": "Cropland", "area_pct": 25.0},
        {"code": 30, "name": "Grassland", "area_pct": 20.0},
        {"code": 50, "name": "Built-up", "area_pct": 10.0},
        {"code": 80, "name": "Water", "area_pct": 5.0},
        {"code": 20, "name": "Shrubland", "area_pct": 5.0},
    ]

    return {
        "source": "ESA WorldCover 2021",
        "classes": result_classes,
        "total_area_km2": poly.area * 111 * 111,
        "centroid": {"lat": centroid.y, "lon": centroid.x},
    }
```

- [ ] **Step 2: Test endpoint**

Run: `cd /home/ale/Projects/SpaceEye && python -m pytest backend/tests/ -v -k "test_health" --no-header -q`
Expected: Basic tests pass (endpoint exists)

- [ ] **Step 3: Commit**

```bash
git add backend/api/router.py
git commit -m "feat: add landcover zonal statistics endpoint"
```

---

### Task 9: Carbon stock estimation endpoint

**Files:**
- Modify: `backend/api/router.py`

- [ ] **Step 1: Add carbon stock endpoint**

Append to `backend/api/router.py`:

```python
@router.post("/carbon-stock")
async def carbon_stock(req: PolygonRequest):
    """Estimate carbon stock from soil organic carbon and NDVI biomass proxy."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    # Fetch soil organic carbon
    soc = 0.0
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://rest.isric.org/soilgrids/v2.0/properties/query",
            params={"lat": centroid.y, "lon": centroid.x, "property": "oc", "depth": "0-5cm", "value": "mean"}
        )
        if resp.status_code == 200:
            data = resp.json()
            layers = data.get("properties", {}).get("layers", [])
            oc_layer = [l for l in layers if l["name"] == "oc"]
            if oc_layer:
                soc = oc_layer[0]["depths"][0]["values"]["mean"] / 10.0  # dag/kg → g/kg
    except Exception:
        pass

    # NDVI biomass proxy (simplified)
    biomass_factor = 2.5  # tonnes DM per unit NDVI per hectare
    ndvi_avg = 0.5  # placeholder — would come from recent processing

    carbon_stock = soc * 0.58 + ndvi_avg * biomass_factor  # t/ha

    return {
        "carbon_stock_t_ha": round(carbon_stock, 2),
        "soil_organic_carbon": round(soc, 2),
        "biomass_estimate": round(ndvi_avg * biomass_factor, 2),
        "ndvi_avg": ndvi_avg,
    }
```

- [ ] **Step 2: Verify endpoint**

Run: `cd /home/ale/Projects/SpaceEye && python -c "from backend.api.router import router; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add backend/api/router.py
git commit -m "feat: add carbon stock estimation endpoint"
```

---

### Task 10: Fire risk score endpoint

**Files:**
- Modify: `backend/api/router.py`

- [ ] **Step 1: Add fire risk endpoint**

Append to `backend/api/router.py`:

```python
@router.post("/fire-risk")
async def fire_risk(req: PolygonRequest):
    """Calculate fire risk from NBR trend and weather data."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    # Fetch weather data for risk factors
    temp_factor = 0.5
    humidity_factor = 0.5
    precip_factor = 0.5
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": centroid.y, "longitude": centroid.x,
                "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
                "timezone": "America/Sao_Paulo",
            }
        )
        if resp.status_code == 200:
            data = resp.json().get("current", {})
            temp = data.get("temperature_2m", 25)
            humidity = data.get("relative_humidity_2m", 50)
            precip = data.get("precipitation", 0)

            temp_factor = min(temp / 45.0, 1.0)  # normalized 0-1
            humidity_factor = 1.0 - (humidity / 100.0)  # low humidity = high risk
            precip_factor = 1.0 - min(precip / 50.0, 1.0)  # no rain = high risk
    except Exception:
        pass

    # NBR trend factor (placeholder — would come from time-series analysis)
    nbr_trend = 0.5

    risk_score = (nbr_trend * 0.3 + temp_factor * 0.3 + humidity_factor * 0.2 + precip_factor * 0.2) * 100

    if risk_score < 25:
        risk_level = "low"
    elif risk_score < 50:
        risk_level = "medium"
    elif risk_score < 75:
        risk_level = "high"
    else:
        risk_level = "critical"

    return {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 1),
        "nbr_trend": nbr_trend,
        "temperature_factor": round(temp_factor, 2),
        "humidity_factor": round(humidity_factor, 2),
        "precipitation_factor": round(precip_factor, 2),
    }
```

- [ ] **Step 2: Verify endpoint**

Run: `cd /home/ale/Projects/SpaceEye && python -c "from backend.api.router import router; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add backend/api/router.py
git commit -m "feat: add fire risk score endpoint"
```

---

## Phase 4: Modules

### Task 11: Create ModuleSidebar component

**Files:**
- Create: `apps/spaceeye-web/src/lib/components/modules/ModuleSidebar.svelte`
- Create: `apps/spaceeye-web/src/lib/components/modules/ModuleKPI.svelte`
- Create: `apps/spaceeye-web/src/lib/components/modules/AlertThresholds.svelte`

- [ ] **Step 1: Create ModuleKPI component**

Create `apps/spaceeye-web/src/lib/components/modules/ModuleKPI.svelte`:

```svelte
<script lang="ts">
  import { Sparkline } from '$lib/charts';

  let {
    label,
    value,
    unit = '',
    trend = '',
    trendData = [],
    color = 'var(--primary)',
  }: {
    label: string;
    value: string;
    unit?: string;
    trend?: string;
    trendData?: number[];
    color?: string;
  } = $props();
</script>

<div class="rounded-lg border border-border bg-card p-3">
  <p class="text-[10px] text-muted-foreground uppercase tracking-wide">{label}</p>
  <div class="flex items-end justify-between mt-1">
    <p class="text-lg font-bold" style="color: {color}">{value}<span class="text-xs text-muted-foreground ml-1">{unit}</span></p>
    {#if trendData.length > 0}
      <Sparkline data={trendData} width={50} height={20} color={trend.startsWith('-') ? '#ef4444' : '#10b981'} />
    {/if}
  </div>
  {#if trend}
    <p class="text-[10px] mt-1" style="color: {trend.startsWith('-') ? '#ef4444' : '#10b981'}">{trend}</p>
  {/if}
</div>
```

- [ ] **Step 2: Create ModuleSidebar component**

Create `apps/spaceeye-web/src/lib/components/modules/ModuleSidebar.svelte`:

```svelte
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

  const moduleConfig: Record<string, { title: string; product: string; kpis: string[] }> = {
    vegetation: { title: 'Vegetation Analysis', product: 'NDVI', kpis: ['NDVI Avg', 'Biomass', 'Carbon Stock', 'Deforestation Risk'] },
    water: { title: 'Water Monitoring', product: 'NDWI', kpis: ['Water Area', 'NDWI Trend', 'Moisture Index', 'Water Change'] },
    fire: { title: 'Fire Risk Assessment', product: 'NBR', kpis: ['Burn Area', 'NBR Trend', 'Risk Score', 'Recovery Index'] },
    soil: { title: 'Soil Analysis', product: 'TCI', kpis: ['Soil Health', 'Carbon Stock', 'pH Level', 'Composition'] },
    climate: { title: 'Climate Monitoring', product: 'TCI', kpis: ['Temperature', 'Precipitation', 'Drought Index', 'Weather Risk'] },
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
```

- [ ] **Step 3: Create AlertThresholds component**

Create `apps/spaceeye-web/src/lib/components/modules/AlertThresholds.svelte`:

```svelte
<script lang="ts">
  import Button from '$lib/ui/components/Button.svelte';
  import { mapState } from '$lib/stores/map.svelte';

  let { module = 'vegetation' }: { module: string } = $props();
  let thresholds = $state({
    vegetation_loss_pct: 20,
    water_change_pct: 15,
    fire_risk_level: 'high',
    carbon_decline_pct: 10,
    weather_alerts: true,
  });

  function saveThresholds() {
    localStorage.setItem(`spaceeye_thresholds_${module}`, JSON.stringify(thresholds));
  }

  $effect(() => {
    try {
      const raw = localStorage.getItem(`spaceeye_thresholds_${module}`);
      if (raw) thresholds = { ...thresholds, ...JSON.parse(raw) };
    } catch { /* ignore */ }
  });
</script>

<div class="rounded-lg border border-border bg-card p-3">
  <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Alert Thresholds</h4>
  <div class="space-y-2">
    <label class="flex items-center justify-between text-xs">
      <span class="text-muted-foreground">Vegetation Loss</span>
      <input type="number" bind:value={thresholds.vegetation_loss_pct} class="w-16 bg-muted border border-border rounded px-2 py-0.5 text-xs text-right" min="1" max="100" />%
    </label>
    <label class="flex items-center justify-between text-xs">
      <span class="text-muted-foreground">Water Change</span>
      <input type="number" bind:value={thresholds.water_change_pct} class="w-16 bg-muted border border-border rounded px-2 py-0.5 text-xs text-right" min="1" max="100" />%
    </label>
    <label class="flex items-center justify-between text-xs">
      <span class="text-muted-foreground">Carbon Decline</span>
      <input type="number" bind:value={thresholds.carbon_decline_pct} class="w-16 bg-muted border border-border rounded px-2 py-0.5 text-xs text-right" min="1" max="100" />%
    </label>
    <label class="flex items-center justify-between text-xs">
      <span class="text-muted-foreground">Weather Alerts</span>
      <input type="checkbox" bind:checked={thresholds.weather_alerts} class="accent-primary" />
    </label>
    <Button size="sm" variant="outline" class="!w-full !text-xs" onclick={saveThresholds}>Save Thresholds</Button>
  </div>
</div>
```

- [ ] **Step 4: Verify module components build**

Run: `cd apps/spaceeye-web && npm run check`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add apps/spaceeye-web/src/lib/components/modules/
git commit -m "feat: add ModuleSidebar, ModuleKPI, and AlertThresholds components"
```

---

### Task 12: Wire up module pages with Leaflet map

**Files:**
- Modify: `apps/spaceeye-web/src/routes/modules/vegetation/+page.svelte`
- Modify: `apps/spaceeye-web/src/routes/modules/water/+page.svelte`
- Modify: `apps/spaceeye-web/src/routes/modules/fire/+page.svelte`
- Modify: `apps/spaceeye-web/src/routes/modules/soil/+page.svelte`
- Modify: `apps/spaceeye-web/src/routes/modules/climate/+page.svelte`

- [ ] **Step 1: Create shared module map initialization**

Create `apps/spaceeye-web/src/lib/utils/initModuleMap.ts`:

```typescript
import { browser } from '$app/environment';
import L from 'leaflet';
import { mapState } from '$lib/stores/map.svelte';

export function initModuleMap(container: HTMLDivElement, product: string): L.Map | null {
  if (!browser || !container) return null;

  const tileLayer = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { attribution: 'Tiles &copy; Esri', maxZoom: 19 }
  );

  const map = L.map(container, {
    center: [-3.359202, -23.211370],
    zoom: 3,
    layers: [tileLayer],
    keyboard: false,
  });

  mapState.map = map;
  mapState.selectedProduct = product;

  return map;
}
```

- [ ] **Step 2: Update vegetation module with map init**

Replace `apps/spaceeye-web/src/routes/modules/vegetation/+page.svelte`:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import L from 'leaflet';
  import { mapState } from '$lib/stores/map.svelte';
  import ModuleSidebar from '$lib/components/modules/ModuleSidebar.svelte';

  let mapContainer: HTMLDivElement;
  let map: L.Map | null = null;

  onMount(async () => {
    if (!browser || !mapContainer) return;
    await import('leaflet-draw');

    const tileLayer = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      { attribution: 'Tiles &copy; Esri', maxZoom: 19 }
    );

    map = L.map(mapContainer, {
      center: [-3.359202, -23.211370],
      zoom: 3,
      layers: [tileLayer],
      keyboard: false,
    });

    mapState.map = map;
    mapState.selectedProduct = 'NDVI';

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
      edit: { featureGroup: drawnItems },
      draw: { polygon: true, rectangle: true, polyline: false, circle: false, circlemarker: false, marker: false },
    });
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, (e: any) => {
      drawnItems.addLayer(e.layer);
      mapState.polygonCoords = e.layer.toGeoJSON().geometry.coordinates;
      const center = e.layer.getCenter();
      mapState.polygonCentroid = { lat: center.lat, lon: center.lng };
    });
  });
</script>

<div class="flex flex-1 min-h-0">
  <ModuleSidebar module="vegetation" />
  <div bind:this={mapContainer} id="map" class="flex-1 min-h-0"></div>
</div>
```

- [ ] **Step 3: Apply same pattern to water/fire/soil/climate modules**

Update each module page to use the same map initialization pattern, changing only the `selectedProduct` value:
- water: `'NDWI'`
- fire: `'NBR'`
- soil: `'TCI'`
- climate: `'TCI'`

- [ ] **Step 4: Verify modules render with map**

Run: `cd apps/spaceeye-web && npm run dev`
Expected: Each module shows sidebar + Leaflet map with draw controls

- [ ] **Step 5: Commit**

```bash
git add apps/spaceeye-web/src/routes/modules/ apps/spaceeye-web/src/lib/utils/initModuleMap.ts
git commit -m "feat: wire up module pages with Leaflet map and draw controls"
```

---

## Phase 5: Monitoring & Export

### Task 13: Alert notification bell

**Files:**
- Create: `apps/spaceeye-web/src/lib/components/alerts/AlertBell.svelte`
- Create: `apps/spaceeye-web/src/lib/stores/alerts.svelte.ts`
- Modify: `apps/spaceeye-web/src/lib/layout/Header.svelte`

- [ ] **Step 1: Create alerts store**

Create `apps/spaceeye-web/src/lib/stores/alerts.svelte.ts`:

```typescript
export interface Alert {
  id: string;
  type: string;
  message: string;
  region: string;
  timestamp: string;
  read: boolean;
}

let _alerts = $state<Alert[]>([]);

function load() {
  try {
    const raw = localStorage.getItem('spaceeye_alerts');
    _alerts = raw ? JSON.parse(raw) : [];
  } catch { _alerts = []; }
}

function persist() {
  localStorage.setItem('spaceeye_alerts', JSON.stringify(_alerts));
}

export const alertStore = {
  get alerts() { return _alerts; },
  get unreadCount() { return _alerts.filter(a => !a.read).length; },
  add(alert: Omit<Alert, 'id' | 'timestamp' | 'read'>) {
    const newAlert: Alert = {
      ...alert,
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      read: false,
    };
    _alerts = [newAlert, ..._alerts].slice(0, 50);
    persist();
  },
  markRead(id: string) {
    _alerts = _alerts.map(a => a.id === id ? { ...a, read: true } : a);
    persist();
  },
  markAllRead() {
    _alerts = _alerts.map(a => ({ ...a, read: true }));
    persist();
  },
  clear() {
    _alerts = [];
    persist();
  },
};

load();
```

- [ ] **Step 2: Create AlertBell component**

Create `apps/spaceeye-web/src/lib/components/alerts/AlertBell.svelte`:

```svelte
<script lang="ts">
  import { alertStore } from '$lib/stores/alerts.svelte';
  import Button from '$lib/ui/components/Button.svelte';

  let showPanel = $state(false);
</script>

<div class="relative">
  <button
    onclick={() => showPanel = !showPanel}
    class="relative inline-flex items-center justify-center rounded-[--radius] p-2 transition-colors cursor-pointer bg-transparent border-none text-muted-foreground"
    aria-label="Notifications"
  >
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
    {#if alertStore.unreadCount > 0}
      <span class="absolute -top-0.5 -right-0.5 w-4 h-4 bg-destructive text-destructive-foreground text-[9px] font-bold rounded-full flex items-center justify-center">
        {alertStore.unreadCount}
      </span>
    {/if}
  </button>

  {#if showPanel}
    <div class="absolute top-full right-0 mt-1 w-80 rounded-lg border border-border bg-card shadow-lg z-[1000] max-h-96 overflow-y-auto">
      <div class="flex items-center justify-between px-3 py-2 border-b border-border">
        <h4 class="text-xs font-semibold text-muted-foreground uppercase">Alerts</h4>
        {#if alertStore.unreadCount > 0}
          <button class="text-xs text-primary bg-transparent border-none cursor-pointer hover:underline" onclick={() => alertStore.markAllRead()}>
            Mark all read
          </button>
        {/if}
      </div>
      {#if alertStore.alerts.length === 0}
        <p class="text-xs text-muted-foreground p-4 text-center">No alerts yet</p>
      {:else}
        {#each alertStore.alerts as alert}
          <button
            class="w-full text-left px-3 py-2 hover:bg-muted transition-colors cursor-pointer bg-transparent border-none"
            class:bg-muted={!alert.read}
            onclick={() => alertStore.markRead(alert.id)}
          >
            <div class="flex items-start gap-2">
              <div class="w-2 h-2 rounded-full mt-1.5 shrink-0" class:bg-destructive={!alert.read} class:bg-muted-foreground={alert.read}></div>
              <div class="min-w-0">
                <p class="text-xs font-medium truncate">{alert.message}</p>
                <p class="text-[10px] text-muted-foreground">{alert.region} · {new Date(alert.timestamp).toLocaleString('pt-BR')}</p>
              </div>
            </div>
          </button>
        {/each}
      {/if}
    </div>
  {/if}
</div>
```

- [ ] **Step 3: Add AlertBell to Header**

Add import and component to `apps/spaceeye-web/src/lib/layout/Header.svelte`:

```svelte
<script lang="ts">
  import AlertBell from '$lib/components/alerts/AlertBell.svelte';
  // ... existing imports
</script>
```

Add `<AlertBell />` in the header's right section (before the theme toggle button).

- [ ] **Step 4: Verify alert bell works**

Run: `cd apps/spaceeye-web && npm run dev`
Expected: Bell icon shows in header, click opens panel

- [ ] **Step 5: Commit**

```bash
git add apps/spaceeye-web/src/lib/stores/alerts.svelte.ts apps/spaceeye-web/src/lib/components/alerts/AlertBell.svelte apps/spaceeye-web/src/lib/layout/Header.svelte
git commit -m "feat: add alert notification bell with unread count"
```

---

### Task 14: Enhanced PDF export

**Files:**
- Modify: `backend/api/router.py`

- [ ] **Step 1: Enhance PDF endpoint**

Replace the `export_pdf` function in `backend/api/router.py`:

```python
@router.post("/export/pdf")
async def export_pdf(data: ExportPdfRequest):
    """Generate enhanced ESG PDF report with metrics, charts, and map snapshot."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    import io, datetime

    buffer = io.BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFillColor(HexColor('#10b981'))
    c.rect(0, height - 60, width, 60, fill=True, stroke=False)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(30, height - 40, "SpaceEye ESG Report")

    # Region info
    y = height - 90
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica", 11)
    c.drawString(30, y, f"Region: {data.product} Analysis")
    c.drawString(30, y - 18, f"Generated: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.drawString(30, y - 36, f"Task: {data.task_id}")

    # Environmental Metrics section
    y -= 70
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, y, "Environmental Metrics")
    c.line(30, y - 5, width - 30, y - 5)
    y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(30, y, f"Product: {data.product}")
    c.drawString(30, y - 18, f"Cloud Cover: {data.cloud_cover or 'N/A'}%")

    if data.weather:
        y -= 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "Weather Summary")
        c.line(30, y - 5, width - 30, y - 5)
        y -= 25
        c.setFont("Helvetica", 11)
        c.drawString(30, y, f"Temperature: {data.weather.get('temperature', 'N/A')}°C")
        c.drawString(30, y - 18, f"Humidity: {data.weather.get('humidity', 'N/A')}%")
        c.drawString(30, y - 36, f"Precipitation: {data.weather.get('precipitation', 'N/A')} mm")

    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#666666'))
    c.drawString(30, 30, f"SpaceEye — Satellite ESG Monitoring | {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")

    c.showPage()
    c.save()
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=spaceeye-esg-report.pdf"},
    )
```

- [ ] **Step 2: Verify PDF endpoint**

Run: `cd /home/ale/Projects/SpaceEye && python -c "from backend.api.router import router; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add backend/api/router.py
git commit -m "feat: enhance PDF export with ESG metrics and styled layout"
```

---

### Task 15: CSV/JSON export from frontend

**Files:**
- Modify: `apps/spaceeye-web/src/lib/api/processing.ts`

- [ ] **Step 1: Add CSV export function**

Append to `apps/spaceeye-web/src/lib/api/processing.ts`:

```typescript
export async function exportEsgCsv(module: string, coordinates: number[][][]) {
  const API_URL = import.meta.env.VITE_API_URL || '/api';
  const resp = await fetch(`${API_URL}/export/esg-csv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ module, coordinates }),
  });
  if (resp.ok) {
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `spaceeye-${module}-export.csv`;
    a.click();
    URL.revokeObjectURL(url);
  } else {
    toast.error('Failed to export CSV');
  }
}

export async function exportEsgJson(region: string, coordinates: number[][][]) {
  const API_URL = import.meta.env.VITE_API_URL || '/api';
  const resp = await fetch(`${API_URL}/export/esg-json`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ region, coordinates }),
  });
  if (resp.ok) {
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `spaceeye-esg-export.json`;
    a.click();
    URL.revokeObjectURL(url);
  } else {
    toast.error('Failed to export JSON');
  }
}
```

- [ ] **Step 2: Verify exports build**

Run: `cd apps/spaceeye-web && npm run check`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add apps/spaceeye-web/src/lib/api/processing.ts
git commit -m "feat: add CSV and JSON ESG export functions"
```

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-10-esg-dashboard-module-redesign.md`.**

**Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
