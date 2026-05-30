<script lang="ts">
  import { Dialog as BitsDialog } from 'bits-ui';

  let {
    open = $bindable(false),
    title = undefined as string | undefined,
    icon,
    children,
    actions,
  }: {
    open?: boolean;
    title?: string;
    icon?: import('svelte').Snippet;
    children?: import('svelte').Snippet;
    actions?: import('svelte').Snippet;
  } = $props();
</script>

<BitsDialog.Root bind:open>
  <BitsDialog.Portal>
    <BitsDialog.Overlay
      class="fixed inset-0 z-[--z-overlay,30] bg-black/50 backdrop-blur-sm
             data-[state=open]:animate-in data-[state=closed]:animate-out
             data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0"
    />
    <BitsDialog.Content
      class="fixed left-1/2 top-1/2 z-[--z-overlay,30] w-full max-w-md -translate-x-1/2 -translate-y-1/2
             rounded-[--radius,0.625rem] bg-card text-card-foreground border border-border p-6 shadow-lg
             data-[state=open]:animate-in data-[state=closed]:animate-out
             data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0
             data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95
             data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-48
             data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-48
             duration-[--duration-slow,400ms] contain-layout"
    >
      {#if icon}
        <div class="mb-4 text-primary">
          {@render icon()}
        </div>
      {/if}

      {#if title}
        <h2 class="text-lg font-semibold mb-4">{title}</h2>
      {/if}

      {#if children}
        <div class="text-sm text-muted-foreground">
          {@render children()}
        </div>
      {/if}

      {#if actions}
        <div class="mt-6 flex justify-end gap-3">
          {@render actions()}
        </div>
      {/if}
    </BitsDialog.Content>
  </BitsDialog.Portal>
</BitsDialog.Root>
