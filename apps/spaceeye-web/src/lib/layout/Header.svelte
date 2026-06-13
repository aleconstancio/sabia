<script lang="ts">
  import { toggleMode } from 'mode-watcher';
  import { toast } from 'svelte-sonner';
  import { browser } from '$app/environment';
  import SearchMenu from '$lib/components/SearchMenu.svelte';
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

  function handleBookmarkSelect(coords: number[][][], _name: string) {
    mapState.polygonCoords = coords;
  }

  function copyShareLink() {
    if (!browser || !mapState.polygonCoords) return;
    const params = new URLSearchParams();
    params.set('coords', JSON.stringify(mapState.polygonCoords));
    if (mapState.taskId) params.set('image', mapState.taskId);
    params.set('product', mapState.selectedProduct);
    navigator.clipboard.writeText(`${window.location.origin}${window.location.pathname}?${params.toString()}`)
      .then(() => toast.success('Link copiado!'))
      .catch(() => toast.error('Falha ao copiar link'));
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
        aria-label="Abrir menu lateral"
        aria-expanded={mapState.sidebarOpen}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
      <h1 class="text-lg font-bold text-primary">SpaceEye</h1>
      <SearchMenu {navigateToCity} />
    </div>

    <div class="flex items-center gap-1.5 sm:gap-2 shrink-0">
      <ConnectionStatus />
      <a href="/dashboard" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
        Dashboard
      </a>
      <a href="/modules/vegetation" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
        Vegetation
      </a>
      <a href="/modules/water" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
        Water
      </a>
      <a href="/modules/fire" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
        Fire
      </a>
      <a href="/modules/soil" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
        Soil
      </a>
      <a href="/modules/climate" class="text-xs text-muted-foreground hover:text-foreground transition-colors no-underline">
        Climate
      </a>
      {#if mapState.results.length > 0}
        <Button variant={showCompare ? 'default' : 'ghost'} size="sm" onclick={onToggleCompare}>
          {showCompare ? 'Sair' : 'Comparar'}
        </Button>
        <Button variant={showTimelapse ? 'default' : 'ghost'} size="sm" onclick={onToggleTimelapse}>
          {showTimelapse ? 'Sair' : 'Timelapse'}
        </Button>
      {/if}
      {#if mapState.rasterOverlay}
        <Button variant="ghost" size="sm" onclick={onClearOverlay}>Limpar</Button>
      {/if}
      {#if mapState.hasOverlay}
        <Button variant="ghost" size="sm" onclick={copyShareLink}>Link</Button>
        <Button variant="ghost" size="sm" onclick={() => downloadGeotiff(mapState.taskId)}>GeoTIFF</Button>
        <Button variant="ghost" size="sm" onclick={onExportPdf}>PDF</Button>
      {/if}
      {#if mapState.polygonCoords}
        <Button variant="outline" size="sm" onclick={onSaveProfile} disabled={isSavingProfile}>
          {isSavingProfile ? 'Salvando...' : 'Salvar Perfil'}
        </Button>
      {/if}
      <Select.Root type="single" bind:value={mapState.selectedCollection}>
        <Select.Trigger class="!w-28 !text-xs">
          Coleção...
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
        onclick={toggleMode}
        class="inline-flex items-center justify-center rounded-[--radius] p-2 transition-colors cursor-pointer bg-transparent border-none text-muted-foreground"
        aria-label="Alternar tema"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
    </div>
  </div>
</header>
