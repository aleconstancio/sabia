# ESG Features

> Environmental, Social, and Governance monitoring capabilities in Horus.

## Overview

Horus provides a comprehensive ESG monitoring platform built on satellite imagery, weather data, soil properties, and land cover analysis. The system is designed for ESG analysts and remote sensing specialists who need to monitor environmental conditions across multiple regions.

## ESG Dashboard

The dashboard is the primary landing page (`/dashboard`), providing a portfolio-level overview of all monitored regions.

### ESG Scorecard

Four key metrics displayed at the top:

| Metric | Description | Data Source |
|--------|-------------|-------------|
| **Regions Monitored** | Total saved region profiles | `region_profiles` table |
| **Avg NDVI Health** | Mean vegetation index across all regions | Satellite processing results |
| **Active Alerts** | Number of triggered alert thresholds | localStorage alert store |
| **Avg Temperature** | Mean temperature across all regions | Open-Meteo API |

Each card includes a 30-day sparkline trend indicator and trend percentage.

### Portfolio Grid

Region cards displaying:
- Region name and creation date
- Weather snapshot (temperature, humidity)
- Soil health indicators (pH, organic carbon)
- Last analysis product badge
- NDVI average value
- Click → navigates to map view for that region

## Domain Modules

Five domain-specific modules, each accessible from the navigation bar:

### Vegetation Module (`/modules/vegetation`)

**Product**: NDVI (Normalized Difference Vegetation Index)

**KPI Cards**:
- NDVI Average — mean vegetation index for the region
- Carbon Stock — estimated t/ha from soil organic carbon + biomass proxy
- Biomass Estimate — NDVI-derived biomass in t/ha

**Charts**:
- NDVI time-series (interactive LayerCake area chart)
- Multi-product comparison (NDVI vs EVI vs SAVI)

**Alert Thresholds**:
- Vegetation Loss — percentage change threshold (default: 20%)
- Carbon Decline — percentage change threshold (default: 10%)

### Water Module (`/modules/water`)

**Product**: NDWI (Normalized Difference Water Index)

**KPI Cards**:
- Water Area — estimated water body extent
- NDWI Trend — water index trend over time
- Moisture Index — vegetation moisture content

**Charts**:
- Water extent timeline
- Multi-product comparison (NDWI vs MNDWI)

**Alert Thresholds**:
- Water Change — percentage change threshold (default: 15%)

### Fire Module (`/modules/fire`)

**Product**: NBR (Normalized Burn Ratio)

**KPI Cards**:
- Risk Level — low/medium/high/critical classification
- Risk Score — numerical score (0-100)
- NBR Trend — burn ratio trend

**Charts**:
- Fire risk score breakdown (temperature, humidity, precipitation factors)
- Burn severity timeline

**Alert Thresholds**:
- Fire Risk Level — trigger threshold (default: high)

### Soil Module (`/modules/soil`)

**Product**: TCI (True Color Image) for visual inspection

**KPI Cards**:
- Soil Health Score — composite indicator
- pH Level — soil acidity/alkalinity
- Organic Carbon — g/kg concentration

**Charts**:
- Soil property trends
- Composition breakdown (sand/silt/clay donut chart)

### Climate Module (`/modules/climate`)

**Product**: TCI for visual context

**KPI Cards**:
- Temperature — current and trend
- Precipitation — current and forecast
- Drought Index — derived from weather patterns

**Charts**:
- 7-day temperature/precipitation forecast
- Historical weather trends
- Anomaly detection

## Multi-Source Data Fusion

When a region is selected, Horus fetches data from multiple sources in parallel:

### Weather (Open-Meteo)

- **Endpoint**: `GET /api/weather/{lat}/{lon}`
- **Data**: Temperature, humidity, precipitation, soil moisture, 7-day forecast
- **Cost**: Free, no API key required
- **Update**: Real-time

### Soil (ISRIC SoilGrids)

- **Endpoint**: `POST /api/soil/zonal`
- **Data**: pH, organic carbon, sand/silt/clay composition, nitrogen, CEC
- **Method**: Samples multiple points within polygon, returns averaged values
- **Resolution**: 250m

