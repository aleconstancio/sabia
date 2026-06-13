# IMPORTANT: This migration delegates to the SQL files in sql/.
# The SQL files are the single source of truth for the schema.
# This migration simply executes them in order via Alembic.
"""Initial schema — delegates to SQL files

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
import os
from pathlib import Path
from typing import Sequence, Union

from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# SQL files to execute in order — single source of truth
SQL_FILES = [
    "sql/001_init.sql",
    "sql/003_analyses.sql",
    "sql/004_profiles.sql",
    "sql/005_triggers.sql",
]


def _find_sql_dir() -> Path:
    """Locate the sql/ directory relative to the project root."""
    # Walk up from alembic/versions/ to find sql/
    current = Path(__file__).resolve().parent
    for _ in range(5):
        sql_dir = current / "sql"
        if sql_dir.exists():
            return sql_dir
        current = current.parent
    raise FileNotFoundError("Could not find sql/ directory relative to migration file")


def upgrade() -> None:
    sql_dir = _find_sql_dir()
    for filename in SQL_FILES:
        sql_path = sql_dir / filename
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_path}")
        sql = sql_path.read_text(encoding="utf-8")
        op.execute(sql)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.execute("DROP TABLE IF EXISTS alert_rules CASCADE")
    op.execute("DROP TABLE IF EXISTS metric_timeseries CASCADE")
    op.execute("DROP TABLE IF EXISTS processing_tasks CASCADE")
    op.execute("DROP TABLE IF EXISTS region_profiles CASCADE")
    op.execute("DROP TABLE IF EXISTS analyses CASCADE")
    op.execute("DROP TABLE IF EXISTS images CASCADE")
    op.execute("DROP FUNCTION IF EXISTS update_timestamp()")
