<script lang="ts">
  import { onMount } from 'svelte';
  import Input from '$lib/ui/components/Input.svelte';

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

  const API_URL = import.meta.env.VITE_API_URL || '/api';

  onMount(async () => {
    try {
      const resp = await fetch(`${API_URL}/ibge/uf`);
      ufs = await resp.json();
    } catch (e) {
      console.error('Failed to load UFs', e);
    }
  });

  async function onUfSelect(uf: string) {
    selectedUf = uf;
    ufFilter = uf;
    showUfDropdown = false;
    try {
      const resp = await fetch(`${API_URL}/ibge/cidades/${uf}`);
      cities = await resp.json();
    } catch (e) {
      cities = [];
    }
  }

  async function onCitySelect(city: string) {
    selectedCity = city;
    cityFilter = city;
    showCityDropdown = false;

    try {
      const resp = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${city}-${selectedUf}&limit=1`);
      const data = await resp.json();
      if (data.length > 0) {
        navigateToCity(parseFloat(data[0].lat), parseFloat(data[0].lon));
      }
    } catch (e) {
      console.error('Geocoding failed', e);
    }
  }

  let filteredUfs = $derived(ufs.filter(u => u.toLowerCase().includes(ufFilter.toLowerCase())));
  let filteredCities = $derived(cities.filter(c => c.toLowerCase().includes(cityFilter.toLowerCase())));
</script>

<div class="flex items-center gap-2">
  <div class="relative">
    <Input bind:value={ufFilter} placeholder="UF" class="!w-20" onfocus={() => showUfDropdown = true} />
    {#if showUfDropdown && filteredUfs.length > 0}
      <div class="absolute top-full left-0 z-50 mt-1 max-h-48 overflow-auto rounded border bg-card shadow-lg w-20">
        {#each filteredUfs as uf}
          <button class="w-full px-2 py-1 text-left text-sm hover:bg-muted" onclick={() => onUfSelect(uf)}>{uf}</button>
        {/each}
      </div>
    {/if}
  </div>
  <div class="relative">
    <Input bind:value={cityFilter} placeholder="Cidade" class="!w-48" onfocus={() => showCityDropdown = true} disabled={!selectedUf} />
    {#if showCityDropdown && filteredCities.length > 0}
      <div class="absolute top-full left-0 z-50 mt-1 max-h-48 overflow-auto rounded border bg-card shadow-lg w-48">
        {#each filteredCities as city}
          <button class="w-full px-2 py-1 text-left text-sm hover:bg-muted" onclick={() => onCitySelect(city)}>{city}</button>
        {/each}
      </div>
    {/if}
  </div>
</div>
