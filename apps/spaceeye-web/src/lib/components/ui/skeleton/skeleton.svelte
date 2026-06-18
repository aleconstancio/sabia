<script lang="ts">
  let { class: className = '', variant = 'text' }: { class?: string; variant?: 'text' | 'circular' | 'rectangular' | 'card' } = $props();
  
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
    card: 'rounded-xl',
  };
</script>

<div class="animate-pulse bg-muted {variantClasses[variant]} {className}" aria-hidden="true"></div>
