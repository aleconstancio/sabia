<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { dashboardState } from '$lib/stores/dashboard.svelte';
  import { alertStore } from '$lib/stores/alerts.svelte';
  import { historyStore } from '$lib/stores/history.svelte';
  import { toast } from 'svelte-sonner';
  import { logger } from '$lib/utils/logger';
  import StatusBar from '$lib/components/dashboard/StatusBar.svelte';
  import OverviewMap from '$lib/components/dashboard/OverviewMap.svelte';
  import KpiStrip from '$lib/components/dashboard/KpiStrip.svelte';
  import ActivityFeed from '$lib/components/dashboard/ActivityFeed.svelte';
  import QuickActions from '$lib/components/dashboard/QuickActions.svelte';
  import PortfolioGrid from './PortfolioGrid.svelte';
  import * as Select from '$lib/components/ui/select';
  import { Skeleton } from '$lib/components/ui/skeleton';
  import type { RegionProfile } from '$lib/api/types';

  let sortBy = $state<'name' | 'date' | 'ndvi'>('date');
  let filterProductRaw = $state('');
  let currentPage = $state(1);
  const pageSize = 24;

  const productOptions = ['NDVI', 'TCI', 'NDWI', 'NBR'];
  let filterProduct = $derived(filterProductRaw || null);

  let filteredProfiles = $derived.by(() => {
    let result = dashboardState.profiles;
    if (filterProduct) {
      result = result.filter(p => p.satellite_data?.product === filterProduct);
    }
    result = [...result].sort((a: RegionProfile, b: RegionProfile) => {
      if (sortBy === 'name') return (a.name || '').localeCompare(b.name || '');
      if (sortBy === 'ndvi') {
        const aNdvi = (a.satellite_data?.stats?.mean as number) || 0;
        const bNdvi = (b.satellite_data?.stats?.mean as number) || 0;
        return bNdvi - aNdvi;
      }
      return (b.created_at || '').localeCompare(a.created_at || '');
    });
    return result;
  });

  $effect(() => {
    filteredProfiles;
    currentPage = 1;
  });

  let totalProfiles = $derived(filteredProfiles.length);
  let totalPages = $derived(Math.ceil(totalProfiles / pageSize));

  let paginatedProfiles = $derived.by(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredProfiles.slice(start, start + pageSize);
  });

  let ndviWithDates = $derived.by(() => {
    return dashboardState.profiles
      .map(p => ({ mean: p.satellite_data?.stats?.mean as number | undefined, date: p.created_at }))
      .filter((e): e is { mean: number; date: string | null } => e.mean != null)
      .sort((a, b) => (a.date ?? '').localeCompare(b.date ?? ''));
  });

  let avgNdvi = $derived.by(() => {
    const values = ndviWithDates.map(e => e.mean);
    return values.length ? (values.reduce((a, b) => a + b, 0) / values.length) : null;
  });

  let ndviTrendData = $derived.by(() => {
    if (ndviWithDates.length < 2) return [];
    return ndviWithDates.map(e => e.mean);
  });

  let avgTemp = $derived.by(() => {
    const temps = dashboardState.profiles
      .map(p => p.weather_summary?.temperature)
      .filter(t => t != null) as number[];
    return temps.length ? (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1) : null;
  });

  let confirmDeleteId = $state<string | null>(null);

  function handleDeleteProfile(id: string) {
    confirmDeleteId = id;
  }

  function executeDelete() {
    if (confirmDeleteId) {
      dashboardState.deleteProfile(confirmDeleteId);
      toast.success('Region deleted');
      confirmDeleteId = null;
    }
  }

  onMount(() => {
    dashboardState.loadProfiles();
    dashboardState.startAutoRefresh(30000);
  });

  onDestroy(() => {
    dashboardState.stopAutoRefresh();
  });
</script>

