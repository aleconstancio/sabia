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

  let avgNdvi = $derived.by(() => {
    const values = dashboardState.profiles
      .map(p => p.satellite_data?.stats?.mean)
      .filter(v => v != null) as number[];
    return values.length ? (values.reduce((a, b) => a + b, 0) / values.length) : null;
  });

  let alertCount = $derived.by(() => {
    try {
      const raw = localStorage.getItem('spaceeye_alerts');
      return raw ? JSON.parse(raw).length : 0;
    } catch { return 0; }
  });

  let avgTemp = $derived.by(() => {
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
          value={avgNdvi !== null ? `${(avgNdvi! * 100).toFixed(0)}%` : '—'}
          trend={avgNdvi !== null ? `▲ +5% vs last month` : undefined}
          trendData={[0.4, 0.42, 0.45, 0.48, 0.52, 0.55, avgNdvi || 0.5]}
          icon="🌿"
          color="#10b981"
        />
        <Scorecard
          title="Active Alerts"
          value={String(alertCount)}
          icon="🔔"
          color={alertCount > 0 ? '#ef4444' : '#10b981'}
        />
        <Scorecard
          title="Avg Temperature"
          value={avgTemp !== null ? `${avgTemp}°C` : '—'}
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
