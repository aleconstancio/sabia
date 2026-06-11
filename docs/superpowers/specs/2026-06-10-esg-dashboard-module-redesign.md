# SpaceEye ESG Dashboard & Module Redesign

> **Date:** 2026-06-10
> **Status:** Approved
> **Approach:** Hybrid A+C — Dashboard-first with modular deep-dives

## Overview

Transform SpaceEye from a general-purpose satellite imagery tool into a comprehensive ESG monitoring platform. The redesign makes the Dashboard the primary landing page, adds domain-specific modules (Vegetation, Water, Fire, Soil, Climate), integrates LayerCake for rich visualizations, and adds ESG-specific features like alert thresholds, carbon stock estimation, and enhanced reporting.

**Target users:** ESG analysts + remote sensing specialists/scientists.

## Architecture

### Navigation & Information Architecture

**Current problem:** Map page is the only entry point. Dashboard is secondary. No ESG module structure.

**Proposed routes:**

```
/ (Dashboard)          ← NEW primary landing page
├── ESG Scorecard (top row)
├── Portfolio Grid (region cards with mini charts)
├── Alerts & Anomalies panel
└── Quick-action buttons → navigate to modules

/map (Map Analysis)    ← Existing, refined
├── Clean sidebar (Search → Results → Timeline)
├── ESG product presets (auto-selects best product per domain)
└── Floating panels REMOVED (consolidated into sidebar)

/modules/vegetation    ← Module deep-dive
/modules/water         ← Module deep-dive
/modules/fire          ← Module deep-dive
/modules/soil          ← Module deep-dive
/modules/climate       ← Module deep-dive
```

**Navigation bar:**
```
[Dashboard] [Map] [Vegetation] [Water] [Fire] [Soil] [Climate]
```

Each module view = map + module-specific sidebar + module-specific charts. The map is shared (same Leaflet instance), but the sidebar and panels adapt to the module context.

---

## Dashboard Components

The Dashboard is the ESG command center.

### Top Row — ESG Scorecard (4 cards)

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 12 Regions   │ │ 72% NDVI     │ │ 3 Alerts     │ │ 98% Coverage │
│ Monitored    │ │ Avg Health   │ │ Active       │ │ Data Quality │
│ [mini spark] │ │ [trend arrow]│ │ [color dot]  │ │ [progress]   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

Each card has a LayerCake sparkline showing the trend over the last 30 days.

### Middle — Portfolio Grid

Region cards with mini data visualizations:
- Thumbnail of last processed overlay
- Mini NDVI trend sparkline (LayerCake)
- Weather snapshot (temp + humidity)
- Soil health indicator (pH + organic carbon)
- Last analysis date
- Click → opens that region on `/map`

### Bottom — Alerts & Activity Feed

- Threshold alerts: "NDVI dropped below 0.3 in Region X"
- New imagery available for monitored regions
- Anomaly detection: sudden vegetation loss, water body change
- Activity log: "Profile saved", "Analysis exported"

### Empty state

When no profiles exist, the dashboard shows a call-to-action with an illustration guiding users to `/map` to create their first region.

---

## Module System (Vegetation, Water, Fire, Soil, Climate)

Each module is a focused view for a specific ESG domain. They share the same map infrastructure but have domain-specific sidebars and charts.

### Module Structure

```
/modules/{domain}
┌──────┬─────────────────────────────────────┐
│      │                                      │
│Module│         Shared Map                   │
│Panel │    (centered on user's region)       │
│      │                                      │
│Domain│    + Domain-specific overlay         │
│KPIs  │    + Timeline at bottom              │
│      │                                      │
│Charts│                                      │
│      │                                      │
└──────┴─────────────────────────────────────┘
```

### Module Details

| Module | KPI Cards | Charts | Overlay | Alerts |
|--------|-----------|--------|---------|--------|
| Vegetation | NDVI avg, biomass trend, deforestation risk, carbon stock | NDVI time-series, vegetation health distribution, multi-product comparison | NDVI/EVI/SAVI | Vegetation loss >20% |
| Water | Water body area, NDWI trend, moisture index, water change % | Water extent timeline, moisture levels, multi-product | NDWI/MNDWI | Water body shrinkage >15% |
| Fire | Burn scar area, NBR trend, fire risk score, recovery index | Burn severity timeline, fire risk heatmap, recovery trend | NBR | Fire risk >high |
| Soil | Soil health score, carbon stock, pH trend, composition | Soil property trends, composition donut, carbon stock bar | Soil data overlay | Carbon stock decline >10% |
| Climate | Temperature trend, precipitation anomaly, drought index, weather risk | 7-day forecast, historical trends, anomaly detection | Weather overlay | Drought, heavy rain, temp extremes |

