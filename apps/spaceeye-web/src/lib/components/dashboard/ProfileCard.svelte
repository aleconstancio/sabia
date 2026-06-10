<script lang="ts">
  import Card from '$lib/ui/components/Card.svelte';
  import Badge from '$lib/ui/components/Badge.svelte';
  import Button from '$lib/ui/components/Button.svelte';
  import type { RegionProfile } from '$lib/api/types';

  let { profile, onDelete }: { profile: RegionProfile; onDelete: () => void } = $props();
  let expanded = $state(false);

  const weatherIcons: Record<number, string> = {
    0: '☀️', 1: '🌤️', 2: '⛅', 3: '☁️',
    45: '🌫️', 48: '🌫️', 51: '🌦️', 61: '🌧️', 71: '❄️', 95: '⛈️',
  };
</script>

<Card interactive onclick={() => expanded = !expanded}>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold truncate">{profile.name || 'Região sem nome'}</h3>
      <span class="text-[10px] text-muted-foreground">
        {new Date(profile.created_at || '').toLocaleDateString('pt-BR')}
      </span>
    </div>

    {#if profile.weather_summary}
      <div class="flex items-center gap-2 text-xs">
        <span>{weatherIcons[profile.weather_summary.weather_code || 0] || '🌡️'}</span>
        <span class="font-mono">{profile.weather_summary.temperature}°C</span>
        <span class="text-muted-foreground">|</span>
        <span>{profile.weather_summary.humidity}% umidade</span>
      </div>
    {/if}

    {#if profile.soil_summary}
      <div class="flex items-center gap-2 text-xs">
        <span>🌱</span>
        <span>pH {profile.soil_summary.phh2o?.toFixed(1) || '—'}</span>
        <span class="text-muted-foreground">|</span>
        <span>OC {profile.soil_summary.oc?.toFixed(1) || '—'} g/kg</span>
      </div>
    {/if}

    {#if profile.satellite_data}
      <Badge variant="success">{profile.satellite_data.product}</Badge>
    {/if}

    {#if expanded}
      <div class="pt-2 border-t border-border space-y-2 text-[11px]">
        {#if profile.weather_summary}
          <div>
            <p class="font-medium">Clima</p>
            <p>Temp: {profile.weather_summary.temperature}°C | Chuva: {profile.weather_summary.precipitation}mm</p>
          </div>
        {/if}
        {#if profile.soil_summary}
          <div>
            <p class="font-medium">Solo</p>
            <p>pH: {profile.soil_summary.phh2o} | Areia: {profile.soil_summary.sand}% | Argila: {profile.soil_summary.clay}%</p>
          </div>
        {/if}
        {#if profile.satellite_data?.stats}
          <div>
            <p class="font-medium">Estatísticas</p>
            {#each Object.entries(profile.satellite_data.stats) as [key, value]}
              {#if typeof value === 'number'}
                <span class="mr-2">{key}: {value.toFixed(4)}</span>
              {/if}
            {/each}
          </div>
        {/if}
      </div>
    {/if}

    <div class="flex justify-end pt-1">
      <Button variant="ghost" size="sm" onclick={(e) => { e.stopPropagation(); if (confirm('Tem certeza que deseja remover este perfil?')) onDelete(); }} class="!text-[10px] !text-destructive">
        Remover
      </Button>
    </div>
  </div>
</Card>
