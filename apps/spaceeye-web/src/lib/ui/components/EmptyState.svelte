<script lang="ts">
  let {
    icon,
    title = undefined as string | undefined,
    description = undefined as string | undefined,
    action,
  }: {
    icon?: import('svelte').Snippet;
    title?: string;
    description?: string;
    action?: import('svelte').Snippet;
  } = $props();
</script>

<div class="flex flex-col items-center justify-center py-16 text-center">
  {#if icon}
    <div class="mb-4 text-muted-foreground/50">
      {@render icon()}
    </div>
  {/if}

  {#if title}
    <h3 class="text-lg font-semibold text-foreground mb-1">{title}</h3>
  {/if}

  {#if description}
    <p class="text-sm text-muted-foreground max-w-sm">{description}</p>
  {/if}

  {#if action}
    <div class="mt-4">
      {@render action()}
    </div>
  {/if}
</div>
