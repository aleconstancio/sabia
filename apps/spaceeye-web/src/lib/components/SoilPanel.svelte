<script lang="ts">
  let { lat = 0, lon = 0 }: { lat: number; lon: number } = $props();
  let soil: any = $state(null);
  let loading = $state(false);
  let error = $state('');

  const API_URL = import.meta.env.VITE_API_URL || '/api';

  $effect(() => { if (lat && lon) fetchSoil(); });

  async function fetchSoil() {
    loading = true; error = '';
    try {
      const resp = await fetch(`${API_URL}/soil/${lat}/${lon}`);
      if (!resp.ok) throw new Error('Soil fetch failed');
      soil = await resp.json();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function findValue(layer: string): number | null {
    if (!soil?.properties?.layers) return null;
    const l = soil.properties.layers.find((l: any) => l.name === layer);
    return l?.depths?.[0]?.values?.mean ?? null;
  }

  let ph = $derived(findValue('phh2o'));
  let oc = $derived(findValue('oc'));
  let nitrogen = $derived(findValue('nitrogen'));
  let sand = $derived(findValue('sand'));
  let silt = $derived(findValue('silt'));
  let clay = $derived(findValue('clay'));
  let cec = $derived(findValue('cec'));
</script>

<div class="rounded-lg border border-border bg-card p-4">
  <h3 class="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Solo</h3>
  {#if loading}
    <p class="text-sm text-muted-foreground">Carregando...</p>
  {:else if error}
    <p class="text-sm text-destructive">{error}</p>
  {:else if soil}
    <div class="grid grid-cols-2 gap-3">
      <div>
        <p class="text-xs text-muted-foreground">pH</p>
        <p class="text-lg font-bold">{ph?.toFixed(1) ?? '—'}</p>
        <p class="text-xs" class:text-emerald-400={ph && ph >= 5.5 && ph <= 7.5} class:text-amber-400={ph && (ph < 5.5 || ph > 7.5)}>
          {ph ? (ph >= 5.5 && ph <= 7.5 ? 'Ideal' : ph < 5.5 ? 'Ácido' : 'Alcalino') : ''}
        </p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Carbono Org.</p>
        <p class="text-lg font-bold">{oc?.toFixed(1) ?? '—'} g/kg</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Nitrogênio</p>
        <p class="text-lg font-bold">{nitrogen ? (nitrogen / 100).toFixed(2) : '—'}%</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">CTC</p>
        <p class="text-lg font-bold">{cec?.toFixed(1) ?? '—'} cmolc/kg</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Areia</p>
        <p class="text-lg font-bold">{sand?.toFixed(0) ?? '—'}%</p>
      </div>
      <div>
        <p class="text-xs text-muted-foreground">Argila</p>
        <p class="text-lg font-bold">{clay?.toFixed(0) ?? '—'}%</p>
      </div>
    </div>
  {/if}
</div>
