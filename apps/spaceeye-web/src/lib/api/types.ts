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
