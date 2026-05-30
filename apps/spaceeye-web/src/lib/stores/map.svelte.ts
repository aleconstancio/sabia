let _map: any = $state(null);
let _polygonCoords = $state<number[][][] | null>(null);
let _polygonCentroid = $state<{lat: number; lon: number} | null>(null);
let _results = $state<any[]>([]);
let _selectedProduct = $state('NDVI');
let _showLegend = $state(false);
let _hasOverlay = $state(false);
let _rasterOverlay: any = $state(null);
let _showPolygonModal = $state(false);
let _showImageGallery = $state(false);
let _showProcessingViewer = $state(false);
let _showComparison = $state(false);
let _isLoading = $state(false);
let _processingProgress = $state(0);
let _processingPhase = $state('');
let _taskId = $state('');
let _searchError = $state('');
let _comparisonFirst = $state<any>(null);
let _comparisonSecond = $state<any>(null);
let _selectedIds = $state<string[]>([]);
let _lastWeatherData = $state<any>(null);
let _lastOverlayPath = $state('');
let _selectedCollection = $state('cbers4a');

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
};
