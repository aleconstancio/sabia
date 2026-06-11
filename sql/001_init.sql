-- SpaceEye database schema
-- Uses PostGIS when available, falls back to JSON geometry otherwise.

DO $$
BEGIN
  CREATE EXTENSION IF NOT EXISTS postgis;
EXCEPTION WHEN OTHERS THEN
  RAISE NOTICE 'PostGIS not available — using JSON geometry fallback';
END $$;

CREATE TABLE IF NOT EXISTS images (
    id VARCHAR PRIMARY KEY,
    collection VARCHAR NOT NULL,
    cloud_cover DOUBLE PRECISION,
    acquired_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}',
    thumbnail_url VARCHAR,
    CONSTRAINT check_cloud_cover CHECK (cloud_cover >= 0 AND cloud_cover <= 100)
);

-- Add geometry column when PostGIS is available
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
    ALTER TABLE images ADD COLUMN IF NOT EXISTS footprint GEOMETRY(POLYGON, 4326);
    CREATE INDEX IF NOT EXISTS idx_images_footprint ON images USING GIST (footprint);
  ELSE
    ALTER TABLE images ADD COLUMN IF NOT EXISTS footprint_geojson TEXT;
    RAISE NOTICE 'PostGIS not found: spatial queries will use Python-side filtering';
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_images_collection ON images (collection);
CREATE INDEX IF NOT EXISTS idx_images_acquired_at ON images (acquired_at DESC);
