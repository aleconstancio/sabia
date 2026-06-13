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
      const data = await apiProcessImage(image.id, polygonCoords, product);
      const result = await pollTaskStatus(data.task_id, { intervalMs: 1000 });
      if (result.status === 'done') {
        const bounds = result.result?.bounds as [[number, number], [number, number]];
        const map = side === 'A' ? mapA : mapB;
        if (map && bounds) {
          const overlay = L.imageOverlay(`${API_URL}/overlay/${(result.result?.path as string).split('/').pop()}`, bounds, { opacity: 0.8 });
          map.addLayer(overlay);
          map.flyToBounds(bounds, { duration: 1 });
          if (side === 'A') overlayA = overlay; else overlayB = overlay;
        }
        if (side === 'A') { taskIdA = data.task_id; }
        else { taskIdB = data.task_id; }
      } else {
        if (side === 'A') { errorA = result.error || 'Erro'; }
        else { errorB = result.error || 'Erro'; }
      }
      if (side === 'A') loadingA = false; else loadingB = false;
    } catch (e: unknown) {
      if (side === 'A') { errorA = e instanceof Error ? e.message : String(e); loadingA = false; }
      else { errorB = e instanceof Error ? e.message : String(e); loadingB = false; }
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
      const result = await pollTaskStatus(data.task_id, { intervalMs: 2000 });
      if (result.status === 'done') {
        const bounds = result.result?.bounds as [[number, number], [number, number]];
        const overlay = L.imageOverlay(`${API_URL}/overlay/${(result.result?.path as string).split('/').pop()}`, bounds, { opacity: 0.7 });
        if (diffOverlay) { mapA.removeLayer(diffOverlay); mapB.removeLayer(diffOverlay); }
        mapA.addLayer(overlay);
        mapB.addLayer(overlay);
        diffOverlay = overlay;
      } else {
        diffError = result.error || 'Erro ao calcular diferença';
      }
      computingDiff = false;
    } catch (e: unknown) {
      console.warn('RegionComparison computeDifference error:', e);
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
