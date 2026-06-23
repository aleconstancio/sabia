<script lang="ts">
  import { page } from '$app/state';
</script>

<div class="flex flex-col items-center justify-center min-h-[60vh] p-8 text-center">
  <h1 class="text-4xl font-bold text-foreground mb-4">{page.status}</h1>
  <p class="text-muted-foreground mb-6 max-w-md">
    {page.error?.message || 'An unexpected error occurred.'}
  </p>
  <a
    href="/"
    class="inline-flex items-center justify-center rounded-[--radius,0.625rem] font-medium transition-all bg-primary text-primary-foreground hover:opacity-90 h-10 px-4 text-sm"
  >
    Back to home
  </a>
</div>
