<script lang="ts">
  import * as Select from '$lib/components/ui/select';
  import { Button } from '$lib/components/ui/button';
  import { mapState } from '$lib/stores/map.svelte';
  import { searchImages } from '$lib/api/processing';
  import ProductInfo from '$lib/components/ProductInfo.svelte';
  import { SPECTRAL_PRODUCTS } from '$lib/constants';
  import { Spinner } from '$lib/components/ui/spinner';
  import SidebarSection from './SidebarSection.svelte';
</script>

<SidebarSection title="Search" icon="🔍">
  <div class="space-y-3">
    <div class="text-xs text-muted-foreground">
      Draw a polygon on the map to search for images
    </div>
    <Select.Root type="single" bind:value={mapState.selectedProduct}>
      <Select.Trigger class="w-full">
        Product...
      </Select.Trigger>
      <Select.Content>
        {#each SPECTRAL_PRODUCTS as option}
          <Select.Item value={option.value}>{option.label}</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
    <ProductInfo product={mapState.selectedProduct} />
    {#if mapState.polygonCoords}
        <Button onclick={searchImages} class="!w-full">
          {#if mapState.isLoading}<Spinner size="sm" />{/if}
          Search images
        </Button>
    {/if}
    {#if mapState.searchError}
      <p class="text-xs text-destructive">{mapState.searchError}</p>
    {/if}
  </div>
</SidebarSection>
