<script lang="ts">
  import type { ImageResult } from '$lib/api/types';

  let {
    images = [] as ImageResult[],
    onSelect = (imageId: string) => {}
  }: {
    images: ImageResult[];
    onSelect: (imageId: string) => void;
  } = $props();

  let currentIndex = $state(0);
  let current = $derived(images[currentIndex] || null);
</script>

{#if images.length > 0}
  <div class="rounded-lg border border-border bg-card p-3">
    <div class="flex items-center justify-between mb-2">
      <p class="text-xs text-muted-foreground">Linha do tempo</p>
      <p class="text-xs font-mono">{currentIndex + 1} / {images.length}</p>
    </div>
    <input
      type="range"
      min="0"
      max={Math.max(0, images.length - 1)}
      bind:value={currentIndex}
      class="w-full accent-emerald-500"
      onchange={() => current && onSelect(current.id)}
    />
    {#if current}
      <div class="flex items-center justify-between mt-2">
        <div class="flex items-center gap-2">
          <span class="text-xs text-muted-foreground">{new Date(current.acquired_at).toLocaleDateString('pt-BR')}</span>
          <span class="text-xs" class:text-emerald-400={(current.cloud_cover ?? 100) < 20} class:text-amber-400={(current.cloud_cover ?? 100) >= 20 && (current.cloud_cover ?? 100) < 50} class:text-red-400={(current.cloud_cover ?? 100) >= 50}>
            {current.cloud_cover?.toFixed(0) ?? '—'}%
          </span>
        </div>
        <button
          class="text-xs text-primary hover:underline cursor-pointer bg-transparent border-none"
          onclick={() => onSelect(current.id)}
        >
          Processar
        </button>
      </div>
    {/if}
  </div>
{/if}
