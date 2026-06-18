<script lang="ts">
  import * as Dialog from '$lib/components/ui/dialog';
  import { Button } from '$lib/components/ui/button';

  let { open = $bindable(false) }: { open?: boolean } = $props();
  let step = $state(0);
  let previousFocus = $state<HTMLElement | null>(null);

  function handleClose() {
    step = 0;
    open = false;
    previousFocus?.focus();
  }

  function handleOpenChange(isOpen: boolean) {
    if (isOpen) {
      previousFocus = document.activeElement as HTMLElement;
    }
    if (!isOpen) {
      step = 0;
    }
  }

  const steps = [
    { title: 'Welcome to SpaceEye', description: 'Analyze satellite images of your region with vegetation, soil, and climate tools.', icon: '🛰️' },
    { title: 'Draw an area', description: 'Use the polygon tool on the map to select the region you want to analyze.', icon: '✏️' },
    { title: 'Search and process', description: 'Choose a spectral product (NDVI, TCI...) and process the image to see the result on the map.', icon: '📊' },
    { title: 'Explore modules', description: 'Use Vegetation, Water, Fire, Soil, and Climate modules to analyze your region from different angles.', icon: '🔬' },
    { title: 'Analyze strategically', description: 'Save locations, monitor changes, and use the dashboard to compare areas over time.', icon: '🗺️' },
  ];

  function next() {
    if (step < steps.length - 1) { step++; }
    else { localStorage.setItem('spaceeye_onboarded', 'true'); handleClose(); }
  }
  function skip() { localStorage.setItem('spaceeye_onboarded', 'true'); handleClose(); }
</script>

<Dialog.Root bind:open onOpenChange={handleOpenChange}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" />
    <Dialog.Content class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card border border-border p-6 shadow-lg" onkeydown={(e) => { if (e.key === 'Escape') handleClose(); }}>
      <Dialog.Title>{steps[step].title}</Dialog.Title>
      <div class="text-center py-4">
        <div class="text-5xl mb-4">{steps[step].icon}</div>
        <p class="text-sm text-muted-foreground">{steps[step].description}</p>
        <div class="flex flex-col items-center gap-2 mt-6">
          <div class="flex justify-center gap-1.5">
            {#each steps as _, i}
              <div class="w-2 h-2 rounded-full transition-colors" class:bg-primary={i === step} class:bg-muted={i !== step}></div>
            {/each}
          </div>
          <span class="text-[10px] text-muted-foreground">Step {step + 1} of {steps.length}</span>
        </div>
      </div>
      <Dialog.Footer>
        <Button variant="ghost" onclick={skip}>Skip</Button>
        <Button onclick={next}>{step < steps.length - 1 ? 'Next' : 'Get Started'}</Button>
      </Dialog.Footer>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
