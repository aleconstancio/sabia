<script lang="ts">
  import { scaleLinear } from 'd3-scale';
  import { line, area, curveMonotoneX } from 'd3-shape';

  let {
    data = [] as number[],
    width = 60,
    height = 24,
    color = '#10b981',
  } = $props();

  let chartData = $derived(data.map((v, i) => ({ x: i, y: v })));

  let xScale = $derived(
    scaleLinear()
      .domain([0, Math.max(data.length - 1, 1)])
      .range([2, width - 2])
  );

  let yScale = $derived(
    scaleLinear()
      .domain([0, 1])
      .range([height - 2, 2])
  );

  let linePath = $derived.by(() => {
    const gen = line<{ x: number; y: number }>()
      .x(d => xScale(d.x))
      .y(d => yScale(d.y))
      .curve(curveMonotoneX);
    return gen(chartData) || '';
  });

  let areaPath = $derived.by(() => {
    const gen = area<{ x: number; y: number }>()
      .x(d => xScale(d.x))
      .y0(height)
      .y1(d => yScale(d.y))
      .curve(curveMonotoneX);
    return gen(chartData) || '';
  });
</script>

{#if data.length > 1}
  <svg {width} {height} class="overflow-visible" role="img" aria-label="Sparkline showing trend data">
    <path d={areaPath} fill={color} fill-opacity={0.1} />
    <path d={linePath} fill="none" stroke={color} stroke-width={1.5} stroke-linecap="round" />
  </svg>
{:else}
  <div class="flex items-center justify-center" style="width: {width}px; height: {height}px;">
    <div class="w-1 h-1 rounded-full" style="background: {color}"></div>
  </div>
{/if}
