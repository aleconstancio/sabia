<script lang="ts">
  let ModuleMapPage = $state<any>(null);

  $effect(() => {
    import('$lib/components/modules/ModuleMapPage.svelte').then(mod => {
      ModuleMapPage = mod.default;
    });
  });
</script>

{#if ModuleMapPage}
  <ModuleMapPage module="water" product="NDWI" />
{/if}
