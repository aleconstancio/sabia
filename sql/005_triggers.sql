-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to images table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_images_updated_at') THEN
        CREATE TRIGGER trg_images_updated_at
        BEFORE UPDATE ON images
        FOR EACH ROW
        EXECUTE FUNCTION update_timestamp();
    END IF;
END $$;

-- Apply to region_profiles table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_profiles_updated_at') THEN
        CREATE TRIGGER trg_profiles_updated_at
        BEFORE UPDATE ON region_profiles
        FOR EACH ROW
        EXECUTE FUNCTION update_timestamp();
    END IF;
END $$;

-- Processing task results table
CREATE TABLE IF NOT EXISTS processing_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR NOT NULL UNIQUE,
    image_id VARCHAR,
    product VARCHAR NOT NULL,
    polygon JSONB,
    status VARCHAR NOT NULL DEFAULT 'pending',
    result_path TEXT,
    statistics JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_processing_tasks_status ON processing_tasks (status);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_image_id ON processing_tasks (image_id);

-- ESG metric time series
CREATE TABLE IF NOT EXISTS metric_timeseries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES region_profiles(id) ON DELETE CASCADE,
    metric_name VARCHAR NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT now(),
    source VARCHAR,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_metric_timeseries_profile ON metric_timeseries (profile_id, metric_name, recorded_at DESC);

-- User-defined alert rules
CREATE TABLE IF NOT EXISTS alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES region_profiles(id) ON DELETE CASCADE,
    metric VARCHAR NOT NULL,
    operator VARCHAR NOT NULL CHECK (operator IN ('<', '<=', '>', '>=', '==')),
    threshold_value DOUBLE PRECISION NOT NULL,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_alert_rules_profile ON alert_rules (profile_id);
