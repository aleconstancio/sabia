<script lang="ts">
  import type { SoilData, SoilZonalResponse } from '$lib/api/types';

  import { API_URL } from '$lib/config';

  let { lat = 0, lon = 0, polygonCoords = null as number[][][] | null }: { lat: number; lon: number; polygonCoords?: number[][][] | null } = $props();
  let soil: SoilData | SoilZonalResponse | null = $state(null);
  let loading = $state(false);
  let error = $state('');

  $effect(() => {
    if (lat && lon) {
      const timer = setTimeout(() => {
        fetchSoil();
      }, 300);
      return () => clearTimeout(timer);
    }
  });


  async function fetchSoil() {
    loading = true; error = '';
    try {
      const url = polygonCoords ? `${API_URL}/soil/zonal` : `${API_URL}/soil/${lat}/${lon}`;
      const body = polygonCoords ? JSON.stringify({ coordinates: polygonCoords }) : undefined;
      const resp = await fetch(url, { method: polygonCoords ? 'POST' : 'GET', headers: { 'Content-Type': 'application/json' }, body });
      if (!resp.ok) throw new Error('Soil fetch failed');
      soil = await resp.json();
    } catch (e: unknown) {
      error = (e as Error).message;
    } finally {
      loading = false;
    }
  }

  function findValue(layer: string): number | null {
    if (!soil || !('properties' in soil)) return null;
    const props = (soil as Record<string, unknown>).properties as { layers?: Array<{ name: string; depths?: Array<{ values?: { mean?: number } }> }> } | undefined;
    if (!props?.layers) return null;
    const l = props.layers.find((l) => l.name === layer);
    return l?.depths?.[0]?.values?.mean ?? null;
  }

  let ph = $derived(!polygonCoords ? findValue('phh2o') : (soil as SoilZonalResponse | null)?.ph);
  let oc = $derived(!polygonCoords ? findValue('oc') : (soil as SoilZonalResponse | null)?.organic_carbon_gkg);
  let sand = $derived(!polygonCoords ? findValue('sand') : (soil as SoilZonalResponse | null)?.sand_pct);
  let silt = $derived(!polygonCoords ? findValue('silt') : (soil as SoilZonalResponse | null)?.silt_pct);
  let clay = $derived(!polygonCoords ? findValue('clay') : (soil as SoilZonalResponse | null)?.clay_pct);
  let nitrogen = $derived(!polygonCoords ? findValue('nitrogen') : null);
  let cec = $derived(!polygonCoords ? findValue('cec') : null);
</script>

<div class="rounded-lg border border-border bg-card p-4">
  <h3 class="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Solo</h3>
  {#if loading}
    <div class="flex items-center gap-2 text-sm text-muted-foreground">
      <span class="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin"></span>
      <span>Carregando...</span>
    </div>
  {:else if error}
    <p class="text-sm text-destructive">{error}</p>
  {:else if soil}
    {#if polygonCoords}
      <p class="text-xs text-muted-foreground mb-2">{(soil as SoilZonalResponse).source}</p>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <p class="text-xs text-muted-foreground">pH</p>
          <p class="text-lg font-bold">{(soil as SoilZonalResponse).ph?.toFixed(1) ?? '—'}</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Carbono Org.</p>
          <p class="text-lg font-bold">{(soil as SoilZonalResponse).organic_carbon_gkg?.toFixed(1) ?? '—'} g/kg</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Areia</p>
          <p class="text-lg font-bold">{(soil as SoilZonalResponse).sand_pct?.toFixed(0) ?? '—'}%</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Silte</p>
          <p class="text-lg font-bold">{(soil as SoilZonalResponse).silt_pct?.toFixed(0) ?? '—'}%</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Argila</p>
          <p class="text-lg font-bold">{(soil as SoilZonalResponse).clay_pct?.toFixed(0) ?? '—'}%</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground">Pontos amostrados</p>
          <p class="text-lg font-bold">{(soil as SoilZonalResponse).points_sampled ?? '—'}</p>
        </div>
      </div>
      {#if (soil as SoilZonalResponse).note}
        <p class="text-xs text-muted-foreground italic mt-2">{(soil as SoilZonalResponse).note}</p>
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
