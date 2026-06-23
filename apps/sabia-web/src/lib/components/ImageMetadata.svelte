<script lang="ts">
  import type { ImageResult } from '$lib/api/types';

  let { image = null as ImageResult | null }: { image: ImageResult | null } = $props();
</script>

{#if image}
  <div class="rounded-lg border border-border bg-card p-3 text-xs space-y-2">
    <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Image Details</h4>
    <div class="grid grid-cols-2 gap-x-3 gap-y-1.5">
      <span class="text-muted-foreground">Satellite</span>
      <span class="text-right font-mono">{image.collection || '—'}</span>

      <span class="text-muted-foreground">ID</span>
      <span class="text-right font-mono truncate" title={image.id}>{image.id?.slice(0, 24)}...</span>

      <span class="text-muted-foreground">Date</span>
      <span class="text-right">{image.acquired_at ? new Date(image.acquired_at).toLocaleString() : '—'}</span>

      <span class="text-muted-foreground">Cloud</span>
      <span class="text-right">{image.cloud_cover?.toFixed(1) ?? '—'}%</span>
    </div>
  </div>
{/if}