### Module Sidebar Pattern (consistent across all)

1. **Quick Stats** — 3-4 KPI cards with sparklines
2. **Domain Chart** — main LayerCake time-series chart
3. **Composition** — breakdown chart (pie/donut for land cover, bar for soil properties)
4. **Actions** — Export report, View on map, Set alert threshold

### Navigation

Modules are accessible from the top nav bar AND from Dashboard cards (clicking a module badge on a region card navigates to that module).

---

## Map Page Refinement

### Current problems

Floating panels duplicate sidebar tabs. 11-product dropdown overwhelming. No ESG context.

### Proposed changes

**Remove floating panels** — Weather, Soil, Land Cover panels currently float on the right side of the map. Consolidate into sidebar only. The map becomes clean:

```
┌──────────────────────────────────────┐
│ Header (simplified)                   │
├──────┬───────────────────────────────┤
│Sidebar│                              │
│      │       Clean Leaflet Map       │
│Search│    + overlay only              │
│Result│                              │
│ESG   │                              │
│Stats │                              │
│Time- │                              │
│line  │                              │
└──────┴───────────────────────────────┘
```

**Sidebar restructure:**
1. **Search** — Product selector with ESG presets (auto-selects based on active module)
2. **Results** — Image gallery with filters
3. **ESG Quick Stats** — Mini KPI cards (weather, soil, land cover) when polygon is active
4. **Timeline** — LayerCake NDVI time-series (prominent, ~200px height)

### ESG Product Presets

When navigating from a module, the product dropdown auto-selects:
- Vegetation module → NDVI
- Water module → NDWI
- Fire module → NBR
- Soil module → TCI (for visual inspection)
- Climate module → TCI
- Default → NDVI

User can still manually change. Preset is just a smart default.

### Land Cover Area Display

When polygon is drawn, the sidebar shows a donut chart of land cover composition (Tree cover 45%, Cropland 30%, Built-up 15%, etc.) using the new backend zonal endpoint.

---

## Timeline & Charts (LayerCake Integration)

### Chart Components

Create `lib/charts/` with reusable chart components:

- `LineChart.svelte` — general time-series
- `AreaChart.svelte` — filled area charts
- `BarChart.svelte` — vertical/horizontal bars
- `DonutChart.svelte` — composition breakdown
- `Sparkline.svelte` — tiny inline trends

### Main NDVI Time-Series (Map Sidebar + Vegetation Module)

```
┌─────────────────────────────────────┐
│ NDVI Time-Series          [Export]  │
│ ┌─────────────────────────────────┐ │
│ │  ╭──╮    ╭─╮                    │ │
│ │ ╭╯  ╰╮  ╭╯ ╰╮   ╭──╮          │ │
│ │╭╯    ╰──╯   ╰──╯   ╰──╮       │ │
│ │╯                       ╰──     │ │
│ └─────────────────────────────────┘ │
│ Jan  Feb  Mar  Apr  May  Jun  Jul  │
│ ● 0.45 avg  ▲ +12% vs last month  │
└─────────────────────────────────────┘
```

- Line chart with area fill
- Trend line overlay (linear regression)
- Hover tooltip with date + value + image thumbnail
- Click point → processes that image
- Anomaly markers (red dots for values below threshold)
- Export button (CSV, JSON)

### Mini Sparklines (Dashboard cards + Module KPI cards)

```
┌──────────────┐
│ 72% NDVI     │
│ Avg Health   │
│ ▲ +5%  ───╮ │  ← 30-day sparkline
│            ╰│
└──────────────┘
```

- 60px wide, 24px tall
- Shows 30-day trend
- Color: green (up), red (down), gray (stable)

### Composition Charts (Module sidebars)

- **Donut chart** — Land cover classes (Tree, Water, Urban, etc.)
- **Horizontal bar** — Soil properties (pH, OC, sand, silt, clay)
- **Stacked bar** — Multi-product comparison (NDVI vs EVI vs SAVI over time)

### Comparison Charts (Change Detection)

- **Diverging bar chart** — NDVI change (blue = gain, red = loss)
- **Before/After sparklines** — Side-by-side trend comparison

---

## Monitoring & Alerts

### Alert Types

