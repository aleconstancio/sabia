<script lang="ts">
  import { goto } from '$app/navigation';
  import type { RegionProfile } from '$lib/api/types';
  import { getNdviColor, formatTimeAgo } from '$lib/utils/dashboard';

  let { profiles = [], deleteProfile = (id: string) => {}, confirmDeleteId = null }: { profiles: RegionProfile[]; deleteProfile?: (id: string) => void; confirmDeleteId?: string | null } = $props();
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
  {#each profiles as profile (profile.id)}
    {@const ndvi = (profile.satellite_data?.stats?.mean as number) ?? null}
    {@const timeAgo = formatTimeAgo(profile.created_at)}
    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
    <div
      role="button"
      tabindex="0"
      class="text-left group glass-panel rounded-lg p-3 hover:ring-1 hover:ring-primary/30 transition-all duration-200 cursor-pointer"
      onclick={() => goto(`/map?profile=${profile.id}`)}
      onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') goto(`/map?profile=${profile.id}`); }}
    >
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-2 min-w-0">
          <span
            class="w-2 h-2 rounded-full flex-shrink-0"
            style="background: {getNdviColor(ndvi)}"
          ></span>
          <h3 class="text-sm font-semibold truncate">{profile.name || 'Unnamed Region'}</h3>
        </div>
        <div class="flex items-center gap-1.5 flex-shrink-0">
          <span class="text-[10px] text-muted-foreground font-mono">{timeAgo}</span>
          {#if confirmDeleteId === profile.id}
            <div class="flex items-center gap-1" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()} role="group" aria-label="Confirm delete">
              <button class="text-[10px] px-1.5 py-0.5 rounded bg-destructive text-destructive-foreground hover:bg-destructive/90" onclick={(e) => { e.stopPropagation(); deleteProfile(profile.id); }}>Yes</button>
              <button class="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground hover:bg-muted/80" onclick={(e) => { e.stopPropagation(); deleteProfile(profile.id); }}>No</button>
            </div>
          {:else}
            <button
              class="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive"
              onclick={(e) => { e.stopPropagation(); deleteProfile(profile.id); }}
              aria-label="Delete profile"
            >
              <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
              </svg>
            </button>
          {/if}
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 mb-2">
        <div>
          <p class="text-[9px] text-muted-foreground uppercase">Temp</p>
          <p class="text-xs font-mono font-bold text-blue-400">{profile.weather_summary?.temperature ?? '—'}°</p>
        </div>
        <div>
          <p class="text-[9px] text-muted-foreground uppercase">Humidity</p>
          <p class="text-xs font-mono font-bold text-cyan-400">{profile.weather_summary?.humidity ?? '—'}%</p>
        </div>
        <div>
          <p class="text-[9px] text-muted-foreground uppercase">NDVI</p>
          <p class="text-xs font-mono font-bold" style="color: {getNdviColor(ndvi)}">{ndvi != null ? ndvi.toFixed(2) : '—'}</p>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 mb-3">
        <div>
          <p class="text-[9px] text-muted-foreground uppercase">pH</p>
          <p class="text-xs font-mono">{profile.soil_summary?.phh2o?.toFixed(1) ?? '—'}</p>
        </div>
        <div>
          <p class="text-[9px] text-muted-foreground uppercase">OC</p>
          <p class="text-xs font-mono">{profile.soil_summary?.oc?.toFixed(1) ?? '—'} <span class="text-muted-foreground">g/kg</span></p>
        </div>
        <div>
          <p class="text-[9px] text-muted-foreground uppercase">Product</p>
          <p class="text-[10px] font-mono text-primary">{profile.satellite_data?.product ?? '—'}</p>
        </div>
      </div>

      <div class="flex gap-1.5">
        <span class="flex-1 text-center py-1 rounded text-[10px] font-medium bg-muted/50 text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary transition-colors">View Map</span>
        <span class="flex-1 text-center py-1 rounded text-[10px] font-medium bg-muted/50 text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary transition-colors">Analyze</span>
      </div>
    </div>
  {/each}
</div>
