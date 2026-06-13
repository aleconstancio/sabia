<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import L from 'leaflet';
  import type { ImageResult } from '$lib/api/types';
  import { processImage as apiProcessImage } from '$lib/api/client';
  import { pollTaskStatus } from '$lib/helpers/pollTask';

  let {
    imageA = null as ImageResult | null,
    imageB = null as ImageResult | null,
    polygonCoords = null as number[][][] | null,
    polygonCentroid = null as { lat: number; lon: number } | null,
    product = 'NDVI',
  } = $props();

  let container: HTMLDivElement;
  let map: L.Map;
  let overlayA: L.ImageOverlay | null = null;
  let overlayB: L.ImageOverlay | null = null;
  let swipePos = $state(50);
  let dragging = $state(false);
  let loading = $state(false);
  let urlA = $state('');
  let urlB = $state('');
  let bounds: [[number, number], [number, number]] | null = null;
  import { API_URL } from '$lib/config';

  let swipeError = $state('');
  let pendingCount = $state(0);

  onMount(() => {
    map = L.map(container, {
      center: [polygonCentroid?.lat ?? -3.35, polygonCentroid?.lon ?? -23.21],
      zoom: 14, zoomControl: false, attributionControl: false,
      layers: [L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 })],
    });
  });

  async function processImage(image: ImageResult, side: 'A' | 'B') {
    if (!image || !polygonCoords) return;
    pendingCount++;
    loading = true;
    try {
      const data = await apiProcessImage(image.id, polygonCoords, product);
      const result = await pollTaskStatus(data.task_id, { intervalMs: 1000 });
      pendingCount--;
      if (pendingCount === 0) loading = false;
      if (result.status === 'done') {
        const b = result.result?.bounds as [[number, number], [number, number]];
        if (side === 'A' && imageA?.id === image.id) {
          bounds = b;
          urlA = `${API_URL}/overlay/${(result.result?.path as string).split('/').pop()}`;
        } else if (side === 'B' && imageB?.id === image.id) {
          bounds = b;
          urlB = `${API_URL}/overlay/${(result.result?.path as string).split('/').pop()}`;
        }
      } else {
        swipeError = result.error || 'Erro';
      }
    } catch {
      pendingCount--;
      if (pendingCount === 0) loading = false;
      console.warn('SwipeComparison processImage error');
      swipeError = 'Falha ao iniciar processamento';
    }
  }

  $effect(() => {
    if (imageA) processImage(imageA, 'A');
    if (imageB) processImage(imageB, 'B');
  });

  $effect(() => {
    if (map && urlA && urlB && bounds) {
      if (overlayA) map.removeLayer(overlayA);
      if (overlayB) map.removeLayer(overlayB);
      overlayA = L.imageOverlay(urlA, bounds, { opacity: 1 }).addTo(map);
      overlayB = L.imageOverlay(urlB, bounds, { opacity: 1 }).addTo(map);
      (overlayB as any).getContainer().style.clipPath = `inset(0 50% 0 0)`;
      map.flyToBounds(bounds, { duration: 1 });
    }
  });

  onDestroy(() => { if (map) map.remove(); });

  function handleStart(e: MouseEvent | TouchEvent) { dragging = true; e.preventDefault(); }
  function handleMove(e: MouseEvent | TouchEvent) {
    if (!dragging || !container || !overlayB) return;
    const rect = container.getBoundingClientRect();
    const x = (e.type.startsWith('touch') ? (e as TouchEvent).touches[0].clientX : (e as MouseEvent).clientX) - rect.left;
    swipePos = Math.max(0, Math.min(100, (x / rect.width) * 100));
    (overlayB as any).getContainer().style.clipPath = `inset(0 ${100 - swipePos}% 0 0)`;
  }
  function handleEnd() { dragging = false; }
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div
  bind:this={container}
  class="relative w-full h-[400px] rounded-lg overflow-hidden border border-border"
  role="application"
  aria-label="Comparação de imagens"
  onmousedown={handleStart}
  onmousemove={handleMove}
  onmouseup={handleEnd}
  onmouseleave={handleEnd}
  ontouchstart={handleStart}
  ontouchmove={handleMove}
  ontouchend={handleEnd}
>
  {#if loading}
    <div class="absolute inset-0 bg-black/40 flex items-center justify-center z-[1002]">
      <span class="text-white text-sm">Processando...</span>
    </div>
  {/if}
  {#if swipeError}
    <div class="absolute bottom-2 left-1/2 -translate-x-1/2 z-[1002] bg-destructive/90 text-white text-xs px-2 py-1 rounded">{swipeError}</div>
  {/if}
  {#if urlA && urlB}
    <div
      class="absolute top-0 bottom-0 z-[1001] w-1 bg-white cursor-col-resize shadow-lg"
      style="left: {swipePos}%; transform: translateX(-50%)"
    >
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-md flex items-center justify-center text-sm font-bold text-gray-600">↔</div>
    </div>
    <div class="absolute top-2 left-2 z-[1001] bg-black/60 text-white text-xs px-2 py-1 rounded">
      {imageA?.id?.slice(0, 20)}... {new Date(imageA?.acquired_at ?? Date.now()).toLocaleDateString('pt-BR')}
    </div>
    <div class="absolute top-2 right-2 z-[1001] bg-black/60 text-white text-xs px-2 py-1 rounded">
      {imageB?.id?.slice(0, 20)}... {new Date(imageB?.acquired_at ?? Date.now()).toLocaleDateString('pt-BR')}
    </div>
  {/if}
</div>
