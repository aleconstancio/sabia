<script lang="ts">
  import Button from '$lib/ui/components/Button.svelte';

  let { module = 'vegetation' }: { module: string } = $props();
  let thresholds = $state({
    vegetation_loss_pct: 20,
    water_change_pct: 15,
    fire_risk_level: 'high',
    carbon_decline_pct: 10,
    weather_alerts: true,
  });

  function saveThresholds() {
    localStorage.setItem(`spaceeye_thresholds_${module}`, JSON.stringify(thresholds));
  }

  $effect(() => {
    try {
      const raw = localStorage.getItem(`spaceeye_thresholds_${module}`);
      if (raw) thresholds = { ...thresholds, ...JSON.parse(raw) };
    } catch { /* ignore */ }
  });
</script>

<div class="rounded-lg border border-border bg-card p-3">
  <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Alert Thresholds</h4>
  <div class="space-y-2">
    <label class="flex items-center justify-between text-xs">
      <span class="text-muted-foreground">Vegetation Loss</span>
      <input type="number" bind:value={thresholds.vegetation_loss_pct} class="w-16 bg-muted border border-border rounded px-2 py-0.5 text-xs text-right" min="1" max="100" />%
    </label>
    <label class="flex items-center justify-between text-xs">
      <span class="text-muted-foreground">Water Change</span>
      <input type="number" bind:value={thresholds.water_change_pct} class="w-16 bg-muted border border-border rounded px-2 py-0.5 text-xs text-right" min="1" max="100" />%
    </label>
    <label class="flex items-center justify-between text-xs">
      <span class="text-muted-foreground">Carbon Decline</span>
      <input type="number" bind:value={thresholds.carbon_decline_pct} class="w-16 bg-muted border border-border rounded px-2 py-0.5 text-xs text-right" min="1" max="100" />%
    </label>
    <label class="flex items-center justify-between text-xs">
      <span class="text-muted-foreground">Weather Alerts</span>
      <input type="checkbox" bind:checked={thresholds.weather_alerts} class="accent-primary" />
    </label>
    <Button size="sm" variant="outline" fullWidth={true} onclick={saveThresholds}>Save Thresholds</Button>
  </div>
</div>
