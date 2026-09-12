# 📄 Product Requirements Document (PRD)
## Project: Aapda Setu (आपदा सेतु)
### AI-Powered Disaster Early Warning & Rescue Intelligence Platform

---

| **Document Metadata** | **Details** |
|:---|:---|
| **Product Name** | **Aapda Setu (आपदा सेतु)** |
| **Product Type** | AI-Enabled Emergency Decision Support & Rescue Operations Platform |
| **Target Users** | District Disaster Management Authorities (DDMAs), NDRF/SDRF Incident Commanders, Municipal Emergency Operations Centers (EOC), and At-Risk Citizens |
| **Version** | 1.0 (Hackathon MVP) |
| **Date** | September 2026 |
| **Status** | Approved / Deployed MVP |

---

## 1. Executive Summary & Product Vision

### 1.1 Vision
**Aapda Setu** is an intelligent, location-aware disaster early warning and rescue coordination platform designed to bridge the gap between complex multi-source hydro-meteorological data and life-saving ground response. During severe monsoon events and acute flood crises, the platform transforms heterogeneous, disjointed telemetry into actionable operational directives within seconds.

### 1.2 The Core Problem
During extreme weather events (e.g., severe monsoons, river overflows, urban deluge), disaster authorities are inundated with fragmented information:
1. **Weather Radar & IMD Observations:** Raw rainfall and precipitation forecasts.
2. **Central Water Commission (CWC) River Gauges:** Gauge heights and danger-mark levels.
3. **Satellite Flood Extents:** Bhuvan / Sentinel satellite flood inundation maps.
4. **Demographic & Census Records:** Census population counts without live spatial hazard overlays.
5. **Municipal GIS Infrastructure:** Static hospital, school, and bridge directories.

**The Bottleneck:** Converting these isolated data streams into immediate answers to five vital rescue questions in the first 24–48 hours:
- **Where** will the disaster strike hardest?
- **Who & What** critical infrastructure is in the danger zone?
- **Which** community needs immediate rescue team deployment first?
- **How** can civilians evacuate safely without driving into submerged roads?
- **What** concrete operational plan must the Incident Commander execute right now?

---

## 2. Target Personas & User Profiles

### Persona 1: Emergency Operations Commander (DDMA / NDRF / SDRF Officer)
- **Profile:** District Magistrate, Disaster Management Officer, or Incident Commander in the EOC.
- **Pain Point:** Overloaded with conflicting raw data; needs defensible, prioritized dispatch orders and resource allocation.
- **Needs in Aapda Setu:**
  - 0–100 calibrated Disaster Severity Score.
  - Multi-hazard live spatial map with interactive risk zones and critical infrastructure markers.
  - Automated mathematical priority ranking of zones.
  - Instant AI-generated Incident Action Plan (IAP) aligned with NDRF protocols.

### Persona 2: First Responder / Rescue Boat Team Lead
- **Profile:** Field rescue team deployed in flood plains and submerged urban corridors.
- **Pain Point:** Traditional GPS navigation routes lead into inundated roads, washed-out bridges, or dead ends.
- **Needs in Aapda Setu:**
  - Risk-penalized evacuation routes (Route B Highland Bypass vs. flooded direct corridors).
  - Live shelter occupancy and distance calculations.
  - Identification of isolated populations (children, elderly, disabled).

### Persona 3: Citizen / Vulnerable Resident
- **Profile:** Local resident residing in a river catchment, low-lying basin, or monsoon-affected district.
- **Pain Point:** Confusing meteorological bulletins; lack of clear, localized safety instructions.
- **Needs in Aapda Setu:**
  - Simple, color-coded safety status (Green / Yellow / Orange / Red).
  - Nearest verified relief camp with contact info and capacity.
  - One-click safe evacuation route navigation.
  - Direct emergency SOS dispatch triggers (NDRF 1078, SDRF 1070).

---

## 3. Product Architecture & Decoupled Modular Contract

Aapda Setu is built with a resilient, decoupled micro-service architecture that communicates through standardized file and JSON contracts in the `outputs/` directory:

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

