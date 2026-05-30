<script lang="ts">
  import { onDestroy } from 'svelte';

  let { lat = 0, lon = 0, polygonCoords = null as any }: { lat: number; lon: number; polygonCoords?: any } = $props();
  let soil: any = $state(null);
  let loading = $state(false);
  let error = $state('');

  const API_URL = import.meta.env.VITE_API_URL || '/api';
  let debounceTimer: ReturnType<typeof setTimeout>;

  $effect(() => {
    if (lat && lon) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        fetchSoil();
      }, 300);
    }
  });

  onDestroy(() => clearTimeout(debounceTimer));

  async function fetchSoil() {
    loading = true; error = '';
    try {
      const url = polygonCoords ? `${API_URL}/soil/zonal` : `${API_URL}/soil/${lat}/${lon}`;
      const body = polygonCoords ? JSON.stringify({ coordinates: polygonCoords }) : undefined;
      const resp = await fetch(url, { method: polygonCoords ? 'POST' : 'GET', headers: { 'Content-Type': 'application/json' }, body });
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

  let ph = $derived(!polygonCoords ? findValue('phh2o') : soil?.ph);
  let oc = $derived(!polygonCoords ? findValue('oc') : soil?.organic_carbon_gkg);
  let sand = $derived(!polygonCoords ? findValue('sand') : soil?.sand_pct);
  let silt = $derived(!polygonCoords ? findValue('silt') : soil?.silt_pct);
  let clay = $derived(!polygonCoords ? findValue('clay') : soil?.clay_pct);
  let nitrogen = $derived(!polygonCoords ? findValue('nitrogen') : null);
  let cec = $derived(!polygonCoords ? findValue('cec') : null);
</script>

<div class="rounded-lg border border-border bg-card p-4">
  <h3 class="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Solo</h3>
  {#if loading}
    <p class="text-sm text-muted-foreground">Carregando...</p>
  {:else if error}
    <p class="text-sm text-destructive">{error}</p>
  {:else if soil}
    {#if polygonCoords}
      <p class="text-xs text-muted-foreground mb-2">{soil.source}</p>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <p class="text-xs text-muted-foreground">pH</p>
          <p class="text-lg font-bold">{soil.ph?.toFixed(1) ?? '—'}</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Carbono Org.</p>
          <p class="text-lg font-bold">{soil.organic_carbon_gkg?.toFixed(1) ?? '—'} g/kg</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Areia</p>
          <p class="text-lg font-bold">{soil.sand_pct?.toFixed(0) ?? '—'}%</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Silte</p>
          <p class="text-lg font-bold">{soil.silt_pct?.toFixed(0) ?? '—'}%</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Argila</p>
          <p class="text-lg font-bold">{soil.clay_pct?.toFixed(0) ?? '—'}%</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Pontos amostrados</p>
          <p class="text-lg font-bold">{soil.points_sampled ?? '—'}</p>
        </div>
      </div>
      {#if soil.note}
        <p class="text-xs text-muted-foreground italic mt-2">{soil.note}</p>
      {/if}
    {:else}
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
  {/if}
</div>
