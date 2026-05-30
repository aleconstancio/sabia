<script lang="ts">
  let {
    dateFrom = $bindable(''),
    dateTo = $bindable(''),
    maxCloud = $bindable<number | undefined>(undefined),
    sortBy = $bindable('acquired_at'),
    sortOrder = $bindable('desc'),
  } = $props();

  let cloudStr = $derived(maxCloud !== undefined ? String(maxCloud) : '');

  function onCloudChange(val: string) {
    maxCloud = val ? parseFloat(val) : undefined;
  }
</script>

<div class="flex flex-wrap gap-2 p-2 border-b border-border mb-2">
  <div class="flex items-center gap-1">
    <label class="text-xs text-muted-foreground">De:</label>
    <input type="date" bind:value={dateFrom} class="text-xs rounded border border-border bg-input px-1 py-0.5 w-28" />
  </div>
  <div class="flex items-center gap-1">
    <label class="text-xs text-muted-foreground">Até:</label>
    <input type="date" bind:value={dateTo} class="text-xs rounded border border-border bg-input px-1 py-0.5 w-28" />
  </div>
  <div class="flex items-center gap-1">
    <label class="text-xs text-muted-foreground">Nuvem máx:</label>
    <input type="number" min="0" max="100" value={cloudStr}
      oninput={(e) => onCloudChange((e.target as HTMLInputElement).value)}
      class="text-xs rounded border border-border bg-input px-1 py-0.5 w-14" />
    <span class="text-xs text-muted-foreground">%</span>
  </div>
  <div class="flex items-center gap-1">
    <label class="text-xs text-muted-foreground">Ordenar:</label>
    <select bind:value={sortBy} class="text-xs rounded border border-border bg-input px-1 py-0.5">
      <option value="acquired_at">Data</option>
      <option value="cloud_cover">Nuvem</option>
    </select>
    <select bind:value={sortOrder} class="text-xs rounded border border-border bg-input px-1 py-0.5">
      <option value="desc">Decrescente</option>
      <option value="asc">Crescente</option>
    </select>
  </div>
</div>
