/**
 * UI state — modal visibility, sidebar, comparison mode.
 */
import type { WeatherData } from '$lib/api/types';

let _showLegend = $state(false);
let _showPolygonModal = $state(false);
let _showImageGallery = $state(false);
let _showProcessingViewer = $state(false);
let _showComparison = $state(false);
let _sidebarOpen = $state(true);
let _lastWeatherData = $state<WeatherData | null>(null);

export const uiState = {
  get showLegend() { return _showLegend; },
  set showLegend(v) { _showLegend = v; },
  get showPolygonModal() { return _showPolygonModal; },
  set showPolygonModal(v) { _showPolygonModal = v; },
  get showImageGallery() { return _showImageGallery; },
  set showImageGallery(v) { _showImageGallery = v; },
  get showProcessingViewer() { return _showProcessingViewer; },
  set showProcessingViewer(v) { _showProcessingViewer = v; },
  get showComparison() { return _showComparison; },
  set showComparison(v) { _showComparison = v; },
  get sidebarOpen() { return _sidebarOpen; },
  set sidebarOpen(v) { _sidebarOpen = v; },
  get lastWeatherData() { return _lastWeatherData; },
  set lastWeatherData(v) { _lastWeatherData = v; },
};
