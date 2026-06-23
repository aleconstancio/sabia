<script lang="ts">
  import { Button } from '$lib/components/ui/button';

  let {
    showLegend = $bindable(false),
    onZoomIn = () => {},
    onZoomOut = () => {},
    onClearOverlay = () => {},
    onMeasure = () => {},
    hasOverlay = false,
    product = 'NDVI',
    basemap = 'satellite',
    onBasemapChange = (b: string) => {},
    opacity = 0.8,
    onOpacityChange = (o: number) => {},
  }: {
    showLegend?: boolean;
    onZoomIn?: () => void;
    onZoomOut?: () => void;
    onClearOverlay?: () => void;
    onMeasure?: () => void;
    hasOverlay?: boolean;
    product?: string;
    basemap?: string;
    onBasemapChange?: (b: string) => void;
    opacity?: number;
    onOpacityChange?: (o: number) => void;
  } = $props();

  let showBasemapMenu = $state(false);
</script>

<div class="absolute left-2 sm:left-4 top-1/2 -translate-y-1/2 z-[999] flex flex-col gap-1.5 sm:gap-2">
  <Button size="sm" onclick={onZoomIn} class="!w-8 !h-8 sm:!w-10 sm:!h-10 !p-0 !text-base sm:!text-lg" aria-label="Zoom in">+</Button>
  <Button size="sm" onclick={onZoomOut} class="!w-8 !h-8 sm:!w-10 sm:!h-10 !p-0 !text-base sm:!text-lg" aria-label="Zoom out">−</Button>
  {#if hasOverlay}
    <Button size="sm" variant="secondary" onclick={onClearOverlay} class="!w-8 !h-8 sm:!w-10 sm:!h-10 !p-0 !text-xs" aria-label="Remove overlay">✕</Button>
  {/if}
  <Button size="sm" variant="secondary" onclick={() => showLegend = !showLegend} class="!w-8 !h-8 sm:!w-10 sm:!h-10 !p-0 !text-xs" aria-label="Show legend">N</Button>
  <Button size="sm" variant="secondary" onclick={onMeasure} class="!w-8 !h-8 sm:!w-10 sm:!h-10 !p-0 !text-xs" aria-label="Measure coordinates">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 6 1 22 8 22 8 8"/><path d="M20 10c-3-3-6 3-10 0"/><line x1="12" y1="16" x2="12" y2="18"/></svg>
  </Button>
  <Button size="sm" variant="secondary" onclick={() => showBasemapMenu = !showBasemapMenu} class="!w-8 !h-8 sm:!w-10 sm:!h-10 !p-0 !text-xs" aria-label="Change basemap">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
  </Button>
</div>

{#if showBasemapMenu}
  <div class="absolute left-4 bottom-36 z-[999] rounded-lg border border-border bg-card p-2 shadow-lg">
    {#each ['satellite', 'osm', 'dark'] as b}
      <button
        class="block w-full text-left text-xs px-2 py-1 rounded hover:bg-muted cursor-pointer bg-transparent border-none"
        class:bg-muted={basemap === b}
        onclick={() => { onBasemapChange(b); showBasemapMenu = false; }}
      >
        {b === 'satellite' ? 'Satellite' : b === 'osm' ? 'OpenStreetMap' : 'Dark'}
      </button>
    {/each}
    <div class="border-t border-border mt-1 pt-1">
      <label for="opacity-slider" class="text-xs text-muted-foreground block mb-1">Opacity</label>
      <input id="opacity-slider" type="range" min="0.1" max="1" step="0.1" value={opacity}
        oninput={(e) => onOpacityChange(parseFloat((e.target as HTMLInputElement).value))}
        class="w-full accent-emerald-500" />
    </div>
  </div>
{/if}

{#if showLegend}
  <div class="absolute left-4 bottom-8 z-[999] rounded-lg border border-border bg-card p-3 shadow-lg">
    {#if product === 'NDVI' || product === 'NDWI' || product === 'SAVI' || product === 'EVI' || product === 'MSAVI2' || product === 'VARI' || product === 'NDMI' || product === 'NBR'}
      <p class="text-xs font-semibold mb-1">{product}</p>
      <div class="w-4 h-40 rounded" style="background: linear-gradient(to top, #d73027, #fc8d59, #fee08b, #d9ef8b, #91cf60, #1a9641);"></div>
      <div class="flex justify-between text-xs text-muted-foreground w-4"><span class="relative -left-4">1</span></div>
      <div class="flex justify-between text-xs text-muted-foreground w-4"><span class="relative -left-2">0</span></div>
      <div class="flex justify-between text-xs text-muted-foreground w-4"><span>-1</span></div>
    {:else if product === 'TCI'}
      <p class="text-xs font-semibold mb-1">True Color</p>
      <p class="text-xs text-muted-foreground">RGB natural composition</p>
    {/if}
  </div>
{/if}
