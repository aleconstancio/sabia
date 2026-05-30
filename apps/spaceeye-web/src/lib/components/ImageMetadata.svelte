<script lang="ts">
  let { image = null as any }: { image: any } = $props();
</script>

{#if image}
  <div class="rounded-lg border border-border bg-card p-3 text-xs space-y-2">
    <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Detalhes da imagem</h4>
    <div class="grid grid-cols-2 gap-x-3 gap-y-1.5">
      <span class="text-muted-foreground">Satélite</span>
      <span class="text-right font-mono">{image.collection || '—'}</span>

      <span class="text-muted-foreground">ID</span>
      <span class="text-right font-mono truncate" title={image.id}>{image.id?.slice(0, 24)}...</span>

      <span class="text-muted-foreground">Data</span>
      <span class="text-right">{image.acquired_at ? new Date(image.acquired_at).toLocaleString('pt-BR') : '—'}</span>

      <span class="text-muted-foreground">Nuvem</span>
      <span class="text-right">{image.cloud_cover?.toFixed(1) ?? '—'}%</span>
    </div>
  </div>
{/if}
