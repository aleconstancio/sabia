<script lang="ts">
  import { onDestroy } from 'svelte';
  import { Button } from '$lib/components/ui/button';
  import type { ImageResult } from '$lib/api/types';
  import { processImage as apiProcessImage } from '$lib/api/client';
  import { pollTaskStatus } from '$lib/helpers/pollTask';
  import { logger } from '$lib/utils/logger';

  let {
    images = [] as ImageResult[],
    polygonCoords = null as number[][][] | null,
    product = 'NDVI',
    onFrameChange = (imageId: string) => {},
  } = $props();

  let playing = $state(false);
  let speed = $state(1500);
  let frameIndex = $state(0);
  let processedIds = $state<Set<string>>(new Set());
  let intervalId: ReturnType<typeof setInterval> | undefined;

  let processError = $state('');
  let processing = $state(false);
  let processProgress = $state(0);

  async function ensureProcessed(imageId: string): Promise<boolean> {
    if (processedIds.has(imageId)) return true;
    try {
      const { task_id } = await apiProcessImage(imageId, polygonCoords || [], product);
      const result = await pollTaskStatus(task_id, { maxAttempts: 60 });
      if (result.status === 'done') {
        processedIds = new Set([...processedIds, imageId]);
        return true;
      }
      return false;
    } catch {
      logger.warn('TimelapsePlayer ensureProcessed error for image:', imageId);
      processError = 'Failed to process frame';
    }
    return false;
  }

  $effect(() => {
    if (images.length > 0 && processedIds.size === 0) {
      onFrameChange(images[0].id);
    }
  });

  $effect(() => {
    if (playing) {
      if (intervalId) clearInterval(intervalId);
      intervalId = setInterval(() => {
        frameIndex = (frameIndex + 1) % images.length;
        onFrameChange(images[frameIndex].id);
      }, speed);
      return () => { if (intervalId) clearInterval(intervalId); };
    }
  });

  async function processAllFrames() {
    if (images.length === 0) return;
    processing = true;
    processProgress = 0;
    processError = '';
    const CONCURRENT = 3;
    const queue = images.map((img, i) => ({ img, i }));
    const running: Promise<void>[] = [];
    let completed = 0;

    while (queue.length > 0 || running.length > 0) {
      while (running.length < CONCURRENT && queue.length > 0) {
        const { img, i } = queue.shift()!;
        const p = ensureProcessed(img.id).then(() => {
          completed++;
          processProgress = (completed / images.length) * 100;
          running.splice(running.indexOf(p), 1);
        });
        running.push(p);
      }
      if (running.length > 0) await Promise.race(running);
    }
    processProgress = 100;
    processing = false;
  }

  async function play() {
    if (processedIds.size < images.length) {
      await processAllFrames();
    }
    playing = true;
    if (frameIndex >= images.length) frameIndex = 0;
    intervalId = setInterval(() => {
      frameIndex = (frameIndex + 1) % images.length;
      onFrameChange(images[frameIndex].id);
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
  {#if processing}
    <div class="mb-2">
      <div class="w-full bg-muted rounded-full h-1.5">
        <div class="bg-emerald-500 h-1.5 rounded-full transition-all" style="width: {processProgress}%"></div>
      </div>
      <p class="text-xs text-muted-foreground mt-1">Processing frames... {processProgress.toFixed(0)}%</p>
    </div>
  {:else}
    <div class="flex items-center gap-2 mb-2">
      <Button size="sm" variant="ghost" onclick={stop} class="!w-8 !h-8 !p-0" aria-label="Stop timelapse">⏹</Button>
      <Button size="sm" variant="default" onclick={playing ? pause : play} class="!w-8 !h-8 !p-0" aria-label={playing ? 'Pause timelapse' : 'Start timelapse'}>{playing ? '⏸' : '▶'}</Button>
      <input type="range" min="200" max="5000" step="100" bind:value={speed} class="flex-1 accent-emerald-500 h-1" aria-label="Timelapse speed" />
      <span class="text-xs text-muted-foreground w-10">{(speed / 1000).toFixed(1)}s</span>
    </div>
    <input type="range" min="0" max={Math.max(0, images.length - 1)} bind:value={frameIndex}
      onchange={() => goTo(frameIndex)} class="w-full accent-emerald-500 h-1"
      aria-label="Timelapse frame"
    />
    {#if images[frameIndex]}
      <div class="flex justify-between text-xs text-muted-foreground mt-1">
        <span>{new Date(images[frameIndex].acquired_at).toLocaleDateString()}</span>
        <span>cloud: {images[frameIndex].cloud_cover?.toFixed(0) ?? '?'}%</span>
      </div>
    {/if}
  {/if}
  {#if processError}
    <p class="text-xs text-destructive mt-1">{processError}</p>
  {/if}
</div>
