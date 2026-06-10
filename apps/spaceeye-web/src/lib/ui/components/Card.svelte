<script lang="ts">
  type Variant = 'surface' | 'glass' | 'outlined' | 'ghost';

  let {
    variant = 'surface' as Variant,
    interactive = false,
    padding = true,
    href = undefined as string | undefined,
    onclick = undefined as ((e: MouseEvent) => void) | undefined,
    header,
    children,
    footer,
    class: className = '',
  }: {
    variant?: Variant;
    interactive?: boolean;
    padding?: boolean;
    href?: string;
    onclick?: (e: MouseEvent) => void;
    header?: import('svelte').Snippet;
    children?: import('svelte').Snippet;
    footer?: import('svelte').Snippet;
    class?: string;
  } = $props();

  const vars: Record<Variant, string> = {
    surface: 'bg-card text-card-foreground shadow-sm border border-border',
    glass: 'bg-[--glass-surface,rgba(0,0,0,0.4)] text-card-foreground border border-[--glass-border,rgba(255,255,255,0.08)] backdrop-blur',
    outlined: 'bg-transparent border border-border',
    ghost: 'bg-transparent',
  };
</script>

{#if href}
  <a
    {href}
    class="block rounded-[--radius,0.625rem] transition-all duration-[--duration-snappy,150ms]
           {vars[variant]} {padding ? 'p-[--radius,0.625rem]' : ''}
           {interactive ? 'hover:shadow-md hover:-translate-y-0.5' : ''}
           {className}"
  >
    {#if header}<div class="mb-2">{@render header()}</div>{/if}
    {#if children}<div>{@render children()}</div>{/if}
    {#if footer}<div class="mt-2 pt-2 border-t border-border">{@render footer()}</div>{/if}
  </a>
{:else}
  <div
    class="rounded-[--radius,0.625rem] transition-all duration-[--duration-snappy,150ms]
           {vars[variant]} {padding ? 'p-[--radius,0.625rem]' : ''}
           {interactive ? 'cursor-pointer hover:shadow-md hover:-translate-y-0.5' : ''}
           {className}"
    role={interactive ? 'button' : undefined}
    tabindex={interactive ? 0 : undefined}
    onclick={interactive ? onclick : undefined}
    onkeydown={interactive ? (e: KeyboardEvent) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onclick?.(e as any); } } : undefined}
  >
    {#if header}<div class="mb-2">{@render header()}</div>{/if}
    {#if children}<div>{@render children()}</div>{/if}
    {#if footer}<div class="mt-2 pt-2 border-t border-border">{@render footer()}</div>{/if}
  </div>
{/if}
