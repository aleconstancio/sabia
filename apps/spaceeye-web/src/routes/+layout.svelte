<script lang="ts">
  import '../app.css';
  import AppProvider from '$lib/ui/components/AppProvider.svelte';
  import ErrorBoundary from '$lib/ui/components/ErrorBoundary.svelte';
  let { children } = $props();
</script>

<AppProvider>
  <ErrorBoundary>
    {@render children()}
  </ErrorBoundary>
</AppProvider>
