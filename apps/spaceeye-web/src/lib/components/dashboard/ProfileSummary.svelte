<script lang="ts">
  import Card from '$lib/ui/components/Card.svelte';
  import type { RegionProfile } from '$lib/api/types';

  let { profiles, total }: { profiles: RegionProfile[]; total: number } = $props();

  let avgTemp = $derived(() => {
    const temps = profiles
      .map(p => p.weather_summary?.temperature)
      .filter(t => t != null) as number[];
    return temps.length ? (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1) : null;
  });

  let avgPh = $derived(() => {
    const phs = profiles
      .map(p => p.soil_summary?.phh2o)
      .filter(p => p != null) as number[];
    return phs.length ? (phs.reduce((a, b) => a + b, 0) / phs.length).toFixed(1) : null;
  });
</script>

<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
  <Card>
    <p class="text-2xl font-bold text-primary">{total}</p>
    <p class="text-xs text-muted-foreground">Perfis de região</p>
  </Card>
  <Card>
    {#if avgTemp() !== null}
      <p class="text-2xl font-bold text-primary">{avgTemp()}°C</p>
      <p class="text-xs text-muted-foreground">Temp. média</p>
    {:else}
      <p class="text-2xl font-bold text-muted-foreground">—</p>
      <p class="text-xs text-muted-foreground">Sem dados climáticos</p>
    {/if}
  </Card>
  <Card>
    {#if avgPh() !== null}
      <p class="text-2xl font-bold text-primary">{avgPh()}</p>
      <p class="text-xs text-muted-foreground">pH médio do solo</p>
    {:else}
      <p class="text-2xl font-bold text-muted-foreground">—</p>
      <p class="text-xs text-muted-foreground">Sem dados de solo</p>
    {/if}
  </Card>
  <Card>
    <p class="text-2xl font-bold text-primary">
      {profiles.filter(p => p.satellite_data).length}
    </p>
    <p class="text-xs text-muted-foreground">Análises satélite</p>
  </Card>
</div>
