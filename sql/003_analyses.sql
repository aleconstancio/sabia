-- Persistent analysis records for dashboard
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_id VARCHAR NOT NULL,
    collection VARCHAR NOT NULL,
    product VARCHAR NOT NULL,
    polygon JSONB NOT NULL,
    centroid JSONB,
    statistics JSONB,
    overlay_path VARCHAR,
    thumbnail_url VARCHAR,
    acquired_at TIMESTAMPTZ,
    cloud_cover DOUBLE PRECISION,
    weather JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    CONSTRAINT check_analyses_cloud_cover CHECK (cloud_cover >= 0 AND cloud_cover <= 100)
);

CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_product ON analyses (product);
CREATE INDEX IF NOT EXISTS idx_analyses_collection ON analyses (collection);
CREATE INDEX IF NOT EXISTS idx_analyses_image_id ON analyses (image_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_analyses_dedup ON analyses (image_id, product, (polygon::text));
