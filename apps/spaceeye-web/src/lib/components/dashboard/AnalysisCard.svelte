<script lang="ts">
  import Card from '$lib/ui/components/Card.svelte';
  import Badge from '$lib/ui/components/Badge.svelte';
  import Button from '$lib/ui/components/Button.svelte';
  import type { SavedAnalysis } from '$lib/api/types';

  let { analysis, onDelete }: { analysis: SavedAnalysis; onDelete: () => void } = $props();
  let showStats = $state(false);

  type BadgeVariant = 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'destructive' | 'outline';
  const productColors: Record<string, BadgeVariant> = {
    NDVI: 'success', TCI: 'default', NDWI: 'primary', SAVI: 'warning',
    EVI: 'success', CIR: 'secondary', NBR: 'destructive', NDMI: 'primary',
  };
</script>

<Card interactive onclick={() => showStats = !showStats}>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <Badge variant={productColors[analysis.product] || 'default'}>{analysis.product}</Badge>
      <span class="text-[10px] text-muted-foreground">{analysis.collection}</span>
    </div>
    {#if analysis.cloud_cover != null}
      <div class="flex items-center gap-2">
        <span class="text-[10px] text-muted-foreground">Nuvem:</span>
        <span class="text-xs font-mono">{analysis.cloud_cover.toFixed(1)}%</span>
      </div>
    {/if}
    {#if analysis.centroid}
      <p class="text-[10px] text-muted-foreground font-mono">
        {analysis.centroid.lat.toFixed(4)}, {analysis.centroid.lon.toFixed(4)}
      </p>
    {/if}
    {#if analysis.created_at}
      <p class="text-[10px] text-muted-foreground">
        {new Date(analysis.created_at).toLocaleDateString('pt-BR')}
      </p>
    {/if}
    {#if showStats && analysis.statistics}
      <div class="pt-2 border-t border-border space-y-1">
        {#each Object.entries(analysis.statistics) as [key, value]}
          {#if typeof value === 'number'}
            <div class="flex justify-between text-[10px]">
              <span class="text-muted-foreground">{key}</span>
              <span class="font-mono">{value.toFixed(4)}</span>
            </div>
          {/if}
        {/each}
      </div>
    {/if}
    <div class="flex justify-end pt-1">
      <Button variant="ghost" size="sm" onclick={(e) => { e.stopPropagation(); onDelete(); }}>
        Remover
      </Button>
    </div>
  </div>
</Card>
