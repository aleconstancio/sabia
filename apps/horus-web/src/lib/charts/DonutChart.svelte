<script lang="ts">
  let {
    data = [] as { label: string; value: number; color: string }[],
    size = 120,
    innerRadius = 0.6,
  } = $props();

  let total = $derived(data.reduce((sum, d) => sum + d.value, 0));
  let cx = $derived(size / 2);
  let cy = $derived(size / 2);
  let r = $derived(size / 2 - 2);
  let hoveredIdx: number | null = $state(null);
  let tooltipX = $state(0);
  let tooltipY = $state(0);

  function polarToCartesian(angle: number) {
    const rad = ((angle - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  function onMouseMove(e: MouseEvent, idx: number) {
    hoveredIdx = idx;
    tooltipX = e.clientX;
    tooltipY = e.clientY;
  }

  let segments = $derived.by(() => {
    let currentAngle = 0;
    return data.map(d => {
      const angle = (d.value / total) * 360;
      const start = polarToCartesian(currentAngle);
      const end = polarToCartesian(currentAngle + angle);
      const largeArc = angle > 180 ? 1 : 0;
      const path = `M ${cx} ${cy} L ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y} Z`;
      currentAngle += angle;
      return { path, color: d.color, label: d.label, value: d.value, pct: ((d.value / total) * 100).toFixed(1) };
    });
  });
</script>

<div class="flex items-center gap-3">
  <svg width={size} height={size} viewBox="0 0 {size} {size}" role="img" aria-label="Donut chart showing proportional data">
    {#each segments as seg, i}
      <path
        d={seg.path}
        fill={seg.color}
        style="transform-origin: {cx}px {cy}px; transform: {hoveredIdx === i ? 'scale(1.02)' : 'scale(1)'};"
        onmouseenter={(e) => onMouseMove(e, i)}
        onmouseleave={() => { hoveredIdx = null; }}
        role="img"
      />
    {/each}
    <circle cx={cx} cy={cy} r={r * innerRadius} fill="var(--card)" pointer-events="none" />
  </svg>
  <div class="space-y-1">
    {#each data as d}
      <div class="flex items-center gap-2 text-xs">
        <div class="w-2 h-2 rounded-full flex-shrink-0" style="background: {d.color}"></div>
        <span class="text-muted-foreground truncate">{d.label}</span>
        <span class="font-mono">{((d.value / total) * 100).toFixed(1)}%</span>
      </div>
    {/each}
  </div>
</div>

{#if hoveredIdx !== null}
  <div
    class="pointer-events-none fixed z-50 rounded-md border bg-popover px-3 py-2 text-xs text-popover-foreground shadow-md"
    style="left: {tooltipX + 12}px; top: {tooltipY - 10}px;"
  >
    <div class="font-medium">{segments[hoveredIdx].label}</div>
    <div class="font-mono">{segments[hoveredIdx].value} ({segments[hoveredIdx].pct}%)</div>
  </div>
{/if}
