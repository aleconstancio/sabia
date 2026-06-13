<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { Button } from '$lib/components/ui/button';

  type TFunction = (key: string, params?: Record<string, string | number>) => string;

  let {
    t = undefined as TFunction | undefined,
    fallbackTitle = t?.('error.ErrorBoundary.title') ?? 'Algo deu errado',
    fallbackDescription = t?.('error.ErrorBoundary.description') ?? 'Ocorreu um erro inesperado. Tente recarregar a página.',
    showRetry = true,
    showHome = false,
    homeUrl = '/',
    onError,
    children,
  }: {
    t?: TFunction;
    fallbackTitle?: string;
    fallbackDescription?: string;
    showRetry?: boolean;
    showHome?: boolean;
    homeUrl?: string;
    onError?: (error: Error) => void;
    children?: import('svelte').Snippet;
  } = $props();

  let error = $state<Error | null>(null);
  let errorInfo = $state<string>('');

  onMount(() => {
    const handler = (event: ErrorEvent) => {
      error = event.error || new Error(event.message);
      errorInfo = event.message;
      if (error) onError?.(error);
      toast.error(fallbackTitle, { description: errorInfo.slice(0, 120) });
      event.preventDefault();
    };
    const rejectionHandler = (event: PromiseRejectionEvent) => {
      error = event.reason instanceof Error ? event.reason : new Error(String(event.reason));
      errorInfo = String(event.reason);
      if (error) onError?.(error);
      toast.error(fallbackTitle, { description: errorInfo.slice(0, 120) });
      event.preventDefault();
    };
    window.addEventListener('error', handler);
    window.addEventListener('unhandledrejection', rejectionHandler);
    return () => {
      window.removeEventListener('error', handler);
      window.removeEventListener('unhandledrejection', rejectionHandler);
    };
  });

  function retry() {
    error = null;
    errorInfo = '';
    window.location.reload();
  }
</script>

{#if error}
  <div class="flex flex-col items-center justify-center p-8 text-center min-h-[40vh]">
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--destructive)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
    <h2 class="text-lg font-semibold mt-4 text-foreground">{fallbackTitle}</h2>
    <p class="text-sm mt-2 max-w-md text-muted-foreground">{fallbackDescription}</p>
    <div class="flex gap-3 mt-6">
      {#if showRetry}
        <Button onclick={retry}>{t?.('common.reload') ?? 'Recarregar'}</Button>
      {/if}
      {#if showHome}
        <Button variant="secondary" href={homeUrl}>{t?.('error.ErrorBoundary.home') ?? 'Página Inicial'}</Button>
      {/if}
    </div>
  </div>
{:else}
  {@render children?.()}
{/if}
