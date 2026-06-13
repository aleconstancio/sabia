<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { alertStore } from '$lib/stores/alerts.svelte';

  let showPanel = $state(false);
  let panelRef: HTMLDivElement;

  function handleClickOutside(e: MouseEvent) {
    if (panelRef && !panelRef.contains(e.target as Node)) {
      showPanel = false;
    }
  }

  onMount(() => document.addEventListener('mousedown', handleClickOutside));
  onDestroy(() => document.removeEventListener('mousedown', handleClickOutside));
</script>

<div class="relative" bind:this={panelRef}>
  <button
    onclick={() => showPanel = !showPanel}
    class="relative inline-flex items-center justify-center rounded-[--radius] p-2 transition-colors cursor-pointer bg-transparent border-none text-muted-foreground"
    aria-label="Notifications"
  >
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
    {#if alertStore.unreadCount > 0}
      <span class="absolute -top-0.5 -right-0.5 w-4 h-4 bg-destructive text-destructive-foreground text-[9px] font-bold rounded-full flex items-center justify-center">
        {alertStore.unreadCount}
      </span>
    {/if}
  </button>

  {#if showPanel}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="absolute top-full right-0 mt-1 w-80 rounded-lg border border-border bg-card shadow-lg z-[1000] max-h-96 overflow-y-auto">
      <div class="flex items-center justify-between px-3 py-2 border-b border-border">
        <h4 class="text-xs font-semibold text-muted-foreground uppercase">Alerts</h4>
        {#if alertStore.unreadCount > 0}
          <button class="text-xs text-primary bg-transparent border-none cursor-pointer hover:underline" onclick={() => alertStore.markAllRead()}>
            Mark all read
          </button>
        {/if}
      </div>
      {#if alertStore.alerts.length === 0}
        <p class="text-xs text-muted-foreground p-4 text-center">No alerts yet</p>
      {:else}
        {#each alertStore.alerts as alert}
          <button
            class="w-full text-left px-3 py-2 hover:bg-muted transition-colors cursor-pointer bg-transparent border-none"
            class:bg-muted={!alert.read}
            onclick={() => alertStore.markRead(alert.id)}
          >
            <div class="flex items-start gap-2">
              <div class="w-2 h-2 rounded-full mt-1.5 shrink-0" class:bg-destructive={!alert.read} class:bg-muted-foreground={alert.read}></div>
              <div class="min-w-0">
                <p class="text-xs font-medium truncate">{alert.message}</p>
                <p class="text-[10px] text-muted-foreground">{alert.region} · {new Date(alert.timestamp).toLocaleString('pt-BR')}</p>
              </div>
            </div>
          </button>
        {/each}
      {/if}
    </div>
  {/if}
</div>
