<script lang="ts">
  import Badge from '$lib/ui/components/Badge.svelte';

  const products: Record<string, { label: string; description: string; category: string }> = {
    NDVI: { label: 'NDVI', description: 'Índice de Vegetação - diferencia solo nuo de vegetação densa', category: 'Vegetação' },
    TCI: { label: 'TCI', description: 'Imagem Verdadeira Cor - visual como o olho humano vê', category: 'Visual' },
    NDWI: { label: 'NDWI', description: 'Índice de Água - detecta corpos d\'água e umidade', category: 'Água' },
    SAVI: { label: 'SAVI', description: 'Vegetação Ajustada ao Solo - reduz efeito do solo nu', category: 'Vegetação' },
    EVI: { label: 'EVI', description: 'Vegetação Melhorada - mais sensível em áreas densas', category: 'Vegetação' },
    MSAVI2: { label: 'MSAVI2', description: 'SAVI Modificado - auto-ajusta para solo nu', category: 'Vegetação' },
    VARI: { label: 'VARI', description: 'Vegetação Apropriada - usa apenas bandas visíveis', category: 'Vegetação' },
    MNDWI: { label: 'MNDWI', description: 'Água Modificada - melhor para áreas urbanas', category: 'Água' },
    CIR: { label: 'CIR', description: 'Cor Infravermelha - realça vegetação saudável em vermelho', category: 'Visual' },
    NBR: { label: 'NBR', description: 'Razão de Queimadas - detecta áreas queimadas', category: 'Solo' },
    NDMI: { label: 'NDMI', description: 'Umidade - monitora estresse hídrico da vegetação', category: 'Vegetação' },
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
