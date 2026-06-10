export interface ImageResult {
  id: string;
  cloud_cover: number;
  thumbnail: string;
  acquired_at: string;
  coordinates?: number[][];
  collection?: string;
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
  coordinates: number[][];
}

export interface Monitor {
  id: string;
  name: string;
  coordinates: number[][];
  interval: number;
  lastChecked?: string;
  lastResult?: string;
}

export interface HistoryRecord {
  id: string;
  timestamp: string;
  imageId: string;
  product: string;
}

export interface TaskStatus {
  task_id: string;
  state: string;
  progress?: number;
  result?: {
    path: string;
    overlay_url: string;
    bounds: number[];
  };
}
