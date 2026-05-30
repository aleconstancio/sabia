<script lang="ts">
  let {
    sidebarContent,
    children,
  }: {
    sidebarContent?: import('svelte').Snippet;
    children?: import('svelte').Snippet;
  } = $props();

  let sidebarOpen = $state(true);

  function toggleSidebar() { sidebarOpen = !sidebarOpen; }

  const SIDEBAR_WIDTH_EXPANDED = '18rem';
  const SIDEBAR_WIDTH_COLLAPSED = '3.5rem';
</script>

<div class="flex h-full w-full" style="background: var(--background);">
  <!-- Sidebar -->
  <aside
    class="flex flex-col border-r shrink-0 overflow-hidden transition-all duration-300 contain-layout"
    style="width: {sidebarOpen ? SIDEBAR_WIDTH_EXPANDED : SIDEBAR_WIDTH_COLLAPSED}; min-width: {sidebarOpen ? SIDEBAR_WIDTH_EXPANDED : SIDEBAR_WIDTH_COLLAPSED}; background: var(--card); border-color: var(--border);"
  >
    {#if sidebarContent}
      <div
        class="flex-1 overflow-y-auto px-3 py-3"
        class:opacity-0={!sidebarOpen}
        class:opacity-100={sidebarOpen}
        style="transition: opacity 200ms; {sidebarOpen ? '' : 'pointer-events: none;'}"
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
