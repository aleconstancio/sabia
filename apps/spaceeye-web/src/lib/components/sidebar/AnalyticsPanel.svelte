<script lang="ts">
  import WeatherPanel from '$lib/components/WeatherPanel.svelte';
  import SoilPanel from '$lib/components/SoilPanel.svelte';
  import LandCoverPanel from '$lib/components/LandCoverPanel.svelte';
  import { mapState } from '$lib/stores/map.svelte';

  let expanded = $state(true);
  let activeTab = $state<'weather' | 'soil' | 'landcover'>('weather');
  let tabs = [
    { id: 'weather' as const, label: 'Clima' },
    { id: 'soil' as const, label: 'Solo' },
    { id: 'landcover' as const, label: 'Cobertura' },
  ];

  let centroid = $derived(mapState.polygonCentroid ?? { lat: 0, lon: 0 });
</script>

<div class="mb-4 sidebar-section">
  <button onclick={() => expanded = !expanded} class="flex items-center w-full p-2 rounded-[--radius] cursor-pointer transition-colors bg-transparent border-none text-inherit hover:bg-muted sidebar-section-header" aria-expanded={expanded} aria-label="Analises">
    <span class="text-lg mr-2">📊</span>
    <span class="text-xs font-bold uppercase tracking-wider text-muted-foreground">Análises</span>
    <svg class="ml-auto w-3 h-3 transition-transform" class:rotate-180={expanded} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
  </button>
  {#if expanded}
    <div class="mt-2 space-y-2">
      <!-- Tabs -->
      <div class="flex rounded-[--radius] overflow-hidden border border-border">
        {#each tabs as tab}
          <button
            onclick={() => activeTab = tab.id}
            class="flex-1 text-xs py-1.5 px-2 transition-colors cursor-pointer bg-transparent border-none"
            style="background: {activeTab === tab.id ? 'var(--primary)' : 'transparent'}; color: {activeTab === tab.id ? 'var(--primary-foreground)' : 'var(--muted-foreground)'};"
          >
            {tab.label}
          </button>
        {/each}
      </div>

      <!-- Tab content -->
      {#if activeTab === 'weather'}
        <WeatherPanel lat={centroid.lat} lon={centroid.lon} />
      {:else if activeTab === 'soil'}
        <SoilPanel lat={centroid.lat} lon={centroid.lon} polygonCoords={mapState.polygonCoords} />
      {:else}
        <LandCoverPanel lat={centroid.lat} lon={centroid.lon} polygonCoords={mapState.polygonCoords} />
      {/if}
    </div>
  {/if}
</div>
