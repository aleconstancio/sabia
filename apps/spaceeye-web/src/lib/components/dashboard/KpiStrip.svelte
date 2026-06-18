<script lang="ts">
  import { dashboardState } from '$lib/stores/dashboard.svelte';
  import { alertStore } from '$lib/stores/alerts.svelte';
  import { historyStore } from '$lib/stores/history.svelte';
  import { Sparkline } from '$lib/charts';
  import Badge from '$lib/components/ui/badge/badge.svelte';

  let { avgNdvi, ndviTrendData, avgTemp }: {
    avgNdvi: number | null;
    ndviTrendData: number[];
    avgTemp: string | null;
  } = $props();

  let alertCount = $derived(alertStore.alerts.length);
  let ndviDisplay = $derived(avgNdvi != null ? `${(avgNdvi * 100).toFixed(0)}%` : '—');
  let tempDisplay = $derived(avgTemp != null ? `${avgTemp}°C` : '—');
  let analysesCount = $derived(historyStore.all.length);
</script>

<div class="grid grid-cols-2 lg:grid-cols-6 gap-2" aria-live="polite">
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
</div>
