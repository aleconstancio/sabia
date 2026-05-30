<script lang="ts">
  import { Progress as BitsProgress } from 'bits-ui';

  let {
    value = 0,
    max = 100,
    size = 'md' as 'sm' | 'md' | 'lg',
    variant = 'default' as 'default' | 'success' | 'warning' | 'destructive',
  } = $props();

  const heights: Record<string, string> = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const colors: Record<string, string> = {
    default: 'bg-primary',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    destructive: 'bg-destructive',
  };
</script>

<BitsProgress.Root
  {value}
  {max}
  class="w-full rounded-full bg-muted {heights[size]} overflow-hidden"
>
  <BitsProgress.Track
    class="h-full rounded-full transition-all duration-[--duration-fluid] {colors[variant]}"
    style="width: {Math.min(value / max * 100, 100)}%"
  />
</BitsProgress.Root>