<div class="h-screen flex flex-col bg-background overflow-hidden">
  <StatusBar />

  {#if confirmDeleteId}
    {@const profile = dashboardState.profiles.find(p => p.id === confirmDeleteId)}
    <div class="flex items-center justify-between gap-2 px-4 py-2 bg-destructive/10 border border-destructive/30 text-sm text-destructive mx-2 mt-2 rounded-lg">
      <span>Delete profile "{profile?.name || 'Unnamed Region'}"?</span>
      <div class="flex items-center gap-2">
        <button class="px-2 py-0.5 text-xs rounded border border-destructive/30 hover:bg-destructive/20 transition-colors" onclick={() => confirmDeleteId = null}>No</button>
        <button class="px-2 py-0.5 text-xs rounded bg-destructive text-destructive-foreground hover:bg-destructive/90 transition-colors" onclick={executeDelete}>Yes, delete</button>
      </div>
    </div>
  {/if}

  {#if dashboardState.error}
    <div class="bg-destructive/10 border border-destructive/30 rounded-lg px-4 py-2 text-sm text-destructive mx-2 mt-2">
      {dashboardState.error}
    </div>
  {/if}

  {#if dashboardState.isLoading && dashboardState.profiles.length === 0}
    <div class="command-grid flex-1 min-h-0">
      <div class="map-area">
        <Skeleton variant="rectangular" class="w-full h-full min-h-[280px] rounded-lg" />
      </div>

      <div class="kpi-area">
        <div class="grid grid-cols-2 lg:grid-cols-6 gap-2">
          {#each Array(6) as _}
            <Skeleton variant="card" class="h-20" />
          {/each}
        </div>
      </div>

      <div class="feed-area">
        <Skeleton variant="card" class="h-full min-h-[200px]" />
      </div>

      <div class="stations-area">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {#each Array(6) as _}
            <Skeleton variant="card" class="h-40" />
          {/each}
        </div>
      </div>
    </div>
  {:else if dashboardState.profiles.length === 0}
    <div class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <h3 class="text-lg font-semibold text-foreground mb-1">No regions monitored</h3>
        <p class="text-sm text-muted-foreground max-w-sm mb-4">Draw an area on the map, process imagery, and save as a profile to build your ESG command center.</p>
        <button class="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors" onclick={() => goto('/map')}>
          Open Map
        </button>
      </div>
    </div>
  {:else}
    <div class="command-grid flex-1 min-h-0">
      <div class="map-area">
        <OverviewMap />
      </div>

      <div class="kpi-area">
        <KpiStrip {avgNdvi} {ndviTrendData} {avgTemp} />
        <div class="mt-2">
          <QuickActions />
        </div>
      </div>

      <div class="feed-area flex flex-col gap-2 min-h-0">
        <ActivityFeed />
      </div>

      <div class="stations-area">
        <div class="flex items-center justify-between mb-2 px-1">
          <div class="flex items-center gap-3">
            <h2 class="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Stations</h2>
            <div class="flex items-center gap-2">
              <Select.Root type="single" bind:value={sortBy}>
                <Select.Trigger class="h-6 text-[10px] w-[70px] px-1.5">
                  {sortBy === 'name' ? 'Name' : sortBy === 'ndvi' ? 'NDVI' : 'Date'}
                </Select.Trigger>
                <Select.Content>
                  <Select.Item value="name">Name</Select.Item>
                  <Select.Item value="date">Date</Select.Item>
                  <Select.Item value="ndvi">NDVI</Select.Item>
                </Select.Content>
              </Select.Root>
              <Select.Root type="single" bind:value={filterProductRaw}>
                <Select.Trigger class="h-6 text-[10px] w-[70px] px-1.5">
                  {filterProduct || 'All'}
                </Select.Trigger>
                <Select.Content>
                  <Select.Item value="">All</Select.Item>
                  {#each productOptions as option}
                    <Select.Item value={option}>{option}</Select.Item>
                  {/each}
                </Select.Content>
              </Select.Root>
            </div>
          </div>
          <span class="text-[10px] text-muted-foreground font-mono">
            {Math.min((currentPage - 1) * pageSize + 1, totalProfiles)}-{Math.min(currentPage * pageSize, totalProfiles)} of {totalProfiles}
          </span>
        </div>

        <PortfolioGrid profiles={paginatedProfiles} deleteProfile={handleDeleteProfile} {confirmDeleteId} />

        {#if totalPages > 1}
          <div class="flex items-center justify-center gap-3 mt-2 pb-2">
            <button
              class="text-[10px] px-2 py-1 rounded border border-border text-muted-foreground hover:text-foreground hover:bg-muted transition-colors disabled:opacity-30"
              disabled={currentPage <= 1}
              onclick={() => currentPage--}
            >
              Prev
            </button>
            <span class="text-[10px] text-muted-foreground font-mono">{currentPage}/{totalPages}</span>
            <button
              class="text-[10px] px-2 py-1 rounded border border-border text-muted-foreground hover:text-foreground hover:bg-muted transition-colors disabled:opacity-30"
              disabled={currentPage >= totalPages}
              onclick={() => currentPage++}
            >
              Next
            </button>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>
