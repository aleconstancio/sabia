<script lang="ts">
  import type { DisasterAlertsResponse } from '$lib/api/types';

  let { data, loading }: {
    data: DisasterAlertsResponse | null;
    loading: boolean;
  } = $props();

  const categoryIcons: Record<string, string> = {
    wildfires: '🔥',
    severeStorms: '⛈️',
    floods: '🌊',
    volcanoes: '🌋',
    seaLakeIce: '🧊',
    drought: '☀️',
  };

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
{:else if data?.events?.length === 0}
  <div class="text-center py-8 text-muted-foreground text-sm">
    No active disasters near your location
  </div>
{:else if data?.events}
  <div class="space-y-2">
    <div class="text-[10px] text-muted-foreground mb-2">
      {data.nearby} event{data.nearby !== 1 ? 's' : ''} within 100km
    </div>
    {#each data.events as event}
      <div class="glass-panel rounded-lg p-2 flex items-center gap-3">
        <span class="text-lg">{categoryIcons[event.category] || '⚠️'}</span>
        <div class="flex-1 min-w-0">
          <div class="text-xs font-medium truncate">{event.title}</div>
          <div class="text-[10px] text-muted-foreground">
            {formatDate(event.date)} · {event.distance_km}km away
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}