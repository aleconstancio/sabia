<script lang="ts">
  import { onMount } from 'svelte';
  import L from 'leaflet';

  let {
    imageA = null as any,
    imageB = null as any,
    polygonCoords = null as any,
    polygonCentroid = null as { lat: number; lon: number },
  } = $props();

  let mapAContainer: HTMLDivElement;
  let mapBContainer: HTMLDivElement;
  let mapA: L.Map;
  let mapB: L.Map;
  let loadingA = $state(false);
  let loadingB = $state(false);
  let overlayA: any = null;
  let overlayB: any = null;
  let errorA = $state('');
  let errorB = $state('');

  const API_URL = import.meta.env.VITE_API_URL || '/api';

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

  async function processImage(image: any, side: 'A' | 'B') {
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
          product: 'NDVI',
        }),
      });
      if (!resp.ok) throw new Error('Process request failed');
      const data = await resp.json();

      const poll = setInterval(async () => {
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
              map.fitBounds(bounds);
              if (side === 'A') overlayA = overlay; else overlayB = overlay;
            }
            if (side === 'A') loadingA = false; else loadingB = false;
          } else if (status.status === 'error') {
            clearInterval(poll);
            if (side === 'A') { errorA = status.error || 'Erro'; loadingA = false; }
            else { errorB = status.error || 'Erro'; loadingB = false; }
          }
        } catch { clearInterval(poll); loadingA = false; loadingB = false; }
      }, 1000);
    } catch (e: any) {
      if (side === 'A') { errorA = e.message; loadingA = false; }
      else { errorB = e.message; loadingB = false; }
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
