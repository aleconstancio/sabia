<script lang="ts">
  import '$lib/components/sidebar/sidebar.css';
  import HistoryPanel from '$lib/components/HistoryPanel.svelte';
  import { restorePolygonOnMap } from '$lib/utils/map-helpers';
  import { mapState } from '$lib/stores/map.svelte.ts';

  let expanded = $state(true);

  async function handleRestore(r: any) {
    if (r?.polygonCoords) {
      mapState.polygonCoords = r.polygonCoords;
      await restorePolygonOnMap(r.polygonCoords);
      mapState.showPolygonModal = true;
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

