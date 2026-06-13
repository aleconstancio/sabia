<script lang="ts">
	import { Select as SelectPrimitive } from "bits-ui";
	import type { Snippet } from "svelte";

	let {
		open = $bindable(false),
		value = $bindable(),
		children,
		...restProps
	}: SelectPrimitive.RootProps & { children?: Snippet } = $props();
</script>

<SelectPrimitive.Root bind:open bind:value={value as never} {children} {...restProps} />
