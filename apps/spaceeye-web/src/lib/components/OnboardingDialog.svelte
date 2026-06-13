<script lang="ts">
  import * as Dialog from '$lib/components/ui/dialog';
  import { Button } from '$lib/components/ui/button';

  let { open = $bindable(false) }: { open?: boolean } = $props();
  let step = $state(0);

  const steps = [
    { title: 'Bem-vindo ao SpaceEye', description: 'Analise imagens de satélite da sua região com ferramentas de vegetação, solo e clima.', icon: '🛰️' },
    { title: 'Desenhe uma área', description: 'Use a ferramenta de polígono no mapa para selecionar a região que deseja analisar.', icon: '✏️' },
    { title: 'Busque e processe', description: 'Escolha um produto espectral (NDVI, TCI...) e processe a imagem para ver o resultado no mapa.', icon: '📊' },
    { title: 'Analise estrategicamente', description: 'Salve locais, monitore mudanças e use o dashboard para comparar áreas ao longo do tempo.', icon: '🗺️' },
  ];

  function next() {
    if (step < steps.length - 1) { step++; }
    else { localStorage.setItem('spaceeye_onboarded', 'true'); open = false; }
  }
  function skip() { localStorage.setItem('spaceeye_onboarded', 'true'); open = false; }
</script>

<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm" />
    <Dialog.Content class="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card border border-border p-6 shadow-lg">
      <Dialog.Title>{steps[step].title}</Dialog.Title>
      <div class="text-center py-4">
        <div class="text-5xl mb-4">{steps[step].icon}</div>
        <p class="text-sm text-muted-foreground">{steps[step].description}</p>
        <div class="flex justify-center gap-1.5 mt-6">
          {#each steps as _, i}
            <div class="w-2 h-2 rounded-full transition-colors" class:bg-primary={i === step} class:bg-muted={i !== step}></div>
          {/each}
        </div>
      </div>
      <Dialog.Footer>
        <Button variant="ghost" onclick={skip}>Pular</Button>
        <Button onclick={next}>{step < steps.length - 1 ? 'Próximo' : 'Começar'}</Button>
      </Dialog.Footer>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
