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

  let mapAContainer: HTMLDivElement;
  let mapBContainer: HTMLDivElement;
  let mapA: L.Map;
  let mapB: L.Map;
  let loadingA = $state(false);
  let loadingB = $state(false);
  let overlayA: L.ImageOverlay | null = $state(null);
  let overlayB: L.ImageOverlay | null = $state(null);
  let errorA = $state('');
  let errorB = $state('');
  let taskIdA = $state('');
  let taskIdB = $state('');
  let computingDiff = $state(false);
  let diffOverlay: L.ImageOverlay | null = $state(null);
  import { API_URL } from '$lib/config';

  let diffError = $state('');

  function initMap(container: HTMLDivElement): L.Map {
    const m = L.map(container, {
      center: [polygonCentroid?.lat || 0, polygonCentroid?.lon || 0],
      zoom: 14,
      zoomControl: false,
      attributionControl: false,
      layers: [
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
          maxZoom: 19,
        }),
      ],
    });
    return m;
  }

  $effect(() => {
    if (mapAContainer && !mapA) {
      mapA = initMap(mapAContainer);
    }
    if (mapBContainer && !mapB) {
      mapB = initMap(mapBContainer);
    }
  });

  onDestroy(() => {
    if (mapA) { mapA.remove(); }
    if (mapB) { mapB.remove(); }
    if (overlayA) { overlayA.remove(); overlayA = null; }
    if (overlayB) { overlayB.remove(); overlayB = null; }
  });

  async function processImage(image: ImageResult, side: 'A' | 'B') {
    if (!image || !polygonCoords) return;
    if (side === 'A') { loadingA = true; errorA = ''; }
    else { loadingB = true; errorB = ''; }

    try {
      const resp = await fetch(`${API_URL}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_id: image.id,
          coordinates: polygonCoords,
          product: product,
        }),
      });
      if (!resp.ok) throw new Error('Process request failed');
      const data = await resp.json();

      let remaining = 120;
      const poll = setInterval(async () => {
        if (--remaining <= 0) {
          clearInterval(poll);
          if (side === 'A') { errorA = 'Timeout'; loadingA = false; }
          else { errorB = 'Timeout'; loadingB = false; }
          return;
        }
        try {
          const sr = await fetch(`${API_URL}/tasks/${data.task_id}`);
          const status = await sr.json();
          if (status.status === 'done') {
            clearInterval(poll);
            const bounds = status.result?.bounds as [[number, number], [number, number]];
            const map = side === 'A' ? mapA : mapB;
            if (map && bounds) {
              const overlay = L.imageOverlay(`${API_URL}/overlay/${status.result.path.split('/').pop()}`, bounds, { opacity: 0.8 });
              map.addLayer(overlay);
              map.flyToBounds(bounds, { duration: 1 });
              if (side === 'A') overlayA = overlay; else overlayB = overlay;
            }
            if (side === 'A') { taskIdA = data.task_id; loadingA = false; }
            else { taskIdB = data.task_id; loadingB = false; }
          } else if (status.status === 'error') {
            clearInterval(poll);
            if (side === 'A') { errorA = status.error || 'Erro'; loadingA = false; }
            else { errorB = status.error || 'Erro'; loadingB = false; }
          }
        } catch {
          console.warn('RegionComparison poll error for side:', side);
          clearInterval(poll);
          if (side === 'A') loadingA = false; else loadingB = false;
        }
      }, 1000);
    } catch (e: unknown) {
      if (side === 'A') { errorA = (e as Error).message; loadingA = false; }
      else { errorB = (e as Error).message; loadingB = false; }
    }
  }

  async function computeDifference() {
    if (!taskIdA || !taskIdB) return;
    computingDiff = true;
    try {
      const resp = await fetch(`${API_URL}/difference`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_id_a: taskIdA,
          task_id_b: taskIdB,
        }),
      });
      const data = await resp.json();
      let remaining = 120;
      const poll = setInterval(async () => {
        if (--remaining <= 0) {
          clearInterval(poll);
          computingDiff = false;
          diffError = 'Timeout';
          return;
        }
        try {
          const sr = await fetch(`${API_URL}/tasks/${data.task_id}`);
          const status = await sr.json();
          if (status.status === 'done') {
            clearInterval(poll);
            computingDiff = false;
            const bounds = status.result.bounds as [[number, number], [number, number]];
            const overlay = L.imageOverlay(`${API_URL}/overlay/${status.result.path.split('/').pop()}`, bounds, { opacity: 0.7 });
            if (diffOverlay) { mapA.removeLayer(diffOverlay); mapB.removeLayer(diffOverlay); }
            mapA.addLayer(overlay);
            mapB.addLayer(overlay);
            diffOverlay = overlay;
          } else if (status.status === 'error') {
            clearInterval(poll);
            computingDiff = false;
            diffError = status.error || 'Erro ao calcular diferença';
          }
        } catch { console.warn('RegionComparison diff poll error'); clearInterval(poll); computingDiff = false; diffError = 'Falha na conexão'; }
      }, 2000);
    } catch {
      console.warn('RegionComparison computeDifference error');
      computingDiff = false;
      diffError = 'Falha ao iniciar diferença';
    }
  }

  $effect(() => {
    if (imageA) processImage(imageA, 'A');
    if (imageB) processImage(imageB, 'B');
  });
</script>

<div class="grid grid-cols-2 gap-2 h-[400px]">
  <div class="relative rounded-lg overflow-hidden border border-border">
    <div class="absolute top-2 left-2 z-[1000] bg-black/60 text-white text-xs px-2 py-1 rounded">
      {imageA?.id?.slice(0, 30) || 'Imagem A'}...
      <span class="ml-1 text-muted-foreground">{imageA?.acquired_at ? new Date(imageA.acquired_at).toLocaleDateString('pt-BR') : ''}</span>
    </div>
    <div bind:this={mapAContainer} class="h-full w-full"></div>
    {#if loadingA}
      <div class="absolute inset-0 bg-black/40 flex items-center justify-center"><span class="text-white text-sm">Processando...</span></div>
    {/if}
    {#if errorA}
      <div class="absolute bottom-2 left-2 bg-destructive/90 text-white text-xs px-2 py-1 rounded">{errorA}</div>
    {/if}
  </div>
  <div class="relative rounded-lg overflow-hidden border border-border">
    <div class="absolute top-2 left-2 z-[1000] bg-black/60 text-white text-xs px-2 py-1 rounded">
      {imageB?.id?.slice(0, 30) || 'Imagem B'}...
      <span class="ml-1">{imageB?.acquired_at ? new Date(imageB.acquired_at).toLocaleDateString('pt-BR') : ''}</span>
    </div>
    <div bind:this={mapBContainer} class="h-full w-full"></div>
    {#if loadingB}
      <div class="absolute inset-0 bg-black/40 flex items-center justify-center"><span class="text-white text-sm">Processando...</span></div>
    {/if}
    {#if errorB}
      <div class="absolute bottom-2 left-2 bg-destructive/90 text-white text-xs px-2 py-1 rounded">{errorB}</div>
    {/if}
  </div>
</div>
{#if overlayA && overlayB && !computingDiff}
  <div class="absolute bottom-2 left-1/2 -translate-x-1/2 z-[1000]">
    <button
      class="bg-primary text-primary-foreground text-xs font-medium h-8 px-3 rounded-md cursor-pointer hover:opacity-90"
      onclick={computeDifference}
    >
      Calcular diferença NDVI
    </button>
  </div>
{/if}
{#if diffError}
  <div class="absolute bottom-10 left-1/2 -translate-x-1/2 z-[1000] bg-destructive/90 text-white text-xs px-2 py-1 rounded">{diffError}</div>
{/if}
{#if computingDiff}
  <div class="absolute bottom-2 left-1/2 -translate-x-1/2 z-[1000] bg-black/60 text-white text-xs px-2 py-1 rounded">
    Calculando diferença...
  </div>
{/if}
