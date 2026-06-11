<script lang="ts">
  import { goto } from '$app/navigation';
  import Card from '$lib/ui/components/Card.svelte';
  import Badge from '$lib/ui/components/Badge.svelte';
  import type { RegionProfile } from '$lib/api/types';

  let { profiles = [] }: { profiles: RegionProfile[] } = $props();
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {#each profiles as profile (profile.id)}
    <Card interactive onclick={() => goto(`/map?profile=${profile.id}`)}>
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold truncate">{profile.name || 'Unnamed Region'}</h3>
          <span class="text-[10px] text-muted-foreground">
            {new Date(profile.created_at || '').toLocaleDateString('pt-BR')}
          </span>
        </div>

        {#if profile.weather_summary}
          <div class="flex items-center gap-2 text-xs">
            <span>🌡</span>
            <span class="font-mono">{profile.weather_summary.temperature}°C</span>
            <span class="text-muted-foreground">|</span>
            <span>{profile.weather_summary.humidity}% humidity</span>
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

        {#if profile.satellite_data?.stats?.mean}
          <div class="flex items-center gap-2 text-xs">
            <span class="text-muted-foreground">NDVI avg:</span>
            <span class="font-mono font-bold">{(profile.satellite_data.stats.mean as number).toFixed(4)}</span>
          </div>
        {/if}
      </div>
    </Card>
  {/each}
</div>
