<script lang="ts">
  import { Select as BitsSelect } from 'bits-ui';

  type Option = { value: string; label: string; disabled?: boolean };
  type TFunction = (key: string, params?: Record<string, string | number>) => string;

  let {
    t = undefined as TFunction | undefined,
    value = $bindable(''),
    label = undefined as string | undefined,
    placeholder = t?.('input.Select.placeholder') ?? 'Selecione...',
    options = [] as Option[],
    disabled = false,
    required = false,
    error = undefined as string | undefined,
  }: {
    t?: TFunction;
    value?: string;
    label?: string;
    placeholder?: string;
    options?: Option[];
    disabled?: boolean;
    required?: boolean;
    error?: string;
  } = $props();

  let selectedLabel = $derived(options.find(o => o.value === value)?.label || placeholder);
</script>

{#if label}
  <label class="block text-sm font-medium mb-1.5 text-muted-foreground">{label}</label>
{/if}

<BitsSelect.Root bind:value {disabled} {required}>
  <BitsSelect.Trigger
    class="flex w-full items-center justify-between rounded-[--radius] border bg-input px-3 py-2 text-sm cursor-pointer
           text-foreground transition-colors duration-[--duration-snappy]
           focus:outline-none focus:ring-2 focus:ring-ring
           disabled:opacity-50 disabled:cursor-not-allowed
           data-[placeholder]:text-muted-foreground
           {error ? 'border-destructive' : 'border-border'}"
  >
    <BitsSelect.Value placeholder={placeholder} />
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="m6 9 6 6 6-6" />
    </svg>
  </BitsSelect.Trigger>

  <BitsSelect.Content
    class="z-[--z-overlay,30] mt-1 max-h-60 min-w-[--bits-select-anchor-width] overflow-auto rounded-[--radius] border bg-card p-1 shadow-md"
    style="border-color: var(--border)"
  >
    <BitsSelect.Group class="space-y-0.5">
      {#each options as option}
        <BitsSelect.Item
          {value}
          disabled={option.disabled}
          class="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm
                 text-foreground hover:bg-muted data-[state=checked]:bg-muted data-[state=checked]:text-foreground
                 focus:outline-none focus:bg-muted"
        >
          <BitsSelect.ItemIndicator class="mr-2 inline-flex items-center">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </BitsSelect.ItemIndicator>
          <BitsSelect.ItemLabel>{option.label}</BitsSelect.ItemLabel>
        </BitsSelect.Item>
      {/each}
    </BitsSelect.Group>
  </BitsSelect.Content>
</BitsSelect.Root>

{#if error}
  <p class="mt-1 text-xs text-destructive">{error}</p>
{/if}