### Land Cover (ESA WorldCover)

- **Endpoint**: `POST /api/landcover/zonal`
- **Data**: Land cover class percentages (Tree cover, Cropland, Water, etc.)
- **Resolution**: 10m
- **Source**: ESA WorldCover 2021

### Carbon Stock (Computed)

- **Endpoint**: `POST /api/carbon-stock`
- **Formula**: `carbon_stock = SOC * 0.58 + NDVI_avg * biomass_factor`
- **Inputs**: Soil organic carbon (from SoilGrids) + NDVI average (from satellite)
- **Note**: NDVI component is estimated when no recent processing exists

### Fire Risk (Computed)

- **Endpoint**: `POST /api/fire-risk`
- **Formula**: Weighted combination of NBR trend, temperature, humidity, precipitation
- **Inputs**: Weather data (Open-Meteo) + NBR trend (estimated)
- **Output**: Risk level (low/medium/high/critical) + numerical score

## Alert System

### Alert Types

| Alert | Trigger | Default Threshold |
|-------|---------|-------------------|
| Vegetation Loss | NDVI drops below baseline | 20% change |
| Water Body Change | NDWI changes from baseline | 15% change |
| Fire Risk | Risk score exceeds level | High |
| Carbon Decline | SOC drops from baseline | 10% change |
| Weather Extreme | Temperature or precipitation exceeds limits | 40°C / 50mm |
| New Imagery | New satellite image available for region | — |

### Configuration

Each region profile has configurable alert thresholds:

```json
{
  "vegetation_loss_pct": 20,
  "water_change_pct": 15,
  "fire_risk_level": "high",
  "carbon_decline_pct": 10,
  "weather_alerts": true
}
```

Thresholds are stored in localStorage and configurable via the module sidebar.

### Notification Delivery

- **In-app**: Alert bell in header with unread count badge
- **Dashboard**: Active alerts panel with color-coded indicators
- **Future**: Email alerts via webhook (planned)

## ESG Reporting

### PDF Reports

Enhanced PDF export with:
- Map snapshot
- Environmental metrics (NDVI, water index, carbon stock)
- Weather summary
- Soil analysis
- Land cover composition
- Time-series chart
- Alert history

### CSV Export

Per-module data export with domain-specific columns:
- **Vegetation**: date, NDVI, EVI, SAVI, biomass_estimate, anomaly_flag
- **Water**: date, NDWI, MNDWI, water_area_pct, moisture_index
- **Fire**: date, NBR, burn_severity, fire_risk_score
- **Soil**: date, pH, organic_carbon, sand, silt, clay, carbon_stock
- **Climate**: date, temperature, precipitation, humidity, drought_index

### JSON Export

Full data package including all metrics, alerts, and thresholds for a region.

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Dashboard scorecard | ✅ Complete | |
| Portfolio grid | ✅ Complete | |
| Vegetation module | ✅ Complete | NDVI processing, carbon stock |
| Water module | ✅ Complete | NDWI processing |
| Fire module | ✅ Complete | Risk scoring from weather + NBR |
| Soil module | ✅ Complete | pH, OC, composition from SoilGrids |
| Climate module | ✅ Complete | Weather trends from Open-Meteo |
| Alert system | ✅ Complete | Threshold-based with bell notification |
| PDF export | ✅ Complete | Enhanced with ESG metrics |
| CSV export | ⚠️ Stub | Returns 501 — needs real data pipeline |
| JSON export | ⚠️ Stub | Returns 501 — needs real data pipeline |
| Carbon stock | ⚠️ Partial | SOC is real, NDVI is estimated |
| Fire risk | ⚠️ Partial | Weather is real, NBR is estimated |
| Land cover stats | ⚠️ Stub | Returns 501 — needs rasterio sampling |
| Time-series storage | ✅ Schema ready | `metric_timeseries` table created |
| Alert rules persistence | ✅ Schema ready | `alert_rules` table created |
