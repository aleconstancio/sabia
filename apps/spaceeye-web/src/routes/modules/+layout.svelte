<script lang="ts">
  import Header from '$lib/layout/Header.svelte';

  let { children } = $props();
</script>

<div class="flex flex-col h-full">
  <Header />
  {@render children()}
</div>
