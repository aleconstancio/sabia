import { mapState } from '$lib/stores/map.svelte';

/**
 * Toggle image selection for comparison mode.
 * Maintains at most 2 selected images and updates comparison state.
 */
export function handleToggleSelect(imageId: string): void {
  const ids = mapState.selectedIds;
  if (ids.includes(imageId)) {
    mapState.selectedIds = ids.filter(id => id !== imageId);
  } else {
    if (ids.length >= 2) {
      mapState.selectedIds = [ids[1], imageId];
    } else {
      mapState.selectedIds = [...ids, imageId];
    }
  }
  if (mapState.selectedIds.length === 2) {
    mapState.comparisonFirst = mapState.results.find(i => i.id === mapState.selectedIds[0]) ?? null;
    mapState.comparisonSecond = mapState.results.find(i => i.id === mapState.selectedIds[1]) ?? null;
  } else {
    mapState.comparisonFirst = null;
    mapState.comparisonSecond = null;
  }
}
