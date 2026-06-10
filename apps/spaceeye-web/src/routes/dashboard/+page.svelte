<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { dashboardState, loadAnalyses, deleteAnalysis } from '$lib/stores/dashboard.svelte';
  import Button from '$lib/ui/components/Button.svelte';
  import Badge from '$lib/ui/components/Badge.svelte';
  import Spinner from '$lib/ui/components/Spinner.svelte';
  import EmptyState from '$lib/ui/components/EmptyState.svelte';
  import Select from '$lib/ui/components/Select.svelte';
  import SummaryStats from '$lib/components/dashboard/SummaryStats.svelte';
  import AnalysisCard from '$lib/components/dashboard/AnalysisCard.svelte';

  onMount(() => loadAnalyses());

  const productOptions = [
    { value: '', label: 'Todos os produtos' },
    { value: 'NDVI', label: 'NDVI' },
    { value: 'TCI', label: 'TCI' },
    { value: 'NDWI', label: 'NDWI' },
    { value: 'SAVI', label: 'SAVI' },
    { value: 'EVI', label: 'EVI' },
    { value: 'CIR', label: 'CIR' },
    { value: 'NBR', label: 'NBR' },
    { value: 'NDMI', label: 'NDMI' },
  ];

  const collectionOptions = [
    { value: '', label: 'Todas as coleções' },
    { value: 'cbers4a', label: 'CBERS-4A' },
    { value: 'sentinel2', label: 'Sentinel-2' },
    { value: 'landsat8', label: 'Landsat 8' },
    { value: 'landsat9', label: 'Landsat 9' },
  ];

  $effect(() => {
    dashboardState.selectedProduct;
    dashboardState.selectedCollection;
    loadAnalyses();
  });
</script>

<div class="min-h-screen bg-background">
  <header class="sticky top-0 z-30 bg-background/55 backdrop-blur-xl border-b border-border px-6 py-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="sm" onclick={() => goto('/')}>
          ← Mapa
        </Button>
        <h1 class="text-lg font-bold text-primary">Dashboard</h1>
        <Badge variant="secondary">{dashboardState.total} análises</Badge>
      </div>
      <div class="flex items-center gap-3">
        <Select bind:value={dashboardState.selectedProduct} options={productOptions} />
        <Select bind:value={dashboardState.selectedCollection} options={collectionOptions} />
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-6 py-6 space-y-6">
    {#if dashboardState.isLoading}
      <div class="flex justify-center py-16">
        <Spinner size="lg" />
      </div>
    {:else if dashboardState.analyses.length === 0}
      <EmptyState
        title="Nenhuma análise salva"
        description="Processe uma imagem no mapa para começar a construir seu dashboard."
      >
        {#snippet action()}
          <Button onclick={() => goto('/')}>Ir para o Mapa</Button>
        {/snippet}
      </EmptyState>
    {:else}
      <SummaryStats
        analyses={dashboardState.analyses}
        total={dashboardState.total}
      />

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each dashboardState.analyses as analysis (analysis.id)}
          <AnalysisCard {analysis} onDelete={() => deleteAnalysis(analysis.id)} />
        {/each}
      </div>
    {/if}
  </main>
</div>
