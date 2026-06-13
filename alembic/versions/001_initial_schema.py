# IMPORTANT: This migration duplicates the SQL init files in sql/. Any schema changes must be applied to BOTH locations. Consider consolidating to Alembic-only.
"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id VARCHAR PRIMARY KEY,
            collection VARCHAR NOT NULL,
            cloud_cover DOUBLE PRECISION NOT NULL DEFAULT 0,
            acquired_at TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now(),
            metadata JSONB DEFAULT '{}',
            thumbnail_url VARCHAR,
            CONSTRAINT check_cloud_cover CHECK (cloud_cover >= 0 AND cloud_cover <= 100)
        )
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
                ALTER TABLE images ADD COLUMN IF NOT EXISTS footprint GEOMETRY(POLYGON, 4326);
                CREATE INDEX IF NOT EXISTS idx_images_footprint ON images USING GIST (footprint);
            ELSE
                ALTER TABLE images ADD COLUMN IF NOT EXISTS footprint_geojson TEXT;
            END IF;
        END $$
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_images_collection ON images (collection)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_images_acquired_at ON images (acquired_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_images_collection_acquired ON images (collection, acquired_at DESC)")

    op.execute("""
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
        )
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses (created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_analyses_product ON analyses (product)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_analyses_collection ON analyses (collection)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_analyses_image_id ON analyses (image_id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_analyses_dedup ON analyses (image_id, product, (polygon::text))")

    op.execute("""
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
        )
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON region_profiles (created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_profiles_name ON region_profiles (name)")

    op.execute("""
        CREATE OR REPLACE FUNCTION update_timestamp() RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_images_updated_at') THEN
                CREATE TRIGGER trg_images_updated_at
                BEFORE UPDATE ON images
                FOR EACH ROW
                EXECUTE FUNCTION update_timestamp();
            END IF;
        END $$
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_profiles_updated_at') THEN
                CREATE TRIGGER trg_profiles_updated_at
                BEFORE UPDATE ON region_profiles
                FOR EACH ROW
                EXECUTE FUNCTION update_timestamp();
            END IF;
        END $$
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_analyses_updated_at') THEN
                CREATE TRIGGER trg_analyses_updated_at
                BEFORE UPDATE ON analyses
                FOR EACH ROW
                EXECUTE FUNCTION update_timestamp();
            END IF;
        END $$
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS processing_tasks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            task_id VARCHAR NOT NULL UNIQUE,
            image_id VARCHAR REFERENCES images(id) ON DELETE SET NULL,
            product VARCHAR NOT NULL,
            polygon JSONB,
            status VARCHAR NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
            result_path TEXT,
            statistics JSONB,
            error TEXT,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now(),
            completed_at TIMESTAMPTZ
        )
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_processing_tasks_status ON processing_tasks (status)")

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_processing_tasks_updated_at') THEN
                CREATE TRIGGER trg_processing_tasks_updated_at
                BEFORE UPDATE ON processing_tasks
                FOR EACH ROW
                EXECUTE FUNCTION update_timestamp();
            END IF;
        END $$
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_processing_tasks_image_id ON processing_tasks (image_id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS metric_timeseries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            profile_id UUID REFERENCES region_profiles(id) ON DELETE CASCADE,
            metric_name VARCHAR NOT NULL,
            value DOUBLE PRECISION NOT NULL,
            recorded_at TIMESTAMPTZ DEFAULT now(),
            source VARCHAR,
            metadata JSONB
        )
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_metric_timeseries_profile ON metric_timeseries (profile_id, metric_name, recorded_at DESC)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS alert_rules (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            profile_id UUID REFERENCES region_profiles(id) ON DELETE CASCADE,
            metric VARCHAR NOT NULL,
            operator VARCHAR NOT NULL CHECK (operator IN ('<', '<=', '>', '>=', '==')),
            threshold_value DOUBLE PRECISION NOT NULL,
            enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMPTZ DEFAULT now()
        )
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_alert_rules_profile ON alert_rules (profile_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS alert_rules CASCADE")
    op.execute("DROP TABLE IF EXISTS metric_timeseries CASCADE")
    op.execute("DROP TABLE IF EXISTS processing_tasks CASCADE")
    op.execute("DROP TABLE IF EXISTS region_profiles CASCADE")
    op.execute("DROP TABLE IF EXISTS analyses CASCADE")
    op.execute("DROP TABLE IF EXISTS images CASCADE")
    op.execute("DROP FUNCTION IF EXISTS update_timestamp()")