## 4. Feature Specifications & Requirements

### 4.1 Feature 1: Dynamic Location-Aware Telemetry Pipeline
- **Requirement:** Zero hardcoded data. Changing the location must dynamically re-evaluate all upstream data points.
- **Input Methods:**
  - Curated disaster hotspot presets (*Kolkata, Varanasi, Nagaon, Dhubri, Patna, Jaipur, Malappuram*).
  - Custom location search with auto-resolution to coordinates, elevation, district, and river catchment.
  - Simulated browser/device GPS detection.
- **Telemetry Feeds:**
  - **Weather:** Real-time temperature, humidity, atmospheric pressure, wind speed, precipitation probability.
  - **Rainfall:** 1-hour, 24-hour, and 48-hour accumulation with IMD warning tier (*Normal, Moderate, Heavy, Very Heavy, Extremely Heavy*).
  - **Hydrology:** Nearest river name, active monitoring station, current water level, danger mark, alert status (*Normal, Approaching, Above Danger Mark, Overflowing*).
  - **Historical Benchmark:** 10-year district flood frequency, peak historical flood depth, average annual flood damage index.

### 4.2 Feature 2: Machine Learning Hazard & Severity Prediction
- **Models:**
  - Primary: `XGBoostClassifier` (`xgb_model.pkl`)
  - Secondary/Baseline: `SGDClassifier` (`sgd_model.pkl`)
- **Calibrated Disaster Severity Score (0–100):**
  $$\text{DSS} = 0.35 \times P_{\text{flood}} + 0.30 \times \text{Rainfall}_{\text{norm}} + 0.20 \times \text{River}_{\text{norm}} + 0.15 \times (100 - \text{Elevation}_{\text{norm}})$$
- **Response Tiers:**
  - `0 - 24`: LOW (Advisory / Normal Monitoring)
  - `25 - 49`: MODERATE (Yellow Watch / Logistics Prepositioning)
  - `50 - 74`: HIGH (Orange Alert / Stage Medical Units & Route Clearance)
  - `75 - 100`: SEVERE / CRITICAL (Red Alert / Immediate Evacuation & NDRF Deployment)

### 4.3 Feature 3: Spatial Demographic & Critical Infrastructure Exposure
- **GIS Engine:** GeoPandas and Shapely spatial polygon intersection.
- **Population Analytics:**
  - Total exposed population within hazard boundary.
  - Vulnerable demographic breakdown: Children (<12 yrs), Elderly (>65 yrs), Mobility-impaired.
  - Evacuation required count.
- **Infrastructure Exposure:**
  - Hospitals & Primary Health Centers at risk.
  - Educational institutions (potential staging grounds or submerged assets).
  - Bridges & culverts facing structural scour or inundation.
  - Power substations and drinking water pumping stations exposed.

### 4.4 Feature 4: Transparent Multi-Factor Emergency Response Ranking
- **Mathematical Formula:**
  $$\text{Priority Score} = 0.40 \times \text{Risk} + 0.25 \times \text{Pop}_{\text{norm}} + 0.20 \times \text{Infra}_{\text{norm}} + 0.15 \times \text{Isolation}_{\text{urgency}}$$
  where $\text{Isolation}_{\text{urgency}} = (1.0 - \text{Accessibility Score}) \times 100$.
- **Outputs:**
  - Automated ordinal rank (Rank 1 = Highest Emergency).
  - Specific operational directive (e.g., *"Deploy 3 NDRF inflatable boat teams to Sector 4"*).
  - Verifiable transparent audit trail explaining *why* the zone was prioritized.

### 4.5 Feature 5: Risk-Aware Safe Evacuation Routing & Shelter Allocation
- **Routing Engine:** NetworkX and OSMnx graph algorithms.
- **Multi-Route Analysis:**
  - **Route A (Fastest / Direct):** Minimal travel time, but passes through high-risk inundated sectors. Marked with safety warnings.
  - **Route B (Safe Highland Bypass):** Maximizes terrain elevation and minimizes proximity to riverbanks. Recommended for heavy vehicles, ambulances, and civilians.
  - **Route C (Balanced Corridor):** Optimal balance between transit duration and safety margin.
