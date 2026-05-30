<script lang="ts">
  import { onDestroy } from 'svelte';
  import Button from '$lib/ui/components/Button.svelte';

  let {
    images = [] as any[],
    polygonCoords = null as any,
    product = 'NDVI',
    onFrameChange = (imageId: string) => {},
  } = $props();

  let playing = $state(false);
  let speed = $state(1500);
  let frameIndex = $state(0);
  let processedIds = $state<Set<string>>(new Set());
  let intervalId: ReturnType<typeof setInterval> | undefined;
  let processError = $state('');

  const API_URL = import.meta.env.VITE_API_URL || '/api';

  async function ensureProcessed(imageId: string) {
    if (processedIds.has(imageId)) return true;
    try {
      const resp = await fetch(`${API_URL}/process`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_id: imageId, coordinates: polygonCoords, product }),
      });
      if (!resp.ok) return false;
      const { task_id } = await resp.json();
      for (let i = 0; i < 60; i++) {
        await new Promise(r => setTimeout(r, 2000));
        const sr = await fetch(`${API_URL}/tasks/${task_id}`);
        const st = await sr.json();
        if (st.status === 'done') {
          processedIds.add(imageId);
          return true;
        }
        if (st.status === 'error') return false;
      }
    } catch { processError = 'Falha ao processar frame'; }
    return false;
  }

  $effect(() => {
    if (images.length > 0) ensureProcessed(images[0].id).then(() => onFrameChange(images[0].id));
  });

  async function play() {
    playing = true;
    if (frameIndex >= images.length) frameIndex = 0;
    for (let i = 0; i < Math.min(images.length, 5); i++) {
      ensureProcessed(images[i].id);
    }
    intervalId = setInterval(async () => {
      frameIndex = (frameIndex + 1) % images.length;
      const img = images[frameIndex];
      await ensureProcessed(img.id);
      onFrameChange(img.id);
      const nextIdx = (frameIndex + 1) % images.length;
      ensureProcessed(images[nextIdx].id);
    }, speed);
  }

  function pause() {
    playing = false;
    if (intervalId) clearInterval(intervalId);
  }

  function stop() {
    pause();
    frameIndex = 0;
    if (images.length > 0) onFrameChange(images[0].id);
  }

  function goTo(idx: number) {
    frameIndex = idx;
    if (images[idx]) onFrameChange(images[idx].id);
  }

  onDestroy(() => { if (intervalId) clearInterval(intervalId); });
</script>

<div class="rounded-lg border border-border bg-card p-3">
  <div class="flex items-center justify-between mb-2">
    <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Timelapse</h4>
    <span class="text-xs font-mono">{frameIndex + 1}/{images.length}</span>
  </div>
  <div class="flex items-center gap-2 mb-2">
    <Button size="sm" variant="ghost" onclick={stop} class="!w-8 !h-8 !p-0" ariaLabel="Parar timelapse">⏹</Button>
    <Button size="sm" variant="default" onclick={playing ? pause : play} class="!w-8 !h-8 !p-0" ariaLabel={playing ? 'Pausar timelapse' : 'Iniciar timelapse'}>{playing ? '⏸' : '▶'}</Button>
    <input type="range" min="200" max="5000" step="100" bind:value={speed} class="flex-1 accent-emerald-500 h-1" aria-label="Velocidade do timelapse" />
    <span class="text-xs text-muted-foreground w-10">{(speed / 1000).toFixed(1)}s</span>
  </div>
  <input type="range" min="0" max={Math.max(0, images.length - 1)} bind:value={frameIndex}
    onchange={() => goTo(frameIndex)} class="w-full accent-emerald-500 h-1"
    aria-label="Frame do timelapse"
  />
  {#if images[frameIndex]}
    <div class="flex justify-between text-xs text-muted-foreground mt-1">
      <span>{new Date(images[frameIndex].acquired_at || images[frameIndex].date).toLocaleDateString('pt-BR')}</span>
      <span>nuvem: {images[frameIndex].cloud_cover?.toFixed(0) ?? '?'}%</span>
    </div>
  {/if}
  {#if processError}
    <p class="text-xs text-destructive mt-1">{processError}</p>
  {/if}
</div>
