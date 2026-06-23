<script lang="ts">
  import { alertStore } from '$lib/stores/alerts.svelte';
  import { historyStore } from '$lib/stores/history.svelte';
  import { monitorsStore } from '$lib/stores/monitors.svelte';
  import { formatTimeAgo } from '$lib/utils/dashboard';

  type FeedEvent = {
    id: string;
    type: 'alert' | 'analysis' | 'monitor';
    message: string;
    region: string;
    timestamp: string;
    unread: boolean;
  };

  let events = $derived.by(() => {
    const alertEvents: FeedEvent[] = alertStore.alerts.map(a => ({
      id: a.id,
      type: 'alert',
      message: a.message,
      region: a.region,
      timestamp: a.timestamp,
      unread: !a.read,
    }));

    const analysisEvents: FeedEvent[] = historyStore.all.map(r => ({
      id: r.id,
      type: 'analysis',
      message: `${r.product} analysis completed`,
      region: 'Unknown',
      timestamp: r.timestamp,
      unread: false,
    }));

    const monitorEvents: FeedEvent[] = monitorsStore.all
      .filter(m => m.lastResult)
      .map(m => ({
        id: m.id,
        type: 'monitor',
        message: m.lastResult!,
        region: m.bookmarkName,
        timestamp: m.lastChecked ?? new Date().toISOString(),
        unread: false,
      }));

    return [...alertEvents, ...analysisEvents, ...monitorEvents]
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 30);
  });

  function dotColor(type: FeedEvent['type']): string {
    switch (type) {
      case 'alert': return 'bg-destructive';
      case 'analysis': return 'bg-primary';
      case 'monitor': return 'bg-blue-500';
    }
  }
</script>

<div class="glass-panel rounded-lg p-3 flex flex-col">
  <div class="flex items-center justify-between mb-2">
    <h3 class="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Activity</h3>
    <span class="text-[10px] text-muted-foreground">{events.length} events</span>
  </div>
  <div class="flex-1 overflow-y-auto max-h-[280px] space-y-0" aria-live="polite">
    {#if events.length === 0}
      <p class="text-xs text-muted-foreground text-center py-8">No recent activity. Process an image or trigger an alert to see events here.</p>
    {/if}
    {#each events as event (event.id)}
      <div class="flex items-start gap-2 py-2 border-b border-border/30 last:border-0">
        <span class="mt-1.5 w-2 h-2 rounded-full flex-shrink-0 {dotColor(event.type)}" />
        <div class="flex-1 min-w-0">
          <p class="text-xs truncate">{event.message}</p>
          <div class="flex items-center gap-2 mt-0.5">
            <span class="text-[10px] text-muted-foreground truncate">{event.region}</span>
            <span class="text-[10px] text-muted-foreground ml-auto flex-shrink-0">{formatTimeAgo(event.timestamp)}</span>
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>
