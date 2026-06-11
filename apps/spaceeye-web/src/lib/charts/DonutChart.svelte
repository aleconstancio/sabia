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

  function polarToCartesian(angle: number) {
    const rad = ((angle - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
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
  <svg width={size} height={size} viewBox="0 0 {size} {size}">
    {#each segments as seg}
      <path d={seg.path} fill={seg.color} />
    {/each}
    <circle cx={cx} cy={cy} r={r * innerRadius} fill="var(--card)" />
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