| Alert | Trigger | Data Source |
|-------|---------|-------------|
| Vegetation Loss | NDVI drops below threshold (default: 0.3) | Batch processing results |
| Water Body Change | NDWI changes >15% from baseline | NDWI time-series |
| Fire Risk | Risk score > "High" (NBR + weather) | New fire risk endpoint |
| Carbon Decline | SOC drops >10% from baseline | Soil data over time |
| New Imagery | New image available for monitored region | Existing monitor check |
| Weather Extreme | Temp >40°C, precipitation >50mm/day | Open-Meteo forecast |

### User-Configurable Thresholds

Each region profile gets threshold settings:

```
┌─────────────────────────────────────┐
│ Alert Settings — Amazonia Region     │
│                                     │
│ Vegetation Loss:  [▼ 20%] change   │
│ Water Change:     [▼ 15%] change   │
│ Fire Risk:        [▼ High] level   │
│ Carbon Decline:   [▼ 10%] change   │
│ Weather Alerts:   [✓] Enabled      │
│                                     │
│ [Save Thresholds]                   │
└─────────────────────────────────────┘
```

### Alert Delivery

- In-app notification bell (top nav) with unread count
- Dashboard alerts panel (red/yellow dots)
- Optional: Email alerts (future enhancement, backend webhook)

### Alert History

Stored in localStorage (like monitors), shows:
- Alert type, region, timestamp, value vs threshold
- "View" button → navigates to module with that region

### Anomaly Detection

Simple statistical approach:
- Calculate mean + std of NDVI over last 10 observations
- Flag any new observation outside μ ± 2σ as anomaly
- Show anomaly marker on timeline chart (red dot)

---

## ESG Reporting & Export

### Enhanced PDF Report

```
┌─────────────────────────────────────┐
│ SpaceEye ESG Report                 │
│ Region: Amazonia Conservation Area  │
│ Generated: 2026-06-10               │
│                                     │
│ ┌─ Map Snapshot ──────────────────┐ │
│ │ [Leaflet map screenshot]        │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ── Environmental Metrics ─────────  │
│ NDVI: 0.72 (+5% vs last month)     │
│ Water Index: 0.45                   │
│ Carbon Stock: 12.3 t/ha            │
│                                     │
│ ── Weather Summary ───────────────  │
│ Avg Temp: 26.5°C | Precip: 120mm   │
│                                     │
│ ── Soil Analysis ─────────────────  │
│ pH: 5.8 | Organic Carbon: 18 g/kg  │
│ Composition: 40% sand, 35% clay    │
│                                     │
│ ── Land Cover ────────────────────  │
│ Tree cover: 45% | Cropland: 30%    │
│ Built-up: 15% | Water: 10%        │
│                                     │
│ ── Time-Series Chart ─────────────  │
│ [NDVI trend chart embedded]        │
│                                     │
│ ── Alerts & Anomalies ────────────  │
│ 2 vegetation alerts in period      │
│                                     │
│ SpaceEye — Satellite ESG Monitoring │
└─────────────────────────────────────┘
```

**Backend change:** Enhanced PDF endpoint with reportlab templates, chart embedding, map snapshot.

### CSV Export (per module)

- Vegetation: date, NDVI, EVI, SAVI, biomass_estimate, anomaly_flag
- Water: date, NDWI, MNDWI, water_area_pct, moisture_index
- Fire: date, NBR, burn_severity, fire_risk_score
- Soil: date, pH, organic_carbon, sand, silt, clay, carbon_stock
- Climate: date, temperature, precipitation, humidity, drought_index

### JSON Export (full data package)

```json
{
  "region": "Amazonia Conservation",
  "coordinates": [...],
  "export_date": "2026-06-10T12:00:00Z",
  "metrics": {
    "vegetation": { "ndvi_timeseries": [...], "carbon_stock": 12.3 },
    "water": { "ndwi_timeseries": [...], "water_area_pct": 10 },
    "soil": { "ph": 5.8, "organic_carbon": 18 },
    "climate": { "avg_temp": 26.5, "precipitation": 120 }
  },
  "alerts": [...],
  "thresholds": { "ndvi_min": 0.3, "water_change_max": 0.15 }
}
```

### Multi-Region Comparison Export

Compare up to 5 regions side-by-side in a single report:
- Table of metrics across regions
- Overlaid time-series charts
- Ranking: "Best NDVI", "Highest carbon stock", etc.

### Export Access Points

- Dashboard: "Export All" button → exports all regions
- Module: "Export Module Data" → exports that module's data for current region
- Map: "Export Report" → exports single analysis with map snapshot

---

## Backend Quick Wins

These are changes to the existing backend that add significant value with minimal effort.

### 1. Land Cover Zonal Percentages

**New endpoint:** `POST /api/landcover/zonal-stats`

Samples the ESA WorldCover tile within the polygon using rasterio and returns area percentages per class.

