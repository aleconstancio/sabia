<script lang="ts">
  import { mapState } from '$lib/stores/map.svelte.ts';

  let {
    sidebarContent,
    children,
  }: {
    sidebarContent?: import('svelte').Snippet;
    children?: import('svelte').Snippet;
  } = $props();

  const SIDEBAR_WIDTH_EXPANDED = '18rem';
  const SIDEBAR_WIDTH_COLLAPSED = '3.5rem';
</script>

<div class="flex h-full w-full" style="background: var(--background);">
  <!-- Sidebar -->
  <aside
    class="flex flex-col border-r shrink-0 transition-all duration-300 contain-layout"
    style="width: {mapState.sidebarOpen ? SIDEBAR_WIDTH_EXPANDED : SIDEBAR_WIDTH_COLLAPSED}; min-width: {mapState.sidebarOpen ? SIDEBAR_WIDTH_EXPANDED : SIDEBAR_WIDTH_COLLAPSED}; background: var(--card); border-color: var(--border);"
  >
    {#if sidebarContent}
      <div
        class="flex-1 overflow-y-auto px-3 py-3"
        class:opacity-0={!mapState.sidebarOpen}
        class:opacity-100={mapState.sidebarOpen}
        style="transition: opacity 200ms; {mapState.sidebarOpen ? '' : 'pointer-events: none;'}"
      >
        {@render sidebarContent()}
      </div>
    {/if}
  </aside>

  <!-- Main content area -->
  <div class="flex-1 flex flex-col min-w-0" style="background: var(--background);">
    {@render children?.()}
  </div>
</div>
