<script lang="ts">
  import { Button as BitsButton } from 'bits-ui';

  type Variant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  type Size = 'sm' | 'md' | 'lg';

  let {
    variant = 'primary' as Variant,
    size = 'md' as Size,
    fullWidth = false,
    disabled = false,
    loading = false,
    type = 'button' as string,
    href = undefined as string | undefined,
    onclick = undefined as ((e: MouseEvent) => void) | undefined,
    children,
  }: {
    variant?: Variant;
    size?: Size;
    fullWidth?: boolean;
    disabled?: boolean;
    loading?: boolean;
    type?: string;
    href?: string;
    onclick?: (e: MouseEvent) => void;
    children?: import('svelte').Snippet;
  } = $props();

  const vars: Record<Variant, string> = {
    primary: 'bg-primary text-primary-foreground hover:opacity-90',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    outline: 'border border-border bg-transparent hover:bg-accent',
    ghost: 'bg-transparent hover:bg-accent',
    destructive: 'bg-destructive text-destructive-foreground hover:opacity-90',
  };

  const sz: Record<Size, string> = {
    sm: 'h-8 px-3 text-xs gap-1.5',
    md: 'h-10 px-4 text-sm gap-2',
    lg: 'h-12 px-6 text-base gap-2.5',
  };
</script>

{#if href}
  <a
    {href}
    class="inline-flex items-center justify-center rounded-[--radius,0.625rem] font-medium
           transition-all duration-[--duration-snappy,150ms]
           disabled:pointer-events-none disabled:opacity-50
           {vars[variant]} {sz[size]}"
    class:w-full={fullWidth}
    data-loading={loading || undefined}
  >
    {#if loading}
      <span class="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
    {/if}
    {@render children?.()}
  </a>
{:else}
  <BitsButton.Root
    {type}
    {disabled}
    onclick={loading ? undefined : onclick}
    class="inline-flex items-center justify-center rounded-[--radius,0.625rem] font-medium
           transition-all duration-[--duration-snappy,150ms] cursor-pointer
           disabled:pointer-events-none disabled:opacity-50
           {vars[variant]} {sz[size]} {fullWidth ? 'w-full' : ''}"
    data-loading={loading || undefined}
  >
    {#if loading}
      <span class="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
    {/if}
    {@render children?.()}
  </BitsButton.Root>
{/if}
