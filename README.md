# 🚨 Aapda Setu (आपदा सेतु)
### AI-Powered Disaster Early Warning & Rescue Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![ML](https://img.shields.io/badge/ML-XGBoost%20%7C%20SGD-brightgreen.svg)](https://xgboost.readthedocs.io/)
[![GIS](https://img.shields.io/badge/GIS-GeoPandas%20%7C%20Shapely-orange.svg)](https://geopandas.org/)
[![Routing](https://img.shields.io/badge/Routing-NetworkX%20%7C%20OSMnx-purple.svg)](https://networkx.org/)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg)](https://ai.google.dev/)

---

## 📌 Executive Summary

**Aapda Setu (आपदा सेतु)** is an end-to-end, location-aware decision-support platform designed for **District Disaster Management Authorities (DDMAs)**, **NDRF/SDRF Incident Commanders**, and **at-risk citizens**. 

During extreme monsoon events, river overflow, urban flooding, and landslides, disaster management teams receive fragmented data from isolated sources (weather radar, CWC river gauges, satellite inundation masks, demographic records, and static municipal maps). **Aapda Setu** ingests these heterogeneous streams in real time and synthesizes them into actionable tactical directives in seconds.

---

## 🌟 Key Capabilities & Features

### 1. 📍 Zero-Hardcoding Dynamic Location Pipeline
- Fully data-driven: changing or searching a location instantly triggers dynamic geospatial, meteorological, and hydrological re-evaluation.
- Pre-configured disaster hotspots with live telemetry:
  - **Kolkata, West Bengal** (Hooghly River Reach)
  - **Varanasi, Uttar Pradesh** (Ganges Waterfront Sector)
  - **Nagaon, Assam** (Kolong Riverbank & Brahmaputra Flood Plain)
  - **Dhubri, Assam** (Lower Riparian Brahmaputra Reach)
  - **Patna, Bihar** (Rajendra Nagar Low Basin & Ganges Confluence)
  - **Jaipur, Rajasthan** (Walled City Drainage Corridor)
  - **Malappuram, Kerala** (Kadalundi River Valley & Western Ghats)
- Supports arbitrary custom text search and GPS geolocation.

### 2. 🌧️ Real-Time Telemetry & Hydrological Monitoring
- **Live Weather**: Integrated with the Open-Meteo REST API (real-time temperature, humidity, wind speed, precipitation probability) with deterministic offline fallbacks.
- **Rainfall Intelligence**: Real-time 1-hour, 24-hour, and 48-hour rainfall accumulation tracked against official IMD warning categories (*Normal, Moderate, Heavy, Very Heavy, Extremely Heavy*).
- **River Gauge Telemetry**: Nearest river tracking, active gauge stations, current stages vs. danger marks, and flood status (*Normal, Approaching, Above Danger Mark, Overflowing*).
- **Historical Recurrence**: Historical benchmark linking to 17,458 district flood records across 728 Indian districts.

### 3. 🤖 Machine Learning Hazard & Severity Scoring
- Calibrated ML ensemble combining **XGBoost** (`xgb_model.pkl`) and **SGDClassifier** (`sgd_model.pkl`).
- Computes a unified **0–100 Disaster Severity Score (DSS)**:
  $$\text{DSS} = 0.35 \times P_{\text{flood}} + 0.30 \times \text{Rainfall}_{\text{norm}} + 0.20 \times \text{River}_{\text{norm}} + 0.15 \times (100 - \text{Elevation}_{\text{norm}})$$
- Automatic classification into 4 operational tiers: `LOW`, `MODERATE`, `HIGH`, `CRITICAL`.

### 4. 👥 Spatial Demographic & Critical Infrastructure Exposure
- **GeoPandas & Shapely** spatial intersection over dynamic hazard zones.
- Pinpoints exposed populations with demographic breakdowns: children (<12 yrs), elderly (>65 yrs), and mobility-impaired individuals requiring mandatory evacuation.
- Audits critical infrastructure in the danger perimeter: hospitals, schools, bridges/culverts, and power/water utilities.

### 5. ⚡ Transparent Emergency Response Priority Ranking
- Mathematically defensible priority scoring:
  $$\text{Priority Score} = 40\% \text{ Risk} + 25\% \text{ Population} + 20\% \text{ Infrastructure} + 15\% \text{ Isolation Urgency}$$
- Automatically ranks zones (Rank 1 = Highest Emergency) with explicit reasons and actionable deployment directives.

### 6. 🛣️ Risk-Penalized Safe Evacuation Routing & Shelter Allocation
- **NetworkX / OSMnx A\*** routing engine evaluating three distinct evacuation corridors:
  - **Route A (Fastest / Direct)**: Shortest travel time; carries inundation risk warnings.
  - **Route B (Safe Highland Bypass)**: Maximizes elevation and circumvents riverbanks (Recommended).
  - **Route C (Balanced Corridor)**: Optimal trade-off between transit time and safety margin.
- **Shelter Engine**: Evaluates registered relief centers by proximity, remaining bed capacity, backup generator status, and site elevation.

### 7. 📋 Grounded AI Incident Action Plan (IAP)
- Powered by **Google Gemini API** (`gemini-1.5-flash`) with a robust offline Incident Commander fallback.
- Formats authoritative Incident Action Plans compliant with **National Disaster Management Authority (NDMA)** Incident Command System (ICS) guidelines.
- Provides immediate 0–6 hour directives, 6–24 hour tactical objectives, and a full resource deployment matrix (NDRF boat teams, dewatering pumps, medical triages, reconnaissance drones).

---

## 👥 Dual-Persona Interface

Aapda Setu provides dedicated role-based workflows:

| Role | Target Users | Features & Workflow |
|:---|:---|:---|
| **🛡️ Rescue Team / Admin** | Incident Commanders, DDMAs, NDRF/SDRF | Full tactical command access across 10 operational tabs: Overview, Risk Zones, People & Infrastructure, Response Priority, Evacuation Routes, Safe Shelters, AI Action Plan, Disaster History, Data Intelligence, and Pipeline Settings. |
| **👤 Citizen / Normal User** | Vulnerable Residents, Civilians | Panic-free localized view: color-coded safety level, nearest verified relief shelters with directions, safe evacuation route, and one-click Emergency SOS dispatch buttons (NDRF 1078, SDRF 1070). |

---

## 🏗️ System Architecture & Data Flow

```
                               [ USER ENTERS LOCATION / PRESET ]
                                              │
                                              ▼
                             [ LocationService (GIS & Elevation) ]
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
         [ WeatherService ]          [ RainfallService ]       [ RiverService ]
        (Open-Meteo REST API)       (1h, 24h, 48h, Anomaly)   (CWC Gauge Stations)
                    └─────────────────────────┬─────────────────────────┘
                                              ▼
                                 [ HistoricalDisasterService ]
                                 (17,458 District Flood Records)
                                              │
                                              ▼
                    ┌───────────────────────────────────────────────────┐
                    │            CORE INTELLIGENCE ENGINES              │
                    ├───────────────────────────────────────────────────┤
                    │ 1. PredictionEngine (SGDClassifier & XGBoost)     │
                    │ 2. PopulationImpactService (GeoPandas / Shapely)  │
                    │ 3. InfrastructureRiskService (Hospitals/Bridges)  │
                    │ 4. PriorityRankingEngine (Transparent Weights)    │
                    │ 5. SafeRoutingService (NetworkX / OSMnx A*)       │
                    │ 6. ShelterService (Proximity & Capacity Scoring)  │
                    │ 7. AIActionPlanService (Gemini Grounded IAP)      │
                    └─────────────────────────┬─────────────────────────┘
                                              ▼
                             [ MASTER JSON CONTRACT: outputs/ ]
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
         [ Rescue Team / Admin EOC ]                         [ Citizen Safety Portal ]
         (10 Operational Panels)                             (Simple Emergency Cards)
```

---

## 📁 Standardized Output Contracts (`outputs/`)

Each module communicates through standardized CSV/JSON contract files:

- `outputs/risk_predictions.csv`: ML model predictions with probability scores and risk categories per zone.
- `outputs/impact_results.json`: Exposed populations, vulnerable groups, and critical infrastructure counts.
- `outputs/priority_results.json`: Ranked disaster zones with computed priority scores, tiers, and reasons.
- `outputs/shelter.json`: Identified safe shelters with capacity, distance, and safety readiness scores.
- `outputs/route.json`: Calculated coordinate waypoints, distances, transit times, and safety ratings for Routes A, B, and C.
- `outputs/ai_action_plan.json`: Formal incident commander directives, timeline objectives, and resource requirements.

---

## ⚡ Quick Start Guide

### 1. Clone & Setup Environment
```bash
# Clone the repository
git clone https://github.com/Hiten-7/team-010-_ps1.git
cd team-010-_ps1

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** (or **[http://localhost:8502](http://localhost:8502)**) in your browser.

### 3. Run Automated Dynamic Test Suite
Verify that all services, ML models, GIS layers, and location telemetry execute cleanly across diverse geographic regions:
```bash
pytest tests/test_dynamic_locations.py -v
# Or directly via Python:
python tests/test_dynamic_locations.py
```

---

## 📂 Project Structure

```
team-010-_ps1/
├── PRD.md                             # Comprehensive Product Requirements Document
├── README.md                          # Project overview and technical documentation
├── app.py                             # Streamlit Command Center & Citizen Safety Portal
├── requirements.txt                   # Production dependencies
├── model_training_dataset.csv         # 17,458 historical Indian district flood records
├── models/                            # Serialized ML models
│   ├── disaster_priority_model.pkl
│   ├── sgd_model.pkl
│   └── xgb_model.pkl
├── services/                          # Modular location-aware intelligence services
│   ├── location_service.py            # Coordinate, elevation & catchment resolver
│   ├── weather_service.py             # Open-Meteo REST API integration
│   ├── rainfall_service.py            # Dynamic 1h, 24h, 48h IMD rainfall engine
│   ├── river_service.py               # CWC river gauge & danger mark tracker
│   ├── historical_service.py          # District flood history analyzer
│   ├── prediction_service.py          # ML risk zone & severity score engine
│   ├── population_service.py          # Spatial demographic exposure analyzer
│   ├── infrastructure_service.py      # Critical asset & utility vulnerability auditor
│   ├── shelter_service.py             # Nearest safe shelter recommender
│   ├── routing_service.py             # Risk-penalized A* evacuation router
│   ├── ai_action_plan_service.py      # Google Gemini / Offline IAP synthesizer
│   └── disaster_intelligence_service.py # Master pipeline coordinator
├── routing/                           # Routing & priority helpers
│   ├── priority.py                    # Multi-factor priority formula & classification
│   └── route.py                       # NetworkX graph construction
├── utils/                             # Map & UI rendering utilities
│   └── map_utils.py                   # Leaflet/Folium disaster command map generator
├── outputs/                           # Standardized output contracts (JSON / CSV)
│   ├── risk_predictions.csv
│   ├── impact_results.json
│   ├── priority_results.json
│   ├── shelter.json
│   ├── route.json
│   └── ai_action_plan.json
└── tests/                             # Automated test suite
    └── test_dynamic_locations.py
```

---

## 🛠️ Technology Stack

| Domain | Technology | Purpose |
|:---|:---|:---|
| **Frontend & UI** | Streamlit, Folium, Streamlit-Folium | Responsive command center, citizen portal, interactive Leaflet maps |
| **Machine Learning** | Scikit-learn, XGBoost, Joblib | Flood probability classification and calibrated severity scoring |
| **GIS & Demographics** | GeoPandas, Shapely | Spatial polygon overlays, infrastructure and demographic exposure |
| **Graph & Routing** | NetworkX, OSMnx | A* search, risk-weighted edge costs, safe highland bypass corridors |
| **Live Telemetry** | Open-Meteo REST API, Urllib | Zero-API-key global weather, rainfall, and river basin telemetry |
| **Generative AI** | Google Gemini (`google-genai`) | Authoritative NDMA-compliant Incident Action Plans |
| **Data Processing** | Pandas, NumPy | High-performance feature engineering and contract serialization |

---

## 🛡️ License & Acknowledgments

Developed for the Disaster Management AI Hackathon. Built to empower district authorities with rapid, transparent, and actionable intelligence to safeguard vulnerable lives and critical infrastructure during extreme weather calamities.