- **Shelter Allocation Algorithm:**
  - Evaluates registered district relief centers based on Euclidean/road distance, remaining bed capacity, backup generator status, and site elevation above flood plain.

### 4.6 Feature 6: Grounded AI Incident Action Plan (IAP)
- **Engine:** Google Gemini API (`gemini-1.5-flash` / `gemini-2.0`) with robust offline fallback synthesizer.
- **Outputs:**
  - Formatted according to National Disaster Management Authority (NDMA) Incident Command System (ICS) standards.
  - **Situation Assessment:** Synthesized meteorological and hydrological threat matrix.
  - **Immediate Actions (0–6 Hours):** Life safety, siren activation, mandatory evacuation order triggers.
  - **Operational Objectives (6–24 Hours):** Relief camp supply lines, power grid stabilization, medical triaging.
  - **Resource Deployment Matrix:** Recommended count of NDRF battalions, inflatable boats, high-capacity dewatering pumps, and drone reconnaissance sorties.

---

## 5. Non-Functional Requirements (NFRs)

| Metric | Target Specification | Validation Method |
|:---|:---|:---|
| **End-to-End Latency** | $\le 2.0$ seconds for full pipeline execution on location switch | Benchmarked across 7 geographic regions |
| **Offline Resilience** | 100% operational when internet or Open-Meteo REST API is unavailable | Built-in deterministic geospatial fallbacks |
| **Cross-Platform** | Fully responsive across Desktop, Tablet, and Mobile browsers | Tested on Chromium, Edge, Firefox, and Mobile Web |
| **Reproducibility** | All downstream JSON contracts saved to `outputs/` for inter-team handoff | Verified by automated test suite |
| **Map Rendering** | Zero external API token dependencies (Free OpenStreetMap tiles) | Verified in headless browser & user UI |

---

## 6. Output Data Contracts

The platform strictly enforces the following standardized outputs saved in `outputs/`:

1. `outputs/risk_predictions.csv`: ML model predictions with probability scores and risk categories per zone.
2. `outputs/impact_results.json`: Exposed populations, vulnerable groups, and critical infrastructure counts.
3. `outputs/priority_results.json`: Ranked disaster zones with computed priority scores, tiers, and reasons.
4. `outputs/shelter.json`: Identified safe shelters with capacity, distance, and safety readiness scores.
5. `outputs/route.json`: Calculated coordinate waypoints, distances, transit times, and safety ratings for Routes A, B, and C.
6. `outputs/ai_action_plan.json`: Formal incident commander directives, timeline objectives, and resource requirements.

---

## 7. Success Metrics & Key Performance Indicators (KPIs)

1. **Evacuation Decision Time:** Reduced from an industry average of 4–6 hours of manual data collation to **under 30 seconds**.
2. **Resource Allocation Precision:** 100% explainable, multi-factor weighting prevents subjective misallocation of NDRF boat assets.
3. **Route Safety Compliance:** High-risk inundated roads automatically flagged and excluded from civilian routing corridors.
4. **Adoption & Usability:** Dual-persona interface ensures rescue commanders get tactical depth while citizens get simple, panic-free evacuation guidance.

---

## 8. Future Roadmap & Post-Hackathon Enhancements

- **Phase 2 (IoT & Edge):** Direct ingestion from LoRaWAN river level sensors and automated ultrasonic rainfall gauges.
- **Phase 3 (Drone & SAR Imagery):** Integration with drone video feeds and ISRO Bhuvan Synthetic Aperture Radar (SAR) for real-time water boundary contouring.
- **Phase 4 (Citizen Communication):** Automated multi-lingual IVR voice calls and SMS alerts broadcast via Cell Broadcast Emergency Alert System.
- **Phase 5 (Offline Edge Deployment):** Lightweight package deployable on ruggedized field laptops inside mobile incident command vehicles without cellular connectivity.
