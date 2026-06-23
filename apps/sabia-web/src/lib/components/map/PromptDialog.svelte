<script lang="ts">
  import { Button } from '$lib/components/ui/button';

  let {
    open = $bindable(false),
    label = '',
    value = $bindable(''),
    onSubmit = () => {},
  }: {
    open?: boolean;
    label?: string;
    value?: string;
    onSubmit?: (value: string) => void;
  } = $props();

  function handleSubmit(e: Event) {
    e.preventDefault();
    if (value.trim()) {
      onSubmit(value);
      open = false;
      value = '';
    }
  }

  function handleCancel() {
    open = false;
    value = '';
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      handleCancel();
    }
  }
</script>

{#if open}
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <div class="fixed inset-0 z-[2000] flex items-center justify-center bg-black/50" role="dialog" aria-modal="true" tabindex="-1" onkeydown={handleKeydown}>
    <form onsubmit={handleSubmit} class="bg-card border border-border rounded-lg p-6 shadow-xl w-80 space-y-4">
      <label class="text-sm font-medium" for="prompt-input">{label}</label>
      <input
        id="prompt-input"
        type="text"
        bind:value
        class="w-full px-3 py-2 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
      />
      <div class="flex justify-end gap-2">
        <Button type="button" variant="ghost" onclick={handleCancel}>Cancel</Button>
        <Button type="submit">OK</Button>
      </div>
    </form>
  </div>
{/if}