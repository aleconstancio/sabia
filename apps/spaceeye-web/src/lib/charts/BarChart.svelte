<script lang="ts">
  let {
    data = [] as { label: string; value: number; color?: string }[],
    height = 150,
    horizontal = false,
  } = $props();

  let maxVal = $derived(Math.max(...data.map(d => d.value), 1));
  let hoveredIdx: number | null = $state(null);
  let tooltipX = $state(0);
  let tooltipY = $state(0);

  function onMouseMove(e: MouseEvent, idx: number) {
    hoveredIdx = idx;
    tooltipX = e.clientX;
    tooltipY = e.clientY;
  }
</script>

<div style="height: {height}px;" class="overflow-hidden">
  <svg width="100%" height={height} viewBox="0 0 100 {height}" preserveAspectRatio="none" role="img" aria-label="Bar chart showing categorical data">
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
          opacity={hoveredIdx === null || hoveredIdx === i ? 1 : 0.4}
          onmouseenter={(e) => onMouseMove(e, i)}
          onmouseleave={() => { hoveredIdx = null; }}
          role="img"
        />
        <text
          x="100%"
          y={(i / data.length) * height + height / data.length / 2 + 2}
          text-anchor="end"
          class="fill-muted-foreground text-[8px]"
          dy="0.35em"
          pointer-events="none"
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
          opacity={hoveredIdx === null || hoveredIdx === i ? 1 : 0.4}
          onmouseenter={(e) => onMouseMove(e, i)}
          onmouseleave={() => { hoveredIdx = null; }}
          role="img"
        />
        <text
          x="{(i / data.length) * 90 + 5 + barWidth / 2 + 1}%"
          y={height - 5}
          text-anchor="middle"
          class="fill-muted-foreground text-[7px]"
          pointer-events="none"
        >
          {d.label}
        </text>
      {/if}
    {/each}
  </svg>
</div>

{#if hoveredIdx !== null}
  <div
    class="pointer-events-none fixed z-50 rounded-md border bg-popover px-3 py-2 text-xs text-popover-foreground shadow-md"
    style="left: {tooltipX + 12}px; top: {tooltipY - 10}px;"
  >
    <div class="font-medium">{data[hoveredIdx].label}</div>
    <div class="font-mono">{data[hoveredIdx].value}</div>
  </div>
{/if}
