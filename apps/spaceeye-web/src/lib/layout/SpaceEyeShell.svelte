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

<div class="flex h-full w-full bg-background">
  {#if mapState.sidebarOpen}
    <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
    <div
      class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm sm:hidden"
      onclick={() => mapState.sidebarOpen = false}
    ></div>
  {/if}

  <!-- Sidebar -->
  <aside
    class="flex flex-col border-r border-border bg-card shrink-0 transition-all duration-300 contain-layout"
    style="width: {mapState.sidebarOpen ? SIDEBAR_WIDTH_EXPANDED : SIDEBAR_WIDTH_COLLAPSED}; min-width: {mapState.sidebarOpen ? SIDEBAR_WIDTH_EXPANDED : SIDEBAR_WIDTH_COLLAPSED};"
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
  <div class="flex-1 flex flex-col min-w-0 relative bg-background">
    {@render children?.()}
  </div>
</div>

<style>
  @media (max-width: 640px) {
    aside {
      position: absolute !important;
      z-index: 50 !important;
      height: 100% !important;
    }
  }
</style>
