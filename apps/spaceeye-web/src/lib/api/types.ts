// Fields matching backend API use snake_case.
// Frontend-only fields use camelCase.

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

export interface WeatherApiResponse {
  current?: {
    temperature_2m?: number;
    apparent_temperature?: number;
    relative_humidity_2m?: number;
    precipitation?: number;
    weather_code?: number;
    soil_moisture_0_to_7cm?: number;
  };
  daily?: {
    precipitation_sum?: number[];
    temperature_2m_max?: number[];
    temperature_2m_min?: number[];
  };
}

export interface SoilApiResponse {
  properties?: Array<{
    name: string;
    depths: Array<{
      label: string;
      values?: Record<string, number>;
    }>;
  }>;
}

export interface LandCoverData {
  source: string;
  resolution: number;
  classes?: Record<string, number>;
  tile_url?: string;
  polygon_area_m2?: number;
  sampled_points?: number;
  class_percentages?: Record<string, number>;
}

export interface ProcessingStats {
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
  p10?: number;
  p90?: number;
  median?: number;
  nodata_pct?: number;
  pixel_count?: number;
}

export interface WeatherData {
  temperature: number;
  precipitation: number;
  wind_speed: number;
  humidity: number;
  description?: string;
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
  stats?: ProcessingStats;
}

export interface TaskStatus {
  task_id: string;
  status: string;
  progress: number;
  phase: string;
  result?: Record<string, unknown>;
  error?: string;
}

export interface StatsData extends ProcessingStats {
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
    stats: ProcessingStats;
  } | null;
  created_at: string | null;
}

export interface LandCoverStats {
  source: string;
  resolution: string;
  classes: { id: number; name: string; color: string; pixels: number; percentage: number }[];
  total_pixels: number;
}

export interface CarbonStock {
  carbon_stock_t_ha: number;
  soil_organic_carbon: number;
  biomass_estimate: number;
  ndvi_avg: number;
  weather_summary: {
    temperature: number | null;
    humidity: number | null;
    precipitation: number | null;
  };
  soil_summary: {
    organic_carbon_gkg: number;
    nitrogen: number;
  };
}

export interface FireRisk {
  fire_risk_score: number;
  risk_level: 'low' | 'moderate' | 'high' | 'extreme';
  factors: {
    temperature_score: number;
    humidity_score: number;
    precipitation_score: number;
    vegetation_score: number;
    drought_days: number;
  };
  weather_summary: {
    temperature: number;
    humidity: number;
    precipitation_7d: number;
  };
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
