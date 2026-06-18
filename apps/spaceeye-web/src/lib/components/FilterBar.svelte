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
    <label class="text-xs text-muted-foreground" for="filter-date-from">From:</label>
    <input id="filter-date-from" type="date" bind:value={dateFrom} class="text-xs rounded border border-border bg-input px-1 py-0.5 w-28" />
  </div>
  <div class="flex items-center gap-1">
    <label class="text-xs text-muted-foreground" for="filter-date-to">To:</label>
    <input id="filter-date-to" type="date" bind:value={dateTo} class="text-xs rounded border border-border bg-input px-1 py-0.5 w-28" />
  </div>
  <div class="flex items-center gap-1">
    <label class="text-xs text-muted-foreground" for="filter-cloud-max">Max cloud:</label>
    <input id="filter-cloud-max" type="number" min="0" max="100" value={cloudStr}
      oninput={(e) => onCloudChange((e.target as HTMLInputElement).value)}
      class="text-xs rounded border border-border bg-input px-1 py-0.5 w-14" />
    <span class="text-xs text-muted-foreground">%</span>
  </div>
  <div class="flex items-center gap-1">
    <label class="text-xs text-muted-foreground" for="filter-sort-by">Sort:</label>
    <select id="filter-sort-by" bind:value={sortBy} class="text-xs rounded border border-border bg-input px-1 py-0.5">
      <option value="acquired_at">Date</option>
      <option value="cloud_cover">Cloud</option>
    </select>
    <select id="filter-sort-order" bind:value={sortOrder} class="text-xs rounded border border-border bg-input px-1 py-0.5">
      <option value="desc">Descending</option>
      <option value="asc">Ascending</option>
    </select>
  </div>
</div>
