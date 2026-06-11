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
