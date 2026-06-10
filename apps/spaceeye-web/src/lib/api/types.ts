export interface ImageResult {
  id: string;
  collection: string;
  cloud_cover: number | null;
  acquired_at: string;
  thumbnail_url: string | null;
  footprint: any;
}

export interface SoilData {
  sand?: number;
  clay?: number;
  silt?: number;
  organic_carbon?: number;
  ph?: number;
  [key: string]: number | undefined;
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
  stats?: any;
}

export interface TaskStatus {
  task_id: string;
  status: string;
  progress: number;
  phase: string;
  result?: any;
  error?: string;
}
