<script lang="ts">
  import HistoryPanel from '$lib/components/HistoryPanel.svelte';
  import { mapState } from '$lib/stores/map.svelte.ts';

  let expanded = $state(true);

  function handleRestore(r: any) {
    if (mapState.map && r.polygonCoords) {
      mapState.polygonCoords = r.polygonCoords;
      import('leaflet').then(L => {
        const polygon = L.default.polygon(r.polygonCoords[0].map((c: number[]) => [c[1], c[0]]));
        (mapState.map as any).addLayer(polygon);
        (mapState.map as any).fitBounds(polygon.getBounds());
        mapState.polygonCentroid = r.centroid;
        mapState.showPolygonModal = true;
      });
    }
  }
</script>

<div class="sidebar-section">
  <button onclick={() => expanded = !expanded} class="sidebar-section-header">
    <span class="text-lg mr-2">📁</span>
    <span class="text-xs font-bold uppercase tracking-wider" style="color: var(--muted-foreground);">Histórico</span>
    <svg class="ml-auto w-3 h-3 transition-transform" class:rotate-180={expanded} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
  </button>
  {#if expanded}
    <div class="mt-2">
      <HistoryPanel onRestore={handleRestore} />
    </div>
  {/if}
</div>

<style>
  .sidebar-section { margin-bottom: 1rem; }
  .sidebar-section-header {
    display: flex; align-items: center; width: 100%;
    padding: 0.5rem; border-radius: var(--radius);
    cursor: pointer; transition: background 150ms;
    background: transparent; border: none; color: inherit;
  }
  .sidebar-section-header:hover { background: var(--muted); }
</style>
