<script lang="ts">
  import { onDestroy } from 'svelte';

  let { lat = 0, lon = 0 }: { lat: number; lon: number } = $props();
  let landcover: any = $state(null);
  let loading = $state(false);

  const API_URL = import.meta.env.VITE_API_URL || '/api';
  let debounceTimer: ReturnType<typeof setTimeout>;

  $effect(() => {
    if (lat && lon) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        fetchLandcover();
      }, 300);
    }
  });

  onDestroy(() => clearTimeout(debounceTimer));

  async function fetchLandcover() {
    loading = true;
    try {
      const resp = await fetch(`${API_URL}/landcover/${lat}/${lon}`);
      if (resp.ok) landcover = await resp.json();
    } catch {} finally { loading = false; }
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
    <p class="text-sm text-muted-foreground">Carregando...</p>
  {:else if landcover}
    <p class="text-xs text-muted-foreground mb-2">ESA WorldCover 2021 · {landcover.resolution}</p>
    <div class="space-y-1 max-h-48 overflow-y-auto">
      {#each Object.entries(landcover.classes) as [code, name]}
        <div class="flex items-center gap-2 text-sm">
          <div class="w-3 h-3 rounded flex-shrink-0" style="background-color: {classColors[parseInt(code)] || '#666'}"></div>
          <span class="text-foreground">{name}</span>
        </div>
      {/each}
    </div>
  {:else}
    <p class="text-sm text-muted-foreground">Dados de cobertura do solo indisponíveis para esta região.</p>
  {/if}
</div>
