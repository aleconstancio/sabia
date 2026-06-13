<script lang="ts">
  import type { StatsData } from '$lib/api/types';

  let { stats = null as StatsData | null, product = 'NDVI' } = $props();
  let canvas: HTMLCanvasElement | undefined = $state(undefined);

  function drawHistogram() {
    if (!canvas || !stats?.histogram?.deciles) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.width, H = canvas.height;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, W, H);

    const deciles = stats.histogram.deciles;
    const barW = (W - 20) / deciles.length;

    deciles.forEach((d: number, i: number) => {
      const normalized = Math.min(Math.abs(d) / 1.5, 1);
      const barH = 10 + normalized * (H - 30);
      const x = 10 + i * barW;
      const y = H - barH;
      const hue = d > 0 ? 120 + (1 - normalized) * 60 : 0;
      ctx.fillStyle = `hsl(${hue}, 70%, ${40 + normalized * 30}%)`;
      ctx.fillRect(x + 1, y, barW - 2, barH);
    });

    ctx.fillStyle = '#888';
    ctx.font = '8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(stats.min?.toFixed(2) || '', 10, H - 2);
    ctx.fillText(stats.max?.toFixed(2) || '', W - 10, H - 2);
  }

  $effect(() => { if (canvas && stats) drawHistogram(); });
</script>

{#if stats}
  <div class="rounded-lg border border-border bg-card p-3 mt-2">
    <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Estatísticas</h4>
    <div class="grid grid-cols-2 gap-x-3 gap-y-1 text-xs mb-2">
      <span class="text-muted-foreground">Média</span><span class="text-right font-mono">{stats.mean?.toFixed(3) ?? '—'}</span>
      <span class="text-muted-foreground">Desv. Pad.</span><span class="text-right font-mono">{stats.std?.toFixed(3) ?? '—'}</span>
      <span class="text-muted-foreground">Mínimo</span><span class="text-right font-mono">{stats.min?.toFixed(3) ?? '—'}</span>
      <span class="text-muted-foreground">Máximo</span><span class="text-right font-mono">{stats.max?.toFixed(3) ?? '—'}</span>
      <span class="text-muted-foreground">P10</span><span class="text-right font-mono">{stats.histogram?.p10?.toFixed(3) ?? '—'}</span>
      <span class="text-muted-foreground">P90</span><span class="text-right font-mono">{stats.histogram?.p90?.toFixed(3) ?? '—'}</span>
    </div>
    {#if stats.histogram?.deciles}
      <canvas bind:this={canvas} width={200} height={80} class="w-full h-20"></canvas>
    {/if}
  </div>
{/if}
