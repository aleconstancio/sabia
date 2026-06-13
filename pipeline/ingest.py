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
from datetime import datetime
from typing import Optional

import requests
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

STAC_URLS = {
    "cbers4a": "http://www.dgi.inpe.br/lgi-stac/collections/CBERS4A_WPM_L4_DN/items",
    "sentinel2": "https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items",
    "landsat8": "https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l2-sr/items",
}


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "spaceeye"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


def insert_param(link: str) -> str:
    email = os.getenv("email_inpe") or os.getenv("EMAIL_INPE")
    if email:
        return f"{link}?email={email}"
    return link


def parse_item(item: dict, collection: str) -> Optional[dict]:
    try:
        assets = item.get("assets", {})
        
        metadata_assets = {}
        if collection == "cbers4a":
            for k in ("pan", "blue", "green", "red", "nir"):
                url = insert_param(assets.get(k, {}).get("href", ""))
                metadata_assets[k] = url
        elif collection == "sentinel2":
            mapping = {"B02": "blue", "B03": "green", "B04": "red", "B08": "nir", "SCL": "scl"}
            for stac_key, internal_key in mapping.items():
                metadata_assets[internal_key] = assets.get(stac_key, {}).get("href", "")
        elif collection in ("landsat8", "landsat9"):
            mapping = {"B2": "blue", "B3": "green", "B4": "red", "B5": "nir", "B6": "swir1", "B7": "swir2", "B8": "pan"}
            for stac_key, internal_key in mapping.items():
                metadata_assets[internal_key] = assets.get(stac_key, {}).get("href", "")
        
        footprint_coords = item["geometry"]["coordinates"]
        if item["geometry"]["type"] == "MultiPolygon":
            footprint_coords = footprint_coords[0][0]
        else:
            footprint_coords = footprint_coords[0]
        footprint_geojson = json.dumps({
            "type": "Polygon",
            "coordinates": [footprint_coords],
        })
        
        acquired_at = item["properties"].get("datetime") or item["properties"].get("created")
        if acquired_at:
            acquired_at = acquired_at.replace("Z", "+00:00")
        
        return {
            "id": item["id"],
            "collection": collection,
            "footprint_geojson": footprint_geojson,
            "cloud_cover": item["properties"].get("eo:cloud_cover", item["properties"].get("cloud_cover", 0)),
            "acquired_at": acquired_at,
            "metadata": json.dumps({"assets": metadata_assets}),
            "thumbnail_url": assets.get("thumbnail", {}).get("href", ""),
        }
    except (KeyError, IndexError, TypeError) as e:
        print(f"  Skipping item {item.get('id', 'unknown')}: {e}")
        return None


def ingest_collection(collection_id: str, max_pages: int = 600):
    stac_url = STAC_URLS.get(collection_id)
    if not stac_url:
        raise ValueError(f"Unknown collection: {collection_id}")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        total_inserted = 0
        total_skipped = 0
        next_url = stac_url
        
        for page in range(1, max_pages + 1):
            print(f"Fetching {collection_id} page {page}...")
            for attempt in range(3):
                try:
                    resp = requests.get(next_url, timeout=60)
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
            
            links = data.get("links", [])
            next_link = next((l["href"] for l in links if l.get("rel") == "next"), None)
            if next_link:
                next_url = next_link
            else:
                next_url = None
            
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
                # Detect which geometry column exists
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='images' AND column_name IN ('footprint','footprint_geojson')")
                geo_col = cursor.fetchone()
                geo_col = geo_col[0] if geo_col else 'footprint_geojson'

                if geo_col == 'footprint':
                    geo_insert = "footprint"
                    geo_template = "ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)"
                else:
                    geo_insert = "footprint_geojson"
                    geo_template = "%s"

                sql = f"""
                    INSERT INTO images (id, collection, {geo_insert}, cloud_cover, acquired_at, metadata, thumbnail_url)
                    VALUES %s
                    ON CONFLICT (id) DO UPDATE SET
                        cloud_cover = EXCLUDED.cloud_cover,
                        acquired_at = EXCLUDED.acquired_at,
                        metadata = EXCLUDED.metadata,
                        thumbnail_url = EXCLUDED.thumbnail_url,
                        updated_at = now()
                """
                template = f"(%s, %s, {geo_template}, %s, %s::timestamptz, %s::jsonb, %s)"
                execute_values(cursor, sql, records, template=template)
                conn.commit()
                total_inserted += len(records)
            
            total_skipped += len(features) - len(records)
            print(f"  Inserted {len(records)}, skipped {len(features) - len(records)}")
            
            if not next_url:
                break
        
        cursor.close()
        print(f"\nDone. Total inserted: {total_inserted}, skipped: {total_skipped}")
    finally:
        conn.close()


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
