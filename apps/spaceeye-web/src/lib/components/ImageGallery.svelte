<script lang="ts">
  import Badge from '$lib/ui/components/Badge.svelte';

  let {
    images = [] as any[],
    selectedProduct = 'NDVI',
    processImage = (imageId: string) => {}
  }: {
    images: any[];
    selectedProduct: string;
    processImage: (imageId: string) => void;
  } = $props();
</script>

<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-h-[60vh] overflow-y-auto p-2">
  {#each images as img}
    <button
      class="rounded-lg border border-border bg-card p-3 text-left transition-all hover:border-primary hover:shadow-md cursor-pointer"
      onclick={() => processImage(img.id)}
    >
      {#if img.thumbnail_url}
        <img src={img.thumbnail_url} alt={img.id} class="w-full h-40 object-cover rounded-md mb-2" loading="lazy" />
      {:else}
        <div class="w-full h-40 bg-muted rounded-md mb-2 flex items-center justify-center text-muted-foreground text-sm">
          Sem thumbnail
        </div>
      {/if}
      <p class="font-mono text-xs truncate mb-1">{img.id}</p>
      <div class="flex items-center justify-between">
        <Badge variant={img.cloud_cover < 20 ? 'success' : img.cloud_cover < 50 ? 'warning' : 'destructive'}>
          {img.cloud_cover?.toFixed(1)}% nuvem
        </Badge>
        <span class="text-xs text-muted-foreground">
          {new Date(img.acquired_at).toLocaleDateString('pt-BR')}
        </span>
      </div>
    </button>
  {/each}
</div>
