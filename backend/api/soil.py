import asyncio
import logging

from fastapi import APIRouter, HTTPException

from backend.api.deps import get_http_client
from backend.models.schemas import PolygonRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{lat}/{lon}")
async def get_soil(lat: float, lon: float):
    """Fetch soil data from ISRIC SoilGrids REST API (free, no key needed)."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(400, "Latitude must be in [-90, 90], longitude in [-180, 180]")
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {
        "lat": lat,
        "lon": lon,
        "property": ["phh2o", "oc", "nitrogen", "cec", "bdod", "cfvo", "sand", "silt", "clay", "wv0010", "wv0033", "wv1500"],
        "depth": "0-5cm",
        "value": "mean",
    }
    client = await get_http_client()
    resp = await client.get(url, params=params)
    if resp.status_code == 200:
        return resp.json()
    return {}


@router.post("/zonal")
async def soil_zonal(req: PolygonRequest):
    """Get average soil properties for a polygon area."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})

    bounds = poly.bounds
    step = min(bounds[2] - bounds[0], bounds[3] - bounds[1], 0.5) or 0.1

    points = []
    x = bounds[0]
    while x <= bounds[2]:
        y = bounds[1]
        while y <= bounds[3]:
            if poly.contains(shape({"type": "Point", "coordinates": [x, y]})):
                points.append({"lat": y, "lon": x})
            y += max(step, 0.1)
        x += max(step, 0.1)

    # Deterministic grid sampling for reproducible results
    sampled = points[:10]

    results = {"ph": [], "oc": [], "sand": [], "silt": [], "clay": []}
    client = await get_http_client()
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    property_map = [("ph", "phh2o"), ("oc", "oc"), ("sand", "sand"), ("silt", "silt"), ("clay", "clay")]

    async def _fetch_one(p):
        params = {"lat": p["lat"], "lon": p["lon"],
                  "property": ["phh2o", "oc", "sand", "silt", "clay"],
                  "depth": "0-5cm", "value": "mean"}
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        return None

    responses = await asyncio.gather(*[_fetch_one(p) for p in sampled], return_exceptions=True)
    responses = [r for r in responses if not isinstance(r, Exception)]

    for data in responses:
        if data is None:
            continue
        layers = data.get("properties", {}).get("layers", [])
        for k, layer in property_map:
            match = [x for x in layers if x["name"] == layer]
            if match:
                results[k].append(match[0]["depths"][0]["values"]["mean"])

    def avg(vals): return round(sum(vals) / len(vals), 2) if vals else None

    return {
        "source": "ISRIC SoilGrids",
        "points_sampled": len(sampled),
        "ph": avg(results["ph"]),
        "organic_carbon_gkg": avg(results["oc"]),
        "sand_pct": avg(results["sand"]),
        "silt_pct": avg(results["silt"]),
        "clay_pct": avg(results["clay"]),
        "note": "Averaged from multiple points within polygon",
    }
