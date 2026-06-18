<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    title,
    icon = '',
    defaultOpen = true,
    header,
    children,
  }: {
    title: string;
    icon?: string;
    defaultOpen?: boolean;
    header?: Snippet;
    children: Snippet;
  } = $props();

  let expanded = $state(defaultOpen);
</script>

<div class="mb-4 sidebar-section">
  <button
    onclick={() => expanded = !expanded}
    class="flex items-center w-full p-2 rounded-[--radius] cursor-pointer transition-colors bg-transparent border-none text-inherit hover:bg-muted sidebar-section-header"
    aria-expanded={expanded}
    aria-label={title}
  >
    <span class="text-lg mr-2">{icon}</span>
    <span class="text-xs font-bold uppercase tracking-wider text-muted-foreground">{title}</span>
    {#if header}
      {@render header()}
    {/if}
    <svg class="ml-auto w-3 h-3 transition-transform" class:rotate-180={expanded} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
  </button>
  {#if expanded}
    <div class="mt-2">
      {@render children()}
    </div>
  {/if}
</div>
