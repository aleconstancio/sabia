<script lang="ts">
  import { toast } from 'svelte-sonner';
  import { browser } from '$app/environment';
  import { page } from '$app/state';
  import SearchMenu from '$lib/components/SearchMenu.svelte';

  let path = $derived(page.url.pathname);
  import HistoryPanel from '$lib/components/HistoryPanel.svelte';
  import MonitoringPanel from '$lib/components/MonitoringPanel.svelte';
  import Bookmarks from '$lib/components/Bookmarks.svelte';
  import ConnectionStatus from '$lib/components/ConnectionStatus.svelte';
  import AlertBell from '$lib/components/alerts/AlertBell.svelte';
  import * as Select from '$lib/components/ui/select';
  import { Button } from '$lib/components/ui/button';
  import { restorePolygonOnMap } from '$lib/helpers/map-helpers';
  import { mapState } from '$lib/stores/map.svelte';
  import { downloadGeotiff } from '$lib/api/processing';

  import type { AnalysisRecord } from '$lib/api/types';

  let {
    navigateToCity = (lat: number, lng: number) => {},
    onToggleCompare = () => {},
    onToggleTimelapse = () => {},
    onClearOverlay = () => {},
    onExportPdf = () => {},
    onSaveProfile = () => {},
    isSavingProfile = false,
    showCompare = false,
    showTimelapse = false,
  }: {
    navigateToCity?: (lat: number, lng: number) => void;
    onToggleCompare?: (e: MouseEvent) => void;
    onToggleTimelapse?: (e: MouseEvent) => void;
    onClearOverlay?: (e: MouseEvent) => void;
    onExportPdf?: (e: MouseEvent) => void;
    onSaveProfile?: (e: MouseEvent) => void;
    isSavingProfile?: boolean;
    showCompare?: boolean;
    showTimelapse?: boolean;
  } = $props();

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/modules/vegetation', label: 'Vegetation' },
    { href: '/modules/water', label: 'Water' },
    { href: '/modules/fire', label: 'Fire' },
    { href: '/modules/soil', label: 'Soil' },
    { href: '/modules/climate', label: 'Climate' },
  ];

  function handleBookmarkSelect(coords: number[][][], _name: string) {
    mapState.polygonCoords = coords;
  }

  let exportingPdf = $state(false);
  let exportingGeotiff = $state(false);

  async function handleExportPdf(e: MouseEvent) {
    exportingPdf = true;
    try {
      onExportPdf(e);
    } finally {
      exportingPdf = false;
    }
  }

  async function handleExportGeotiff() {
    exportingGeotiff = true;
    try {
      await downloadGeotiff(mapState.taskId);
    } finally {
      exportingGeotiff = false;
    }
  }

  function copyShareLink() {
    if (!browser || !mapState.polygonCoords) return;
    const params = new URLSearchParams();
    params.set('coords', JSON.stringify(mapState.polygonCoords));
    if (mapState.taskId) params.set('image', mapState.taskId);
    params.set('product', mapState.selectedProduct);
    navigator.clipboard.writeText(`${window.location.origin}${window.location.pathname}?${params.toString()}`)
      .then(() => toast.success('Link copied!'))
      .catch(() => toast.error('Failed to copy link'));
  }

  async function handleRestore(r: AnalysisRecord) {
    if (r?.polygonCoords) {
      mapState.polygonCoords = r.polygonCoords;
      await restorePolygonOnMap(r.polygonCoords);
    }
  }
</script>

<header
  class="sticky top-0 shrink-0 z-30 transition-all duration-300 bg-background/55 backdrop-blur-xl border-b border-border"
