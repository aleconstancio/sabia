<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { dashboardState, loadProfiles, deleteProfile } from '$lib/stores/dashboard.svelte';
  import Button from '$lib/ui/components/Button.svelte';
  import Badge from '$lib/ui/components/Badge.svelte';
  import Spinner from '$lib/ui/components/Spinner.svelte';
  import EmptyState from '$lib/ui/components/EmptyState.svelte';
  import ProfileSummary from '$lib/components/dashboard/ProfileSummary.svelte';
  import ProfileCard from '$lib/components/dashboard/ProfileCard.svelte';

  onMount(() => loadProfiles());
</script>

<div class="min-h-screen bg-background">
  <header class="sticky top-0 z-30 bg-background/55 backdrop-blur-xl border-b border-border px-6 py-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="sm" onclick={() => goto('/')}>← Mapa</Button>
        <h1 class="text-lg font-bold text-primary">Dashboard</h1>
        <Badge variant="secondary">{dashboardState.total} perfis</Badge>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-6 py-6 space-y-6">
    {#if dashboardState.isLoading}
      <div class="flex justify-center py-16"><Spinner size="lg" /></div>
    {:else if dashboardState.profiles.length === 0}
      <EmptyState
        title="Nenhum perfil de região"
        description="Processe uma imagem no mapa e salve como perfil para construir seu dashboard ecológico."
      >
        {#snippet action()}
          <Button onclick={() => goto('/')}>Ir para o Mapa</Button>
        {/snippet}
      </EmptyState>
    {:else}
      <ProfileSummary profiles={dashboardState.profiles} total={dashboardState.total} />
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each dashboardState.profiles as profile (profile.id)}
          <ProfileCard {profile} onDelete={() => deleteProfile(profile.id)} />
        {/each}
      </div>
    {/if}
  </main>
</div>
