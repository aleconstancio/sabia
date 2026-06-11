<script lang="ts">
  import { LayerCake, Svg } from 'layercake';
  import { scaleLinear, scaleTime } from 'd3-scale';
  import { line, area, curveMonotoneX } from 'd3-shape';

  let {
    data = [] as { date: string; value: number }[],
    height = 200,
    color = '#10b981',
    showTooltip = true,
    showAxis = true,
  } = $props();

  let tooltipData = $state<{ date: string; value: number; x: number; y: number } | null>(null);
  let containerWidth = $state(280);

  let xScale = $derived(
    scaleTime()
      .domain(data.length > 0 ? [new Date(data[0].date), new Date(data[data.length - 1].date)] : [new Date(), new Date()])
      .range([0, containerWidth])
  );

  let yScale = $derived(
    scaleLinear()
      .domain([0, 1])
      .range([height - 30, 0])
  );

  let linePath = $derived.by(() => {
    const gen = line<{ date: string; value: number }>()
      .x(d => xScale(new Date(d.date)))
      .y(d => yScale(d.value))
      .curve(curveMonotoneX);
    return gen(data) || '';
  });

  let areaPath = $derived.by(() => {
    const gen = area<{ date: string; value: number }>()
      .x(d => xScale(new Date(d.date)))
      .y0(height - 30)
      .y1(d => yScale(d.value))
      .curve(curveMonotoneX);
    return gen(data) || '';
  });

  function handleMouseMove(e: MouseEvent) {
    if (!showTooltip || data.length === 0) return;
    const rect = (e.target as SVGElement).getBoundingClientRect();
    const x = e.clientX - rect.left;
    const dateAtMouse = xScale.invert(x);
    const closest = data.reduce((prev, curr) =>
      Math.abs(new Date(curr.date).getTime() - dateAtMouse.getTime()) <
      Math.abs(new Date(prev.date).getTime() - dateAtMouse.getTime()) ? curr : prev
    );
    tooltipData = {
      date: closest.date,
      value: closest.value,
      x: xScale(new Date(closest.date)),
      y: yScale(closest.value),
    };
  }
</script>

<div class="relative" style="height: {height}px;" bind:clientWidth={containerWidth}>
  {#if data.length > 0}
    <svg width={containerWidth} height={height} class="overflow-visible">
      <!-- Area fill -->
      <path d={areaPath} fill={color} fill-opacity={0.15} />
      <!-- Line -->
      <path d={linePath} fill="none" stroke={color} stroke-width={2} />
      <!-- Interactive overlay -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <rect
        width={containerWidth}
        height={height}
        fill="transparent"
        onmousemove={handleMouseMove}
        onmouseleave={() => tooltipData = null}
      />
      <!-- Axis labels -->
      {#if showAxis}
        {#each data.filter((_, i) => i % Math.max(1, Math.floor(data.length / 6)) === 0 || i === data.length - 1) as d}
          <text
            x={xScale(new Date(d.date))}
            y={height - 8}
            text-anchor="middle"
            class="fill-muted-foreground text-[8px]"
          >
            {new Date(d.date).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' })}
          </text>
        {/each}
      {/if}
    </svg>

    {#if tooltipData}
      <div
        class="absolute pointer-events-none z-50 px-2 py-1 text-xs rounded bg-card border border-border shadow-lg"
        style="left: {tooltipData.x}px; top: {tooltipData.y - 40}px; transform: translateX(-50%);"
      >
        <p class="font-mono font-bold">{tooltipData.value.toFixed(4)}</p>
        <p class="text-muted-foreground">{new Date(tooltipData.date).toLocaleDateString('pt-BR')}</p>
      </div>
    {/if}
  {:else}
    <div class="flex items-center justify-center h-full text-xs text-muted-foreground">
      No data available
    </div>
  {/if}
</div>
