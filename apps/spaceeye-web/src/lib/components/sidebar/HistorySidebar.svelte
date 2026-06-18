<script lang="ts">
  import HistoryPanel from '$lib/components/HistoryPanel.svelte';
  import { restorePolygonOnMap } from '$lib/helpers/map-helpers';
  import { mapState } from '$lib/stores/map.svelte';
  import type { AnalysisRecord } from '$lib/api/types';
  import SidebarSection from './SidebarSection.svelte';

  async function handleRestore(r: AnalysisRecord) {
    if (r?.polygonCoords) {
      mapState.polygonCoords = r.polygonCoords;
      await restorePolygonOnMap(r.polygonCoords);
      mapState.showPolygonModal = true;
    }
  }
</script>

<SidebarSection title="History" icon="📁">
  <HistoryPanel onRestore={handleRestore} />
</SidebarSection>
