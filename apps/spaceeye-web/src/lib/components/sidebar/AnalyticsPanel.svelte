<script lang="ts">
  import WeatherPanel from '$lib/components/WeatherPanel.svelte';
  import SoilPanel from '$lib/components/SoilPanel.svelte';
  import LandCoverPanel from '$lib/components/LandCoverPanel.svelte';
  import { mapState } from '$lib/stores/map.svelte';
  import SidebarSection from './SidebarSection.svelte';

  let activeTab = $state<'weather' | 'soil' | 'landcover'>('weather');
  const tabs = [
    { id: 'weather' as const, label: 'Climate' },
    { id: 'soil' as const, label: 'Soil' },
    { id: 'landcover' as const, label: 'Land Cover' },
  ];

  let centroid = $derived(mapState.polygonCentroid ?? { lat: 0, lon: 0 });
</script>

<SidebarSection title="Analytics" icon="📊">
  <div class="space-y-2">
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

    {#if activeTab === 'weather'}
      <WeatherPanel lat={centroid.lat} lon={centroid.lon} />
    {:else if activeTab === 'soil'}
      <SoilPanel lat={centroid.lat} lon={centroid.lon} polygonCoords={mapState.polygonCoords} />
    {:else}
      <LandCoverPanel lat={centroid.lat} lon={centroid.lon} polygonCoords={mapState.polygonCoords} />
    {/if}
  </div>
</SidebarSection>
