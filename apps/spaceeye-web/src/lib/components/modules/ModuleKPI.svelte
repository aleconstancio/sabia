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
