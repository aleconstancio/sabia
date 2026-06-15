<script lang="ts">
  import { api } from '$lib/api/client';

  let { lat = 0, lon = 0, polygonCoords = null as number[][][] | null }: { lat: number; lon: number; polygonCoords?: number[][][] | null } = $props();
  let landcover: Record<string, unknown> | null = $state(null);
  let loading = $state(false);
  let fetchError = $state('');

  $effect(() => {
    if (lat && lon) {
      const controller = new AbortController();
      const timer = setTimeout(() => {
        fetchLandcover(controller.signal);
      }, 300);
      return () => { clearTimeout(timer); controller.abort(); };
    }
  });


  async function fetchLandcover(signal?: AbortSignal) {
    loading = true;
    try {
      if (polygonCoords) {
        landcover = await api.post('/landcover/zonal', { coordinates: polygonCoords });
      } else {
        landcover = await api.get(`/landcover/${lat}/${lon}`);
      }
    } catch { fetchError = 'Falha ao carregar cobertura do solo'; } finally { loading = false; }
  }

  const classColors: Record<number, string> = {
    10: '#006400', 20: '#ffbb22', 30: '#ffff4c',
    40: '#f096ff', 50: '#fa0000', 60: '#b4b4b4',
    70: '#f0f0ff', 80: '#0066ff', 90: '#009900',
    95: '#00cc66', 100: '#8d8d8d',
  };
</script>

<div class="rounded-lg border border-border bg-card p-4">
  <h3 class="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Cobertura do Solo</h3>
  {#if loading}
    <div class="flex items-center gap-2 text-sm text-muted-foreground">
      <span class="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin"></span>
      <span>Carregando...</span>
    </div>
  {:else if landcover}
    {#if polygonCoords}
      <p class="text-xs text-muted-foreground mb-2">{landcover.source as string}</p>
      {#if landcover.centroid}
        <p class="text-xs text-muted-foreground mb-1">Centroide: {(landcover.centroid as { lat?: number; lon?: number }).lat?.toFixed(4)}, {(landcover.centroid as { lat?: number; lon?: number }).lon?.toFixed(4)}</p>
      {/if}
      {#if landcover.note}
        <p class="text-xs text-muted-foreground italic">{landcover.note as string}</p>
      {/if}
    {:else}
      <p class="text-xs text-muted-foreground mb-2">ESA WorldCover 2021 · {landcover.resolution as string}</p>
      <div class="space-y-1 max-h-48 overflow-y-auto">
        {#each Object.entries(landcover.classes as Record<string, string>) as [code, name]}
          <div class="flex items-center gap-2 text-sm">
            <div class="w-3 h-3 rounded flex-shrink-0" style="background-color: {classColors[parseInt(code)] || '#666'}"></div>
            <span class="text-foreground">{name}</span>
          </div>
        {/each}
      </div>
    {/if}
  {:else}
    <p class="text-sm text-muted-foreground">Dados de cobertura do solo indisponíveis para esta região.</p>
  {/if}
  {#if fetchError}
    <p class="text-sm text-destructive mt-2">{fetchError}</p>
  {/if}
</div>