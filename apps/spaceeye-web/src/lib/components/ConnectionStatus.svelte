<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Badge } from '$lib/components/ui/badge';
  import { API_URL } from '$lib/config';

  let status = $state<'checking' | 'connected' | 'empty' | 'disconnected'>('checking');
  let catalogCount = $state(0);
  let interval: ReturnType<typeof setInterval>;

  async function checkHealth() {
    try {
      const res = await fetch(`${API_URL}/health`);
      if (!res.ok) throw new Error('not ok');
      const data = await res.json();
      if (data.catalog_count === 0) {
        status = 'empty';
      } else {
        status = 'connected';
        catalogCount = data.catalog_count;
      }
    } catch {
      console.warn('ConnectionStatus health check failed');
      status = 'disconnected';
    }
  }

  onMount(() => {
    checkHealth();
    interval = setInterval(checkHealth, 30000);
  });

  onDestroy(() => {
    clearInterval(interval);
  });
</script>

{#if status === 'checking'}
  <Badge variant="outline">Verificando...</Badge>
{:else if status === 'connected'}
  <Badge variant="success">{catalogCount.toLocaleString('pt-BR')} imagens</Badge>
{:else if status === 'empty'}
  <Badge variant="warning">Banco vazio</Badge>
{:else}
  <Badge variant="destructive">Backend offline</Badge>
{/if}
