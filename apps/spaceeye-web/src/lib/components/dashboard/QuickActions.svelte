<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';
  import { dashboardState } from '$lib/stores/dashboard.svelte';
  import { historyStore } from '$lib/stores/history.svelte';
  import { buildCsvExport, downloadCsv } from '$lib/utils/dashboard';

  let loading = $state(false);
  let confirmClear = $state(false);

  async function refreshAll() {
    loading = true;
    await dashboardState.loadProfiles();
    loading = false;
  }

  function exportCsv() {
    const profiles = dashboardState.profiles;
    const headers = ['Name', 'Created', 'Lat', 'Lon', 'NDVI', 'Product', 'Temperature', 'Humidity', 'pH'];
    const rows = profiles.map(p => [
      p.name || 'Unnamed',
      p.created_at || '',
      p.centroid?.lat?.toFixed(4) || '',
      p.centroid?.lon?.toFixed(4) || '',
      (p.satellite_data?.stats?.mean as number)?.toFixed(4) || '',
      p.satellite_data?.product || '',
      p.weather_summary?.temperature?.toString() || '',
      p.weather_summary?.humidity?.toString() || '',
      p.soil_summary?.phh2o?.toFixed(1) || '',
    ]);
    const csv = buildCsvExport(profiles as unknown as Array<Record<string, unknown>>, headers, rows);
    downloadCsv(csv, `spaceeye-regions-${new Date().toISOString().slice(0, 10)}.csv`);
    toast.success('CSV exported');
  }

  function clearHistory() {
    confirmClear = true;
  }

  function executeClear() {
    historyStore.clear();
    toast.success('History cleared');
    confirmClear = false;
  }
</script>

<div class="flex items-center gap-2 p-2 bg-card/50 backdrop-blur-sm rounded-lg border border-border">
  <Button variant="default" size="xs" onclick={() => goto('/map')}>
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
    New Search
  </Button>
  <Button variant="outline" size="xs" disabled={loading} onclick={refreshAll}>
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1 {loading ? 'animate-spin' : ''}"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
    Refresh All
  </Button>
  <Button variant="outline" size="xs" onclick={exportCsv}>
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
    Export CSV
  </Button>
  {#if confirmClear}
    <div class="flex items-center gap-1">
      <span class="text-[10px] text-muted-foreground">Clear?</span>
      <Button variant="destructive" size="xs" onclick={executeClear}>Yes</Button>
      <Button variant="ghost" size="xs" onclick={() => confirmClear = false}>No</Button>
    </div>
  {:else}
    <Button variant="ghost" size="xs" class="text-muted-foreground hover:text-destructive" onclick={clearHistory}>
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
      Clear History
    </Button>
  {/if}
</div>
