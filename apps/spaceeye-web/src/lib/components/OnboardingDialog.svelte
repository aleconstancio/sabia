<script lang="ts">
  import Dialog from '$lib/ui/components/Dialog.svelte';
  import Button from '$lib/ui/components/Button.svelte';

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

<Dialog bind:open title={steps[step].title}>
  <div class="text-center py-4">
    <div class="text-5xl mb-4">{steps[step].icon}</div>
    <p class="text-sm text-muted-foreground">{steps[step].description}</p>
    <div class="flex justify-center gap-1.5 mt-6">
      {#each steps as _, i}
        <div class="w-2 h-2 rounded-full transition-colors" class:bg-primary={i === step} class:bg-muted={i !== step}></div>
      {/each}
    </div>
  </div>
  {#snippet actions()}
    <Button variant="ghost" onclick={skip}>Pular</Button>
    <Button onclick={next}>{step < steps.length - 1 ? 'Próximo' : 'Começar'}</Button>
  {/snippet}
</Dialog>
