export interface ImageResult {
  id: string;
  collection: string;
  cloud_cover: number | null;
  acquired_at: string;
  thumbnail_url: string | null;
  footprint: Record<string, unknown>;
}

export interface SoilData {
  sand?: number;
  clay?: number;
  silt?: number;
  organic_carbon?: number;
  ph?: number;
  [key: string]: number | undefined;
}

export interface SoilZonalResponse {
  source?: string;
  ph?: number;
  organic_carbon_gkg?: number;
  sand_pct?: number;
  silt_pct?: number;
  clay_pct?: number;
  points_sampled?: number;
  note?: string;
  [key: string]: unknown;
}

export interface WeatherData {
  temperature: number;
  precipitation: number;
  wind_speed: number;
  humidity: number;
  description?: string;
}

export interface LandCoverData {
  class_id: number;
  class_name: string;
  area_pct: number;
}

export interface Bookmark {
  id: string;
  name: string;
  coords: number[][][];
  created_at: string;
}

export interface Monitor {
  id: string;
  bookmarkId: string;
  bookmarkName: string;
  polygonCoords: number[][][];
  product: string;
  minCloudCover: number;
  active: boolean;
  lastChecked: string | null;
  lastResult: string | null;
}

export interface AnalysisRecord {
  id: string;
  timestamp: string;
  imageId: string;
  product: string;
  collection: string;
  cloudCover: number | null;
  polygonCoords: number[][][];
  centroid: { lat: number; lon: number } | null;
  stats?: Record<string, unknown>;
}

export interface TaskStatus {
  task_id: string;
  status: string;
  progress: number;
  phase: string;
  result?: Record<string, unknown>;
  error?: string;
}

export interface StatsData {
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
  histogram?: {
    deciles?: number[];
    p10?: number;
    p90?: number;
  };
  [key: string]: unknown;
}

export interface SavedAnalysis {
  id: string;
  image_id: string;
  collection: string;
  product: string;
  polygon: { type: string; coordinates: number[][][] };
  centroid: { lat: number; lon: number } | null;
  statistics: Record<string, unknown> | null;
  acquired_at: string | null;
  cloud_cover: number | null;
  created_at: string | null;
}

export interface RegionProfile {
  id: string;
  name: string | null;
  polygon: { type: string; coordinates: number[][][] };
  centroid: { lat: number; lon: number } | null;
  weather_summary: {
    temperature: number | null;
    humidity: number | null;
    precipitation: number | null;
    weather_code: number | null;
  } | null;
  soil_summary: {
    phh2o: number | null;
    oc: number | null;
    sand: number | null;
    clay: number | null;
  } | null;
  landcover_summary: {
    source: string;
    classes: Record<number, string>;
    tile_url: string;
  } | null;
  satellite_data: {
    product: string;
    stats: Record<string, unknown>;
  } | null;
  created_at: string | null;
}

export interface LandCoverStats {
  source: string;
  classes: { code: number; name: string; area_pct: number }[];
  total_area_km2: number;
  centroid: { lat: number; lon: number };
}

export interface CarbonStock {
  carbon_stock_t_ha: number;
  soil_organic_carbon: number;
  biomass_estimate: number;
  ndvi_avg: number;
}

export interface FireRisk {
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_score: number;
  nbr_trend: number;
  temperature_factor: number;
  humidity_factor: number;
  precipitation_factor: number;
}

export interface Alert {
  id: string;
  type: string;
  message: string;
  region: string;
  timestamp: string;
  read: boolean;
}

export interface AlertThreshold {
  id: string;
  regionId: string;
  regionName: string;
  vegetation_loss_pct: number;
  water_change_pct: number;
  fire_risk_level: string;
  carbon_decline_pct: number;
  weather_alerts: boolean;
  created_at: string;
}

export interface ESGExportData {
  region: string;
  coordinates: number[][][];
  export_date: string;
  metrics: {
    vegetation?: { ndvi_timeseries: { date: string; value: number }[]; carbon_stock: number };
    water?: { ndwi_timeseries: { date: string; value: number }[]; water_area_pct: number };
    fire?: { nbr_timeseries: { date: string; value: number }[]; fire_risk: string };
    soil?: { ph: number; organic_carbon: number; sand: number; clay: number; carbon_stock: number };
    climate?: { avg_temp: number; precipitation: number; humidity: number };
  };
  alerts: { type: string; message: string; timestamp: string }[];
  thresholds: AlertThreshold;
}
