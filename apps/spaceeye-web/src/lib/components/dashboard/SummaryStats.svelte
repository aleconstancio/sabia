<script lang="ts">
  import Card from '$lib/ui/components/Card.svelte';
  import type { SavedAnalysis } from '$lib/api/types';

  let { analyses, total }: { analyses: SavedAnalysis[]; total: number } = $props();

  let productCounts = $derived.by(() => {
    const counts: Record<string, number> = {};
    for (const a of analyses) { counts[a.product] = (counts[a.product] || 0) + 1; }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  });

  let collectionCounts = $derived.by(() => {
    const counts: Record<string, number> = {};
    for (const a of analyses) { counts[a.collection] = (counts[a.collection] || 0) + 1; }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  });

  let avgNdvi = $derived.by(() => {
    const ndviStats = analyses
      .filter((a): a is SavedAnalysis & { statistics: Record<string, unknown> } => a.product === 'NDVI' && a.statistics != null && typeof a.statistics.mean === 'number')
      .map(a => a.statistics.mean as number);
    if (ndviStats.length === 0) return null;
    return (ndviStats.reduce((s, v) => s + v, 0) / ndviStats.length).toFixed(3);
  });
</script>

<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
  <Card>
    <p class="text-2xl font-bold text-primary">{total}</p>
    <p class="text-xs text-muted-foreground">Total de análises</p>
  </Card>
  <Card>
    <p class="text-2xl font-bold text-primary">{productCounts.length}</p>
    <p class="text-xs text-muted-foreground">Produtos utilizados</p>
    <div class="flex flex-wrap gap-1 mt-1">
      {#each productCounts.slice(0, 4) as [product, count]}
        <span class="text-[10px] px-1.5 py-0.5 rounded bg-muted">{product} ({count})</span>
      {/each}
    </div>
  </Card>
  <Card>
    <p class="text-2xl font-bold text-primary">{collectionCounts.length}</p>
    <p class="text-xs text-muted-foreground">Coleções satélite</p>
  </Card>
  <Card>
    {#if avgNdvi !== null}
      <p class="text-2xl font-bold text-primary">{avgNdvi}</p>
      <p class="text-xs text-muted-foreground">NDVI médio</p>
    {:else}
      <p class="text-2xl font-bold text-muted-foreground">—</p>
      <p class="text-xs text-muted-foreground">Sem dados NDVI</p>
    {/if}
  </Card>
</div>
