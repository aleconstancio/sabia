/**
 * Global map state — 34 reactive properties covering map instance, polygon drawing,
 * image search results, processing pipeline, comparison mode, weather data, filters,
 * sidebar, and overlay management.
 *
 * NOTE: This is a god object. Consider decomposing into sub-stores:
 *   - mapStore: map, polygonCoords, polygonCentroid, rasterOverlay, hasOverlay, lastOverlayPath
 *   - searchStore: results, selectedCollection, filter*, searchError, isLoading
 *   - processingStore: taskId, processingProgress, processingPhase, lastStats
 *   - uiStore: showLegend, showPolygonModal, showImageGallery, showProcessingViewer, showComparison, sidebarOpen
 *   - comparisonStore: comparisonFirst, comparisonSecond, selectedIds
 *   - weatherStore: lastWeatherData
 */
import L from 'leaflet';
import type { Map as LeafletMap } from 'leaflet';
import type { ImageResult, WeatherData, AnalysisRecord, StatsData } from '$lib/api/types';

let _map: LeafletMap | null = $state(null);
let _polygonCoords = $state<number[][][] | null>(null);
let _polygonCentroid = $state<{lat: number; lon: number} | null>(null);
let _results = $state<ImageResult[]>([]);
let _selectedProduct = $state('NDVI');
let _showLegend = $state(false);
let _hasOverlay = $state(false);
let _rasterOverlay: L.ImageOverlay | null = $state(null);
let _showPolygonModal = $state(false);
let _showImageGallery = $state(false);
let _showProcessingViewer = $state(false);
let _showComparison = $state(false);
let _isLoading = $state(false);
let _processingProgress = $state(0);
let _processingPhase = $state('');
let _taskId = $state('');
let _searchError = $state('');
let _comparisonFirst = $state<ImageResult | null>(null);
let _comparisonSecond = $state<ImageResult | null>(null);
let _selectedIds = $state<string[]>([]);
let _lastWeatherData = $state<WeatherData | null>(null);
let _lastOverlayPath = $state('');
let _selectedCollection = $state('cbers4a');
let _filterDateFrom = $state('');
let _filterDateTo = $state('');
let _filterMaxCloud = $state<number | undefined>(undefined);
let _filterSortBy = $state('acquired_at');
let _filterSortOrder = $state('desc');
let _lastStats = $state<StatsData | null>(null);
let _sidebarOpen = $state(true);

export const mapState = {
  get map() { return _map; },
  set map(v) { _map = v; },
  get polygonCoords() { return _polygonCoords; },
  set polygonCoords(v) { _polygonCoords = v; },
  get polygonCentroid() { return _polygonCentroid; },
  set polygonCentroid(v) { _polygonCentroid = v; },
  get results() { return _results; },
  set results(v) { _results = v; },
  get selectedProduct() { return _selectedProduct; },
  set selectedProduct(v) { _selectedProduct = v; },
  get showLegend() { return _showLegend; },
  set showLegend(v) { _showLegend = v; },
  get hasOverlay() { return _hasOverlay; },
  set hasOverlay(v) { _hasOverlay = v; },
  get rasterOverlay() { return _rasterOverlay; },
  set rasterOverlay(v) { _rasterOverlay = v; },
  get showPolygonModal() { return _showPolygonModal; },
  set showPolygonModal(v) { _showPolygonModal = v; },
  get showImageGallery() { return _showImageGallery; },
  set showImageGallery(v) { _showImageGallery = v; },
  get showProcessingViewer() { return _showProcessingViewer; },
  set showProcessingViewer(v) { _showProcessingViewer = v; },
  get showComparison() { return _showComparison; },
  set showComparison(v) { _showComparison = v; },
  get isLoading() { return _isLoading; },
  set isLoading(v) { _isLoading = v; },
  get processingProgress() { return _processingProgress; },
  set processingProgress(v) { _processingProgress = v; },
  get processingPhase() { return _processingPhase; },
  set processingPhase(v) { _processingPhase = v; },
  get taskId() { return _taskId; },
  set taskId(v) { _taskId = v; },
  get searchError() { return _searchError; },
  set searchError(v) { _searchError = v; },
  get comparisonFirst() { return _comparisonFirst; },
  set comparisonFirst(v) { _comparisonFirst = v; },
  get comparisonSecond() { return _comparisonSecond; },
  set comparisonSecond(v) { _comparisonSecond = v; },
  get selectedIds() { return _selectedIds; },
  set selectedIds(v) { _selectedIds = v; },
  get lastWeatherData() { return _lastWeatherData; },
  set lastWeatherData(v) { _lastWeatherData = v; },
  get lastOverlayPath() { return _lastOverlayPath; },
  set lastOverlayPath(v) { _lastOverlayPath = v; },
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
  get lastStats() { return _lastStats; },
  set lastStats(v) { _lastStats = v; },
  get sidebarOpen() { return _sidebarOpen; },
  set sidebarOpen(v) { _sidebarOpen = v; },
};
