CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS images (
    id VARCHAR PRIMARY KEY,
    collection VARCHAR NOT NULL,
    footprint GEOMETRY(POLYGON, 4326) NOT NULL,
    cloud_cover DOUBLE PRECISION,
    acquired_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}',
    thumbnail_url VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_images_footprint ON images USING GIST (footprint);
CREATE INDEX IF NOT EXISTS idx_images_collection ON images (collection);
CREATE INDEX IF NOT EXISTS idx_images_acquired_at ON images (acquired_at DESC);
