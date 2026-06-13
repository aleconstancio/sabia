/**
 * Processing state — task ID, progress, phase, and statistics.
 */
import type { StatsData } from '$lib/api/types';

let _taskId = $state('');
let _processingProgress = $state(0);
let _processingPhase = $state('');
let _lastStats = $state<StatsData | null>(null);
let _selectedProduct = $state('NDVI');

export const processingState = {
  get taskId() { return _taskId; },
  set taskId(v) { _taskId = v; },
  get processingProgress() { return _processingProgress; },
  set processingProgress(v) { _processingProgress = v; },
  get processingPhase() { return _processingPhase; },
  set processingPhase(v) { _processingPhase = v; },
  get lastStats() { return _lastStats; },
  set lastStats(v) { _lastStats = v; },
  get selectedProduct() { return _selectedProduct; },
  set selectedProduct(v) { _selectedProduct = v; },
};
