<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import L from 'leaflet';
  import type { ImageResult } from '$lib/api/types';

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

  onMount(() => {
    map = L.map(container, {
      center: [polygonCentroid?.lat ?? -3.35, polygonCentroid?.lon ?? -23.21],
      zoom: 14, zoomControl: false, attributionControl: false,
      layers: [L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 })],
    });
  });

  async function processImage(image: ImageResult, side: 'A' | 'B') {
    if (!image || !polygonCoords) return;
    loading = true;
    try {
      const resp = await fetch(`${API_URL}/process`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_id: image.id, coordinates: polygonCoords, product }),
      });
      if (!resp.ok) throw new Error('Process request failed');
      const data = await resp.json();
      let remaining = 120;
      const poll = setInterval(async () => {
        if (--remaining <= 0) {
          clearInterval(poll); loading = false;
          swipeError = 'Timeout';
          return;
        }
        try {
          const sr = await fetch(`${API_URL}/tasks/${data.task_id}`);
          const status = await sr.json();
          if (status.status === 'done') {
            clearInterval(poll);
            const b = status.result?.bounds as [[number, number], [number, number]];
            bounds = b;
            const url = `${API_URL}/overlay/${status.result.path.split('/').pop()}`;
            if (side === 'A') { urlA = url; }
            else { urlB = url; }
            loading = false;
          } else if (status.status === 'error') {
            clearInterval(poll); loading = false;
            swipeError = status.error || 'Erro';
          }
        } catch { console.warn('SwipeComparison poll error for side:', side); clearInterval(poll); loading = false; swipeError = 'Falha na conexão'; }
      }, 1000);
    } catch {
      console.warn('SwipeComparison processImage error');
      loading = false; swipeError = 'Falha ao iniciar processamento'; }
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
      overlayB.getContainer().style.clipPath = `inset(0 50% 0 0)`;
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
    overlayB.getContainer().style.clipPath = `inset(0 ${100 - swipePos}% 0 0)`;
  }
  function handleEnd() { dragging = false; }
</script>

<div
  bind:this={container}
  class="relative w-full h-[400px] rounded-lg overflow-hidden border border-border"
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
      {imageA?.id?.slice(0, 20)}... {new Date(imageA?.acquired_at).toLocaleDateString('pt-BR')}
    </div>
    <div class="absolute top-2 right-2 z-[1001] bg-black/60 text-white text-xs px-2 py-1 rounded">
      {imageB?.id?.slice(0, 20)}... {new Date(imageB?.acquired_at).toLocaleDateString('pt-BR')}
    </div>
  {/if}
</div>
