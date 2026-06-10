-- Region profiles: fused multi-source ecology data
CREATE TABLE IF NOT EXISTS region_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR,
    polygon JSONB NOT NULL,
    centroid JSONB,
    weather_data JSONB,
    soil_data JSONB,
    landcover_data JSONB,
    satellite_data JSONB,
    tags TEXT[] DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON region_profiles (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_name ON region_profiles (name);