>
  <div class="flex items-center justify-between gap-2 sm:gap-4 px-3 sm:px-4 py-2 overflow-x-auto">
    <div class="flex items-center gap-3 min-w-0 shrink-0">
      <button
        onclick={() => mapState.sidebarOpen = !mapState.sidebarOpen}
        class="inline-flex items-center justify-center rounded-[--radius] p-2 transition-colors cursor-pointer bg-transparent border-none text-muted-foreground"
        aria-label="Open sidebar"
        aria-expanded={mapState.sidebarOpen}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
      <h1 class="text-lg font-bold text-primary">Horus</h1>
      <SearchMenu {navigateToCity} />
    </div>

    <div class="flex items-center gap-1.5 sm:gap-2 shrink-0">
      <ConnectionStatus />
      <a href="/dashboard" class="text-xs {path === '/dashboard' ? 'text-foreground font-medium' : 'text-muted-foreground hover:text-foreground'} transition-colors no-underline">
        Dashboard
      </a>
      <a href="/modules/vegetation" class="text-xs {path.startsWith('/modules/vegetation') ? 'text-foreground font-medium' : 'text-muted-foreground hover:text-foreground'} transition-colors no-underline">
        Vegetation
      </a>
      <a href="/modules/water" class="text-xs {path.startsWith('/modules/water') ? 'text-foreground font-medium' : 'text-muted-foreground hover:text-foreground'} transition-colors no-underline">
        Water
      </a>
      <a href="/modules/fire" class="text-xs {path.startsWith('/modules/fire') ? 'text-foreground font-medium' : 'text-muted-foreground hover:text-foreground'} transition-colors no-underline">
        Fire
      </a>
      <a href="/modules/soil" class="text-xs {path.startsWith('/modules/soil') ? 'text-foreground font-medium' : 'text-muted-foreground hover:text-foreground'} transition-colors no-underline">
        Soil
      </a>
      <a href="/modules/climate" class="text-xs {path.startsWith('/modules/climate') ? 'text-foreground font-medium' : 'text-muted-foreground hover:text-foreground'} transition-colors no-underline">
        Climate
      </a>
      {#if mapState.results.length > 0}
        <Button variant={showCompare ? 'default' : 'ghost'} size="sm" onclick={onToggleCompare}>
          {showCompare ? 'Exit' : 'Compare'}
        </Button>
        <Button variant={showTimelapse ? 'default' : 'ghost'} size="sm" onclick={onToggleTimelapse}>
          {showTimelapse ? 'Exit' : 'Timelapse'}
        </Button>
      {/if}
      {#if mapState.rasterOverlay}
        <Button variant="ghost" size="sm" onclick={onClearOverlay}>Clear</Button>
      {/if}
      {#if mapState.hasOverlay}
        <Button variant="ghost" size="sm" onclick={copyShareLink}>Link</Button>
        <Button variant="ghost" size="sm" onclick={handleExportGeotiff} disabled={exportingGeotiff}>
          {#if exportingGeotiff}
            <span class="w-3 h-3 border-[2px] border-current border-t-transparent rounded-full animate-spin mr-1"></span>
            Exporting...
          {:else}
            GeoTIFF
          {/if}
        </Button>
        <Button variant="ghost" size="sm" onclick={handleExportPdf} disabled={exportingPdf}>
          {#if exportingPdf}
            <span class="w-3 h-3 border-[2px] border-current border-t-transparent rounded-full animate-spin mr-1"></span>
            Exporting...
          {:else}
            PDF
          {/if}
        </Button>
      {/if}
      {#if mapState.polygonCoords}
        <Button variant="outline" size="sm" onclick={onSaveProfile} disabled={isSavingProfile}>
          {isSavingProfile ? 'Saving...' : 'Save Profile'}
        </Button>
      {/if}
      <Select.Root type="single" bind:value={mapState.selectedCollection}>
        <Select.Trigger class="!w-28 !text-xs">
          Collection...
        </Select.Trigger>
        <Select.Content>
          <Select.Item value="cbers4a">CBERS-4A</Select.Item>
          <Select.Item value="sentinel2">Sentinel-2</Select.Item>
          <Select.Item value="landsat8">Landsat 8</Select.Item>
          <Select.Item value="landsat9">Landsat 9</Select.Item>
        </Select.Content>
      </Select.Root>
      <HistoryPanel onRestore={handleRestore} />
      <MonitoringPanel />
      <Bookmarks currentCoords={mapState.polygonCoords} onSelect={handleBookmarkSelect} />
      <AlertBell />
      <button
        onclick={() => { localStorage.removeItem('horus_onboarded'); window.location.reload(); }}
        class="inline-flex items-center justify-center rounded-[--radius] w-7 h-7 text-xs font-medium transition-colors cursor-pointer bg-transparent border border-border text-muted-foreground hover:text-foreground"
        aria-label="Replay onboarding tutorial"
      >?</button>
    </div>
  </div>
</header>
