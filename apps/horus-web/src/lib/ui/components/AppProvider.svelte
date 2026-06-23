<script lang="ts">
  import { Toaster } from 'svelte-sonner';

  let {
    toasterPosition = 'bottom-right' as 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right',
    toasterDuration = 4000,
    toasterVisibleToasts = 5,
    children,
  }: {
    toasterPosition?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
    toasterDuration?: number;
    toasterVisibleToasts?: number;
    children?: import('svelte').Snippet;
  } = $props();
</script>

<Toaster
  richColors
  closeButton
  position={toasterPosition}
  duration={toasterDuration}
  visibleToasts={toasterVisibleToasts}
/>
{@render children?.()}
