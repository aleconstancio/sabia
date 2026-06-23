<script lang="ts">
  import { onMount } from 'svelte';
  import type { ImageResult } from '$lib/api/types';
  import { processBatch } from '$lib/api/client';
  import { pollTaskStatus } from '$lib/helpers/pollTask';
  import { downloadBlob, triggerDownload } from '$lib/helpers/download';
  import { logger } from '$lib/utils/logger';

  let {
    images = [] as ImageResult[],
    polygonCoords = null as number[][][] | null,
    product = 'NDVI',
  } = $props();

  let canvas: HTMLCanvasElement | undefined = $state(undefined);
  let timelineData = $state<{date: string; value: number}[]>([]);

  let loading = $state(false);
  let error = $state('');

  async function fetchTimeline() {
    if (images.length === 0) return;
    loading = true; error = '';

    const ids = images.map((i) => i.id);
    try {
      const { tasks } = await processBatch(ids.slice(0, 10), polygonCoords || [], product);

      const results: {date: string; value: number}[] = [];
      const pollResults = await Promise.allSettled(
        tasks.map(async (task) => {
          const result = await pollTaskStatus(task.task_id);
          return { task, result };
        })
      );
      for (const settled of pollResults) {
        if (settled.status === 'fulfilled') {
          const { task, result } = settled.value;
          if (result.status === 'done') {
            const img = images.find((i) => i.id === task.image_id);
            const rawValue = (result.result as { statistics?: { mean?: number } })?.statistics?.mean;
            const value = rawValue !== undefined && rawValue !== null ? rawValue : 0.5;
            if (img) {
              results.push({ date: img.acquired_at, value });
            }
          }
        }
      }
      results.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      timelineData = results;
    } catch (e: unknown) {
      logger.warn('NdviTimeline fetchTimeline error:', e);
      error = e instanceof Error ? e.message : String(e);
    } finally {
      loading = false;
    }
  }

  let isFallback = $derived(timelineData.length === 0);

  let barData = $derived(timelineData.length > 0 ? timelineData : images.slice(0, 10).map((i) => ({
    date: i.acquired_at,
    value: Math.max(0, 1 - (i.cloud_cover || 0) / 100),
  })));
  let maxVal = $derived(Math.max(...barData.map(d => d.value), 0.1));

  function drawChart() {
    if (!canvas || barData.length === 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const W = 280;
    const H = 140;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width = `${W}px`;
    canvas.style.height = `${H}px`;
    ctx.scale(dpr, dpr);
    const pad = { top: 10, bottom: 25, left: 5, right: 5 };
    const chartW = W - pad.left - pad.right;
    const chartH = H - pad.top - pad.bottom;

    ctx.clearRect(0, 0, W, H);

    barData.forEach((d, i) => {
      const x = pad.left + (i / Math.max(barData.length - 1, 1)) * chartW;
      const barH = (d.value / maxVal) * chartH;
      const y = pad.top + chartH - barH;

      const gradient = ctx.createLinearGradient(0, pad.top, 0, pad.top + chartH);
      gradient.addColorStop(0, '#1a9641');
      gradient.addColorStop(0.5, '#d9ef8b');
      gradient.addColorStop(1, '#d73027');
      ctx.fillStyle = gradient;
      ctx.fillRect(x - 2, y, 4, barH);

      ctx.fillStyle = '#888';
      ctx.font = '8px monospace';
      ctx.textAlign = 'center';
      const label = new Date(d.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      ctx.fillText(label, x, pad.top + chartH + 14);
    });
  }

  function exportCsv() {
    if (barData.length === 0) return;
    const headers = 'date,value\n';
    const rows = barData.map(d => `${d.date},${d.value.toFixed(4)}`).join('\n');
    const csv = headers + rows;
    const blob = new Blob([csv], { type: 'text/csv' });
    triggerDownload(blob, 'ndvi_timeline.csv');
  }

  $effect(() => {
    if (canvas && barData.length > 0) drawChart();
  });
</script>

<div class="rounded-lg border border-border bg-card p-3">
  <div class="flex items-center justify-between mb-2">
    <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide">{isFallback ? 'Cloud Cover Proxy' : 'Time Series'}</h4>
    {#if loading}
      <span class="text-xs text-muted-foreground">Processing...</span>
    {/if}
  </div>
  {#if barData.length > 0}
    <canvas bind:this={canvas} width={280} height={140} class="w-full h-[140px]" aria-label="NDVI time series chart"></canvas>
    <button
      class="text-xs text-primary hover:underline cursor-pointer bg-transparent border-none mt-1"
      onclick={exportCsv}
    >
      Download CSV
    </button>
  {:else if loading}
    <div class="h-[140px] flex items-center justify-center">
      <div class="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
    </div>
  {:else}
    <div class="h-[140px] flex items-center justify-center text-xs text-muted-foreground">
      {#if images.length > 0}
        <button
          class="text-xs text-primary hover:underline cursor-pointer bg-transparent border-none"
          onclick={fetchTimeline}
        >
          Build Time Series
        </button>
      {:else}
        Process images to see the time series
      {/if}
    </div>
  {/if}
</div>
