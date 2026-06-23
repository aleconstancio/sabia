/**
 * Comparison state — selected images for side-by-side comparison.
 */
import type { ImageResult } from '$lib/api/types';

let _comparisonFirst = $state<ImageResult | null>(null);
let _comparisonSecond = $state<ImageResult | null>(null);
let _selectedIds = $state<string[]>([]);

export const comparisonState = {
  get comparisonFirst() { return _comparisonFirst; },
  set comparisonFirst(v) { _comparisonFirst = v; },
  get comparisonSecond() { return _comparisonSecond; },
  set comparisonSecond(v) { _comparisonSecond = v; },
  get selectedIds() { return _selectedIds; },
  set selectedIds(v) { _selectedIds = v; },
};
