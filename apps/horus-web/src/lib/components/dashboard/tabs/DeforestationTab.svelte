<script lang="ts">
  import type { DeforestationAlertsResponse } from '$lib/api/types';

  let { data, loading }: {
    data: DeforestationAlertsResponse | null;
    loading: boolean;
  } = $props();

  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
</script>

{#if loading}
  <div class="space-y-2">
    {#each Array(3) as _}
      <div class="h-12 bg-muted/30 rounded-lg animate-pulse"></div>
    {/each}
  </div>
{:else if data?.alerts?.length === 0}
  <div class="text-center py-8 text-muted-foreground text-sm">
    No deforestation alerts near your location
  </div>
{:else if data?.alerts}
  <div class="space-y-2">
    <div class="flex items-center gap-4 text-[10px] text-muted-foreground mb-2">
      <span>{data.count} alert{data.count !== 1 ? 's' : ''} in last 30 days</span>
      <span class="font-mono text-destructive">{data.total_area_ha.toLocaleString()} ha affected</span>
    </div>
    {#each data.alerts as alert}
      <div class="glass-panel rounded-lg p-2 flex items-center gap-3">
        <span class="text-lg">{alert.class === 'deforestation' ? '🪓' : '⚠️'}</span>
        <div class="flex-1 min-w-0">
          <div class="text-xs font-medium">
            {alert.municipality}, {alert.state}
          </div>
          <div class="text-[10px] text-muted-foreground">
            {formatDate(alert.date)} · {alert.area_ha} ha · {alert.biome}
          </div>
        </div>
        <span class="text-[10px] px-1.5 py-0.5 rounded {alert.class === 'deforestation' ? 'bg-destructive/20 text-destructive' : 'bg-orange-500/20 text-orange-400'}">
          {alert.class}
        </span>
      </div>
    {/each}
  </div>
{/if}