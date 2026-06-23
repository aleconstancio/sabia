<script lang="ts">
  import { Badge } from '$lib/components/ui/badge';

  const products: Record<string, { label: string; description: string; category: string }> = {
    NDVI: { label: 'NDVI', description: 'Vegetation Index - differentiates bare soil from dense vegetation', category: 'Vegetation' },
    TCI: { label: 'TCI', description: 'True Color Image - visual as the human eye sees', category: 'Visual' },
    NDWI: { label: 'NDWI', description: 'Water Index - detects water bodies and moisture', category: 'Water' },
    SAVI: { label: 'SAVI', description: 'Soil Adjusted Vegetation - reduces bare soil effect', category: 'Vegetation' },
    EVI: { label: 'EVI', description: 'Enhanced Vegetation - more sensitive in dense areas', category: 'Vegetation' },
    MSAVI2: { label: 'MSAVI2', description: 'Modified SAVI - self-adjusts for bare soil', category: 'Vegetation' },
    VARI: { label: 'VARI', description: 'Visible Atmospherically Resistant - uses only visible bands', category: 'Vegetation' },
    MNDWI: { label: 'MNDWI', description: 'Modified Water Index - better for urban areas', category: 'Water' },
    CIR: { label: 'CIR', description: 'Color Infrared - highlights healthy vegetation in red', category: 'Visual' },
    NBR: { label: 'NBR', description: 'Burn Ratio - detects burned areas', category: 'Soil' },
    NDMI: { label: 'NDMI', description: 'Moisture Index - monitors vegetation water stress', category: 'Vegetation' },
  };

  let { product, compact = false }: { product: string; compact?: boolean } = $props();
  const info = $derived(products[product] || null);
</script>

{#if info}
  {#if compact}
    <span class="text-xs text-muted-foreground" title={info.description}>
      {info.label}
      <Badge variant="outline" class="!text-[10px] !px-1">{info.category}</Badge>
    </span>
  {:else}
    <div class="flex items-start gap-2 p-2 rounded bg-muted/50">
      <div class="flex-1 min-w-0">
        <p class="text-xs font-medium">{info.label}</p>
        <p class="text-[11px] text-muted-foreground">{info.description}</p>
      </div>
      <Badge variant="outline" class="!text-[10px] shrink-0">{info.category}</Badge>
    </div>
  {/if}
{/if}
