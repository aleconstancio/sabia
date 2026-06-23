/**
 * Global map state — re-exports from sub-stores for backward compatibility.
 *
 * Decomposed into focused sub-stores:
 *   - mapInstance: map, polygonCoords, polygonCentroid, rasterOverlay, hasOverlay, lastOverlayPath
 *   - searchState: results, selectedCollection, filter*, searchError, isLoading
 *   - processingState: taskId, processingProgress, processingPhase, lastStats, selectedProduct
 *   - uiState: showLegend, showPolygonModal, showImageGallery, showProcessingViewer, showComparison, sidebarOpen, lastWeatherData
 *   - comparisonState: comparisonFirst, comparisonSecond, selectedIds
 */
import { mapInstance } from './mapInstance.svelte';
import { searchState } from './searchState.svelte';
import { processingState } from './processingState.svelte';
import { uiState } from './uiState.svelte';
import { comparisonState } from './comparisonState.svelte';

/**
 * Backward-compatible mapState object. All properties proxy to sub-stores.
 * New code should import from the sub-stores directly.
 */
export const mapState = {
  // Map instance
  get map() { return mapInstance.map; },
  set map(v) { mapInstance.map = v; },
  get polygonCoords() { return mapInstance.polygonCoords; },
  set polygonCoords(v) { mapInstance.polygonCoords = v; },
  get polygonCentroid() { return mapInstance.polygonCentroid; },
  set polygonCentroid(v) { mapInstance.polygonCentroid = v; },
  get rasterOverlay() { return mapInstance.rasterOverlay; },
  set rasterOverlay(v) { mapInstance.rasterOverlay = v; },
  get hasOverlay() { return mapInstance.hasOverlay; },
  set hasOverlay(v) { mapInstance.hasOverlay = v; },
  get lastOverlayPath() { return mapInstance.lastOverlayPath; },
  set lastOverlayPath(v) { mapInstance.lastOverlayPath = v; },

  // Search
  get results() { return searchState.results; },
  set results(v) { searchState.results = v; },
  get selectedCollection() { return searchState.selectedCollection; },
  set selectedCollection(v) { searchState.selectedCollection = v; },
  get filterDateFrom() { return searchState.filterDateFrom; },
  set filterDateFrom(v) { searchState.filterDateFrom = v; },
  get filterDateTo() { return searchState.filterDateTo; },
  set filterDateTo(v) { searchState.filterDateTo = v; },
  get filterMaxCloud() { return searchState.filterMaxCloud; },
  set filterMaxCloud(v) { searchState.filterMaxCloud = v; },
  get filterSortBy() { return searchState.filterSortBy; },
  set filterSortBy(v) { searchState.filterSortBy = v; },
  get filterSortOrder() { return searchState.filterSortOrder; },
  set filterSortOrder(v) { searchState.filterSortOrder = v; },
  get isLoading() { return searchState.isLoading; },
  set isLoading(v) { searchState.isLoading = v; },
  get searchError() { return searchState.searchError; },
  set searchError(v) { searchState.searchError = v; },

  // Processing
  get taskId() { return processingState.taskId; },
  set taskId(v) { processingState.taskId = v; },
  get processingProgress() { return processingState.processingProgress; },
  set processingProgress(v) { processingState.processingProgress = v; },
  get processingPhase() { return processingState.processingPhase; },
  set processingPhase(v) { processingState.processingPhase = v; },
  get lastStats() { return processingState.lastStats; },
  set lastStats(v) { processingState.lastStats = v; },
  get selectedProduct() { return processingState.selectedProduct; },
  set selectedProduct(v) { processingState.selectedProduct = v; },

  // UI
  get showLegend() { return uiState.showLegend; },
  set showLegend(v) { uiState.showLegend = v; },
  get showPolygonModal() { return uiState.showPolygonModal; },
  set showPolygonModal(v) { uiState.showPolygonModal = v; },
  get showImageGallery() { return uiState.showImageGallery; },
  set showImageGallery(v) { uiState.showImageGallery = v; },
  get showProcessingViewer() { return uiState.showProcessingViewer; },
  set showProcessingViewer(v) { uiState.showProcessingViewer = v; },
  get showComparison() { return uiState.showComparison; },
  set showComparison(v) { uiState.showComparison = v; },
  get sidebarOpen() { return uiState.sidebarOpen; },
  set sidebarOpen(v) { uiState.sidebarOpen = v; },
  get lastWeatherData() { return uiState.lastWeatherData; },
  set lastWeatherData(v) { uiState.lastWeatherData = v; },

  // Comparison
  get comparisonFirst() { return comparisonState.comparisonFirst; },
  set comparisonFirst(v) { comparisonState.comparisonFirst = v; },
  get comparisonSecond() { return comparisonState.comparisonSecond; },
  set comparisonSecond(v) { comparisonState.comparisonSecond = v; },
  get selectedIds() { return comparisonState.selectedIds; },
  set selectedIds(v) { comparisonState.selectedIds = v; },
};
