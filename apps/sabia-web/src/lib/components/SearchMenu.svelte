<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { getUfs, getCities, geocode } from '$lib/api/client';
  import { clickOutside } from '$lib/actions/clickOutside';
  import { logger } from '$lib/utils/logger';

  let {
    navigateToCity = (lat: number, lng: number) => {}
  }: { navigateToCity?: (lat: number, lng: number) => void } = $props();

  let ufs: string[] = $state([]);
  let cities: string[] = $state([]);
  let selectedUf = $state('');
  let selectedCity = $state('');
  let ufFilter = $state('');
  let cityFilter = $state('');
  let showUfDropdown = $state(false);
  let showCityDropdown = $state(false);

  let apiError = $state('');

  let ufContainer: HTMLDivElement;
  let cityContainer: HTMLDivElement;

  onMount(async () => {
    try {
      ufs = await getUfs();
    } catch {
      logger.warn('SearchMenu failed to load UFs');
      apiError = 'Failed to load states';
    }
  });

  async function onUfSelect(uf: string) {
    selectedUf = uf;
    ufFilter = uf;
    showUfDropdown = false;
    try {
      cities = await getCities(uf);
    } catch {
      logger.warn('SearchMenu failed to load cities for UF:', uf);
      cities = [];
      apiError = 'Failed to load cities';
    }
  }

  async function onCitySelect(city: string) {
    selectedCity = city;
    cityFilter = city;
    showCityDropdown = false;

    try {
      const results = await geocode(`${city}-${selectedUf}`);
      if (results.length > 0) {
        navigateToCity(parseFloat(results[0].lat), parseFloat(results[0].lon));
      }
    } catch {
      logger.warn('SearchMenu geocode failed for city:', city);
      apiError = 'Failed to search location';
    }
  }

  let filteredUfs = $derived(ufs.filter(u => u.toLowerCase().includes(ufFilter.toLowerCase())));
  let filteredCities = $derived(cities.filter(c => c.toLowerCase().includes(cityFilter.toLowerCase())));
</script>

<div class="flex items-center gap-2">
  <div class="relative uf-container" bind:this={ufContainer}>
    <input
      bind:value={ufFilter}
      placeholder="UF"
      class="!w-20 rounded-[--radius,0.625rem] border border-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-ring"
      onfocus={() => showUfDropdown = true}
      aria-label="Search state"
    />
    {#if showUfDropdown && filteredUfs.length > 0}
      <div
        use:clickOutside={{ handler: () => showUfDropdown = false, enabled: showUfDropdown, exclude: [ufContainer] }}
        class="absolute top-full left-0 z-50 mt-1 max-h-48 overflow-auto rounded border bg-card shadow-lg w-20"
      >
        {#each filteredUfs as uf}
          <button class="w-full px-2 py-1 text-left text-sm hover:bg-muted cursor-pointer bg-transparent border-none" onclick={() => onUfSelect(uf)}>{uf}</button>
        {/each}
      </div>
    {/if}
  </div>
  <div class="relative city-container" bind:this={cityContainer}>
    <input
      bind:value={cityFilter}
      placeholder="City"
      class="!w-48 rounded-[--radius,0.625rem] border border-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
      onfocus={() => showCityDropdown = true}
      disabled={!selectedUf}
      aria-label="Search city"
    />
    {#if showCityDropdown && filteredCities.length > 0}
      <div
        use:clickOutside={{ handler: () => showCityDropdown = false, enabled: showCityDropdown, exclude: [cityContainer] }}
        class="absolute top-full left-0 z-50 mt-1 max-h-48 overflow-auto rounded border bg-card shadow-lg w-48"
      >
        {#each filteredCities as city}
          <button class="w-full px-2 py-1 text-left text-sm hover:bg-muted cursor-pointer bg-transparent border-none" onclick={() => onCitySelect(city)}>{city}</button>
        {/each}
      </div>
    {/if}
  </div>
  {#if apiError}
    <span class="text-xs text-destructive">{apiError}</span>
  {/if}
</div>