~20 lines Python. Uses existing rasterio infrastructure.

### 2. Carbon Stock Estimation

**New endpoint:** `POST /api/carbon-stock`

Combines soil organic carbon (from SoilGrids) with NDVI-derived biomass proxy:
```
carbon_stock ≈ SOC + (NDVI_avg * biomass_factor)
```

~15 lines Python.

### 3. Fire Risk Score

**New endpoint:** `POST /api/fire-risk`

Combines NBR trend + weather data (temp, humidity, precipitation) into a simple risk score (Low/Medium/High/Critical).

~20 lines Python.

### 4. Enhanced PDF Reports

**Modified endpoint:** `POST /api/export/pdf`

Enhanced with:
- Map snapshot (Leaflet screenshot)
- All ESG metrics for the region
- Embedded charts (rendered as images)
- Land cover composition
- Weather/soil summaries
- Alert history

Reportlab template work.

---

## File Structure Changes

### New Files

```
apps/spaceeye-web/src/lib/charts/
├── LineChart.svelte
├── AreaChart.svelte
├── BarChart.svelte
├── DonutChart.svelte
├── Sparkline.svelte
└── index.ts

apps/spaceeye-web/src/routes/dashboard/
├── +page.svelte (major rewrite)
├── Scorecard.svelte
├── PortfolioGrid.svelte
├── RegionCard.svelte
├── AlertsFeed.svelte
└── ActivityLog.svelte

apps/spaceeye-web/src/routes/modules/
├── +layout.svelte (shared module layout)
├── vegetation/+page.svelte
├── water/+page.svelte
├── fire/+page.svelte
├── soil/+page.svelte
└── climate/+page.svelte

apps/spaceeye-web/src/lib/components/modules/
├── ModuleSidebar.svelte
├── ModuleKPI.svelte
├── ModuleChart.svelte
├── AlertThresholds.svelte
└── ModuleExport.svelte

apps/spaceeye-web/src/lib/components/alerts/
├── AlertBell.svelte
├── AlertPanel.svelte
├── AlertHistory.svelte
└── alerts.svelte.ts (store)

backend/api/
├── landcover_stats.py (new)
├── carbon_stock.py (new)
├── fire_risk.py (new)
└── enhanced_pdf.py (modified)
```

### Modified Files

```
apps/spaceeye-web/src/routes/+page.svelte → redirects to /dashboard
apps/spaceeye-web/src/lib/layout/Header.svelte → add module nav, alert bell
apps/spaceeye-web/src/lib/components/NdviTimeline.svelte → rewrite with LayerCake
apps/spaceeye-web/src/lib/components/TimeSlider.svelte → enhance with LayerCake
apps/spaceeye-web/src/lib/components/MonitoringPanel.svelte → add thresholds
apps/spaceeye-web/src/lib/stores/map.svelte.ts → add module context state
apps/spaceeye-web/src/lib/api/types.ts → add new types
apps/spaceeye-web/src/lib/api/client.ts → add new API calls
apps/spaceeye-web/package.json → add layercake dependency

backend/api/router.py → add new endpoints
backend/domain/products.py → add carbon stock, fire risk computations
```

---

## Implementation Order

### Phase 1: Foundation
1. Install LayerCake, create chart components
2. Restructure navigation (routes, header)
3. Clean up map page (remove floating panels, restructure sidebar)

### Phase 2: Dashboard
4. Build ESG Scorecard with sparklines
5. Build Portfolio Grid with region cards
6. Build Alerts & Activity Feed

### Phase 3: Modules
7. Create module layout and shared components
8. Vegetation module (NDVI time-series, carbon stock)
9. Water module (NDWI, water extent)
10. Fire module (NBR, risk scoring)
11. Soil module (properties, composition)
12. Climate module (weather trends, anomalies)

### Phase 4: Backend Quick Wins
13. Land cover zonal statistics endpoint
14. Carbon stock estimation endpoint
15. Fire risk score endpoint
16. Enhanced PDF template

### Phase 5: Monitoring & Export
17. Alert threshold system
18. Anomaly detection
19. CSV/JSON/PDF export enhancements
20. Multi-region comparison export

---

## Success Criteria

- Dashboard loads with ESG scorecard and portfolio grid within 2 seconds
- All 5 modules render with correct charts and data
- LayerCake charts are interactive (hover, click, tooltip)
- Alert thresholds trigger correctly
- PDF export includes all sections with embedded charts
- CSV/JSON export contains complete ESG data
- No regression in existing map functionality
- Mobile-responsive layout for all new views
