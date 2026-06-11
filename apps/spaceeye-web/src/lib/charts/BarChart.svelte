<script lang="ts">
  let {
    data = [] as { label: string; value: number; color?: string }[],
    height = 150,
    horizontal = false,
  } = $props();

  let maxVal = $derived(Math.max(...data.map(d => d.value), 1));
</script>

<div style="height: {height}px;" class="overflow-hidden">
  <svg width="100%" height={height} viewBox="0 0 100 {height}" preserveAspectRatio="none">
    {#each data as d, i}
      {#if horizontal}
        {@const barWidth = (d.value / maxVal) * 90}
        <rect
          x="5"
          y={(i / data.length) * height + 2}
          width="{barWidth}%"
          height={height / data.length - 4}
          fill={d.color || 'var(--primary)'}
          rx="2"
        />
        <text
          x="100%"
          y={(i / data.length) * height + height / data.length / 2 + 2}
          text-anchor="end"
          class="fill-muted-foreground text-[8px]"
          dy="0.35em"
        >
          {d.label}
        </text>
      {:else}
        {@const barHeight = (d.value / maxVal) * (height - 30)}
        {@const barWidth = 90 / data.length - 2}
        <rect
          x="{(i / data.length) * 90 + 5 + 1}%"
          y={height - 25 - barHeight}
          width="{barWidth}%"
          height={barHeight}
          fill={d.color || 'var(--primary)'}
          rx="2"
        />
        <text
          x="{(i / data.length) * 90 + 5 + barWidth / 2 + 1}%"
          y={height - 5}
          text-anchor="middle"
          class="fill-muted-foreground text-[7px]"
        >
          {d.label}
        </text>
      {/if}
    {/each}
  </svg>
</div>
