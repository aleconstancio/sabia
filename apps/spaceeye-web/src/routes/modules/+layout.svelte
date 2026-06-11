<script lang="ts">
  import { page } from '$app/stores';
  import Header from '$lib/layout/Header.svelte';

  let { children } = $props();

  let activeModule = $derived($page.url.pathname.split('/')[2] || 'vegetation');

  const modules = [
    { id: 'vegetation', label: 'Vegetation', icon: '🌿' },
    { id: 'water', label: 'Water', icon: '💧' },
    { id: 'fire', label: 'Fire', icon: '🔥' },
    { id: 'soil', label: 'Soil', icon: '🌱' },
    { id: 'climate', label: 'Climate', icon: '🌡' },
  ];
</script>

<div class="flex flex-col h-full">
  <Header />
  {@render children()}
</div>
