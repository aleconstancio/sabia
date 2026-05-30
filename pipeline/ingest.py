#!/usr/bin/env python3
"""
Ingest satellite image catalog from INPE STAC API into PostGIS.

Usage:
    python pipeline/ingest.py --collection cbers4a [--collection amazonia1]
    
Run via cron/systemd timer daily.
"""

import argparse
import os
import sys
import json
import time
from datetime import datetime, timezone
from typing import Optional

import requests
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

STAC_URLS = {
    "cbers4a": "http://www.dgi.inpe.br/lgi-stac/collections/CBERS4A_WPM_L4_DN/items",
    # Add more collections as STAC endpoints become available
    # "amazonia1": "...",
}


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "spaceeye"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def insert_param(link: str) -> str:
    email = os.getenv("email_inpe") or os.getenv("EMAIL_INPE")
    if email:
        return f"{link}?email={email}"
    return link


def parse_item(item: dict, collection: str) -> Optional[dict]:
    try:
        footprint_coords = item["geometry"]["coordinates"][0]
        footprint_geojson = json.dumps({
            "type": "Polygon",
            "coordinates": [footprint_coords],
        })
        
        assets = item.get("assets", {})
        metadata = {
            "assets": {
                "pan": insert_param(assets.get("pan", {}).get("href", "")),
                "blue": insert_param(assets.get("blue", {}).get("href", "")),
                "green": insert_param(assets.get("green", {}).get("href", "")),
                "red": insert_param(assets.get("red", {}).get("href", "")),
                "nir": insert_param(assets.get("nir", {}).get("href", "")),
            }
        }
        
        acquired_at = item["properties"].get("datetime") or item["properties"].get("created")
        if acquired_at:
            acquired_at = acquired_at.replace("Z", "+00:00")
        
        return {
            "id": item["id"],
            "collection": collection,
            "footprint_geojson": footprint_geojson,
            "cloud_cover": item["properties"].get("cloud_cover", 0),
            "acquired_at": acquired_at,
            "metadata": json.dumps(metadata),
            "thumbnail_url": assets.get("thumbnail", {}).get("href", ""),
        }
    except (KeyError, IndexError, TypeError) as e:
        print(f"  Skipping item {item.get('id', 'unknown')}: {e}")
        return None


def ingest_collection(collection_id: str, max_pages: int = 600):
    stac_url = STAC_URLS.get(collection_id)
    if not stac_url:
        print(f"Unknown collection: {collection_id}")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    total_inserted = 0
    total_skipped = 0
    
    for page in range(1, max_pages + 1):
        print(f"Fetching {collection_id} page {page}...")
        for attempt in range(3):
            try:
                resp = requests.get(
                    stac_url,
                    params={"page": page, "limit": 1000},
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                features = data.get("features", [])
                break
            except requests.RequestException:
                if attempt == 2:
                    print(f"  Error on page {page} after 3 attempts")
                    conn.rollback()
                    return
                time.sleep(5)
        
        if not features:
            print("  No more features. Done.")
            break
        
        records = []
        for item in features:
            parsed = parse_item(item, collection_id)
            if parsed:
                records.append((
                    parsed["id"],
                    parsed["collection"],
                    parsed["footprint_geojson"],
                    parsed["cloud_cover"],
                    parsed["acquired_at"],
                    parsed["metadata"],
                    parsed["thumbnail_url"],
                ))
        
        if records:
            sql = """
                INSERT INTO images (id, collection, footprint, cloud_cover, acquired_at, metadata, thumbnail_url)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    cloud_cover = EXCLUDED.cloud_cover,
                    acquired_at = EXCLUDED.acquired_at,
                    metadata = EXCLUDED.metadata,
                    thumbnail_url = EXCLUDED.thumbnail_url,
                    updated_at = now()
            """
            execute_values(
                cursor,
                sql,
                records,
                template="(%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s, %s::timestamptz, %s::jsonb, %s)",
            )
            conn.commit()
            total_inserted += len(records)
        
        total_skipped += len(features) - len(records)
        print(f"  Inserted {len(records)}, skipped {len(features) - len(records)}")
    
    cursor.close()
    conn.close()
    print(f"\nDone. Total inserted: {total_inserted}, skipped: {total_skipped}")


def main():
    parser = argparse.ArgumentParser(description="Ingest STAC catalog into PostGIS")
    parser.add_argument("--collection", action="append", dest="collections", 
                        choices=list(STAC_URLS.keys()), required=True,
                        help="Collection(s) to ingest")
    
    args = parser.parse_args()
    
    for collection in args.collections:
        print(f"\n{'='*60}")
        print(f"Ingesting {collection}...")
        print(f"{'='*60}")
        ingest_collection(collection)


if __name__ == "__main__":
    main()
