<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import AppProvider from '$lib/ui/components/AppProvider.svelte';
  import ErrorBoundary from '$lib/ui/components/ErrorBoundary.svelte';
  let { children } = $props();

  function handleKeydown(e: KeyboardEvent) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      goto('/map');
    }
  }

  onMount(() => {
    document.addEventListener('keydown', handleKeydown);
    return () => document.removeEventListener('keydown', handleKeydown);
  });
</script>

<AppProvider>
  <ErrorBoundary>
    {@render children()}
  </ErrorBoundary>
</AppProvider>
