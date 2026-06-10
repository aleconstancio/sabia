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
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_product ON analyses (product);
CREATE INDEX IF NOT EXISTS idx_analyses_collection ON analyses (collection);

-- Named regions for neighborhood ecology analysis
CREATE TABLE IF NOT EXISTS regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    description TEXT,
    polygon JSONB NOT NULL,
    centroid JSONB,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_regions_name ON regions (name);
