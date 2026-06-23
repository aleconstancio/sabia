/**
 * Search state — image search results, collection, filters, loading/error.
 */
import type { ImageResult } from '$lib/api/types';

let _results = $state<ImageResult[]>([]);
let _selectedCollection = $state('cbers4a');
let _filterDateFrom = $state('');
let _filterDateTo = $state('');
let _filterMaxCloud = $state<number | undefined>(undefined);
let _filterSortBy = $state('acquired_at');
let _filterSortOrder = $state('desc');
let _isLoading = $state(false);
let _searchError = $state('');

export const searchState = {
  get results() { return _results; },
  set results(v) { _results = v; },
  get selectedCollection() { return _selectedCollection; },
  set selectedCollection(v) { _selectedCollection = v; },
  get filterDateFrom() { return _filterDateFrom; },
  set filterDateFrom(v) { _filterDateFrom = v; },
  get filterDateTo() { return _filterDateTo; },
  set filterDateTo(v) { _filterDateTo = v; },
  get filterMaxCloud() { return _filterMaxCloud; },
  set filterMaxCloud(v) { _filterMaxCloud = v; },
  get filterSortBy() { return _filterSortBy; },
  set filterSortBy(v) { _filterSortBy = v; },
  get filterSortOrder() { return _filterSortOrder; },
  set filterSortOrder(v) { _filterSortOrder = v; },
  get isLoading() { return _isLoading; },
  set isLoading(v) { _isLoading = v; },
  get searchError() { return _searchError; },
  set searchError(v) { _searchError = v; },
};
