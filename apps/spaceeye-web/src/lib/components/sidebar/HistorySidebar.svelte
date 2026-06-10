<script lang="ts">
  import HistoryPanel from '$lib/components/HistoryPanel.svelte';
  import { restorePolygonOnMap } from '$lib/utils/map-helpers';
  import { mapState } from '$lib/stores/map.svelte.ts';
  import type { AnalysisRecord } from '$lib/api/types';

  let expanded = $state(true);

  async function handleRestore(r: AnalysisRecord) {
    if (r?.polygonCoords) {
      mapState.polygonCoords = r.polygonCoords;
      await restorePolygonOnMap(r.polygonCoords);
      mapState.showPolygonModal = true;
    }
  }
</script>

<div class="mb-4 sidebar-section">
  <button onclick={() => expanded = !expanded} class="flex items-center w-full p-2 rounded-[--radius] cursor-pointer transition-colors bg-transparent border-none text-inherit hover:bg-muted sidebar-section-header" aria-expanded={expanded} aria-label="Historico">
    <span class="text-lg mr-2">📁</span>
    <span class="text-xs font-bold uppercase tracking-wider text-muted-foreground">Histórico</span>
    <svg class="ml-auto w-3 h-3 transition-transform" class:rotate-180={expanded} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
  </button>
  {#if expanded}
    <div class="mt-2">
      <HistoryPanel onRestore={handleRestore} />
    </div>
  {/if}
</div>
