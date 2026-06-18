<script lang="ts">
  let { size = 'sm', class: className = '' }: { size?: 'xs' | 'sm' | 'md' | 'lg'; class?: string } = $props();
  
  const sizeClasses = {
    xs: 'h-3 w-3 border-[1.5px]',
    sm: 'h-4 w-4 border-2',
    md: 'h-6 w-6 border-2',
    lg: 'h-8 w-8 border-[3px]',
  };
</script>

<span class="animate-spin rounded-full border-current border-t-transparent {sizeClasses[size]} {className}" role="status" aria-label="Loading"></span>
