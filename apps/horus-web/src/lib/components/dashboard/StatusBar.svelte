<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { dashboardState } from '$lib/stores/dashboard.svelte';
  import { alertStore } from '$lib/stores/alerts.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Badge } from '$lib/components/ui/badge';
  import { Spinner } from '$lib/components/ui/spinner';

  let lastUpdated = $state(Date.now());
  let elapsed = $state(0);
  let intervalId: ReturnType<typeof setInterval> | undefined;
  let refreshSpinning = $state(false);
  let _wasLoading = $state(false);

  let alertCount = $derived(alertStore.alerts.length);

  let timeAgo = $derived.by(() => {
    const secs = Math.floor(elapsed / 1000);
    if (secs < 60) return `${secs}s ago`;
    if (secs < 3600) return `${Math.floor(secs / 60)}m ago`;
    return `${Math.floor(secs / 3600)}h ago`;
  });

  $effect(() => {
    const isLoading = dashboardState.isLoading;
    if (_wasLoading && !isLoading) {
      lastUpdated = Date.now();
      elapsed = 0;
    }
    _wasLoading = isLoading;
  });

  onMount(() => {
    intervalId = setInterval(() => {
      elapsed = Date.now() - lastUpdated;
    }, 1000);
  });

  onDestroy(() => {
    if (intervalId) clearInterval(intervalId);
  });

  async function handleRefresh() {
    refreshSpinning = true;
    await dashboardState.loadProfiles();
    refreshSpinning = false;
  }
</script>

<div class="h-9 bg-card/80 backdrop-blur-sm border-b border-border flex items-center px-4 gap-3 text-xs shrink-0">
  <div class="flex items-center gap-2">
    <span class="font-bold text-primary">Horus</span>
    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
  </div>

  <div class="w-px h-4 bg-border"></div>

  <div class="flex items-center gap-2 text-muted-foreground">
    {#if dashboardState.isLoading}
      <Spinner size="xs" />
    {/if}
    <span class="font-mono" aria-live="polite">Updated {timeAgo}</span>
  </div>

  <div class="ml-auto flex items-center gap-2">
    <button
      class="flex items-center gap-1 px-2 py-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
    >
      <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
        <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
      </svg>
      {#if alertCount > 0}
        <Badge variant="destructive" class="h-4 min-w-4 px-1 text-[9px]">{alertCount}</Badge>
      {:else}
        <span class="text-[10px]">{alertCount}</span>
      {/if}
    </button>

    <div class="w-px h-4 bg-border"></div>

    <Button variant="ghost" size="xs" onclick={() => goto('/map')}>
      <svg class="w-3 h-3 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
      </svg>
      New Search
    </Button>

    <Button variant="ghost" size="xs" onclick={handleRefresh}>
      <svg class="w-3 h-3 mr-1 {refreshSpinning ? 'animate-spin' : ''}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
        <path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
        <path d="M16 16h5v5"/>
      </svg>
      Refresh
    </Button>
  </div>
</div>
