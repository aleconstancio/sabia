<script lang="ts">
  import Button from '$lib/ui/components/Button.svelte';

  let {
    showLegend = $bindable(false),
    onZoomIn = () => {},
    onZoomOut = () => {},
    onClearOverlay = () => {},
    hasOverlay = false,
    product = 'NDVI',
  } = $props();
</script>

<div class="absolute left-4 top-1/2 -translate-y-1/2 z-[999] flex flex-col gap-2">
  <Button size="sm" onclick={onZoomIn} class="!w-10 !h-10 !p-0 !text-lg">+</Button>
  <Button size="sm" onclick={onZoomOut} class="!w-10 !h-10 !p-0 !text-lg">−</Button>
  {#if hasOverlay}
    <Button size="sm" variant="secondary" onclick={onClearOverlay} class="!w-10 !h-10 !p-0 !text-xs">✕</Button>
  {/if}
  <Button size="sm" variant="secondary" onclick={() => showLegend = !showLegend} class="!w-10 !h-10 !p-0 !text-xs">N</Button>
</div>

{#if showLegend}
  <div class="absolute left-4 bottom-8 z-[999] rounded-lg border border-border bg-card p-3 shadow-lg">
    {#if product === 'NDVI' || product === 'NDWI' || product === 'SAVI' || product === 'EVI' || product === 'MSAVI2' || product === 'VARI' || product === 'NDMI' || product === 'NBR'}
      <p class="text-xs font-semibold mb-1">{product}</p>
      <div class="w-4 h-40 rounded" style="background: linear-gradient(to top, #d73027, #fc8d59, #fee08b, #d9ef8b, #91cf60, #1a9641);"></div>
      <div class="flex justify-between text-xs text-muted-foreground w-4"><span style="position: relative; left: -16px;">1</span></div>
      <div class="flex justify-between text-xs text-muted-foreground w-4"><span style="position: relative; left: -8px;">0</span></div>
      <div class="flex justify-between text-xs text-muted-foreground w-4"><span>-1</span></div>
    {:else if product === 'TCI'}
      <p class="text-xs font-semibold mb-1">True Color</p>
      <p class="text-xs text-muted-foreground">RGB composição natural</p>
    {/if}
  </div>
{/if}
