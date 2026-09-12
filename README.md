# 🚨 AI-Powered Disaster Early Warning & Rescue Intelligence Platform

An end-to-end mission-critical intelligence platform designed for District Disaster Management Authorities (DDMAs) and emergency response teams to predict disaster zones, evaluate affected population and infrastructure, rank emergency priorities, calculate risk-aware evacuation routes, allocate safe shelters, and generate authoritative AI Incident Action Plans.

---

## 🏗️ Architecture & Communication Contract

Each module is decoupled and communicates exclusively through standard CSV/JSON contracts in the `outputs/` directory:

```
DATASETS (IMD / Bhuvan / NDEM / Sample)
   │
   ▼
[ml/] ML RISK ENGINE (Member 1: SGD + XGBoost)
   │   └─► outputs/risk_predictions.csv
   ▼
[gis/] GIS IMPACT & SHELTER ENGINE (Member 2: GeoPandas + Shapely)
   │   ├─► outputs/impact_results.json
   │   └─► outputs/shelter.json
   ▼
[routing/] EMERGENCY PRIORITY & ROUTING (Member 3: NetworkX + A*)
   │   ├─► outputs/priority_results.json
   │   └─► outputs/route.json
   ▼
[ai/] AI EMERGENCY ACTION PLAN (Member 4 / LLM: Gemini Grounded)
   │
   ▼
[app.py] STREAMLIT COMMAND CENTER (Member 4)
```

---

## 👥 Team Work Distribution (4 Members)

To avoid merge conflicts on `main`, each member has a dedicated directory:

| Member | Domain | Dedicated Directory & Files | Target Output Contract |
| :--- | :--- | :--- | :--- |
| **Member 1** | **ML / Risk Prediction** | `ml/features.py`<br>`ml/train_sgd.py`<br>`ml/train_xgboost.py`<br>`ml/predict_risk.py`<br>`models/` | `outputs/risk_predictions.csv` |
| **Member 2** | **GIS / Impact Analysis** | `gis/impact.py`<br>`gis/shelter.py`<br>`data/` | `outputs/impact_results.json`<br>`outputs/shelter.json` |
| **Member 3** | **Routing & Priority** | `routing/priority.py`<br>`routing/route.py` | `outputs/priority_results.json`<br>`outputs/route.json` |
| **Member 4** | **Streamlit & Integration** | `app.py`<br>`ai/action_plan.py`<br>`utils/` | Integrated Command UI & Action Plan |

> ⚠️ **Rule:** Only **Member 4** should edit `app.py`. All other members work inside their respective directories and produce their contracted output files.

---

## ⚡ Quick Start & Run Commands

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline Test (Generates All Outputs)
```bash
python -c "
import ml.predict_risk as pr, gis.impact as gi, gis.shelter as gs, routing.priority as rp, routing.route as rr, ai.action_plan as ap
pr.run_risk_prediction()
gi.run_impact_analysis()
gs.recommend_shelters()
rp.run_priority_ranking()
rr.find_evacuation_routes()
print('All outputs generated!')
"
```

### 3. Launch the Streamlit Command Center
```bash
streamlit run app.py
```

*Note: If running on Windows with a specific Python binary:*
```powershell
& "c:\Users\DHRUV\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run app.py
```

---

## 📋 Data Contract Specifications

### 1. `outputs/risk_predictions.csv` (Produced by Member 1)
```csv
zone_id,zone_name,district,state,latitude,longitude,rainfall_mm,risk_probability,risk_score,risk_level,model_used
Z-KOL-03,Kolkata South East,KOLKATA,WEST BENGAL,22.518,88.39,245.8,0.934,93.4,VERY HIGH,XGBoost (Primary)
```

### 2. `outputs/impact_results.json` (Produced by Member 2)
```json
[
  {
    "zone": "Z-KOL-03",
    "population": 152140,
    "hospitals": 4,
    "schools": 13,
    "roads": 34,
    "bridges": 5
  }
]
```

### 3. `outputs/priority_results.json` (Produced by Member 3)
```json
[
  {
    "priority_rank": 1,
    "zone_id": "Z-KOL-03",
    "zone_name": "Kolkata South East Lowlands",
    "priority_score": 94.1,
    "priority_level": "CRITICAL",
    "affected_population": 152140,
    "critical_infrastructure_count": 21
  }
]
```

### 4. `outputs/shelter.json` (Produced by Member 2)
```json
[
  {
    "zone_id": "Z-KOL-03",
    "recommended_shelter_id": "SH-01",
    "shelter_name": "Salt Lake Stadium Indoor Complex",
    "distance_km": 3.2,
    "shelter_risk": "LOW",
    "available_capacity": 4150,
    "status": "RECOMMENDED"
  }
]
```

### 5. `outputs/route.json` (Produced by Member 3)
```json
{
  "routes": {
    "fast_route": { "title": "Route A", "distance_km": 8.5, "travel_time_min": 15.2, "flood_risk_level": "HIGH FLOOD RISK", "recommendation": "NOT RECOMMENDED" },
    "safe_route": { "title": "Route B", "distance_km": 13.8, "travel_time_min": 26.0, "flood_risk_level": "LOW FLOOD RISK", "recommendation": "RECOMMENDED ALTERNATIVE" },
    "optimal_route": { "title": "Route C", "distance_km": 11.6, "travel_time_min": 22.4, "flood_risk_level": "LOW FLOOD RISK", "recommendation": "RECOMMENDED PRIMARY" }
  }
}
```

---

## 🔄 Roadmap to Replace Sample Data with Real Datasets

During the hackathon, replace data in this recommended sequence:

1. **Step 1: Real IMD Daily Rainfall (`data/raw/imd_rainfall.csv`)**
   - Replace `data/sample/sample_rainfall.csv` with live/daily district rainfall tables from IMD.
   - Member 1 connects `ml/predict_risk.py` to ingest the live precipitation values.

2. **Step 2: Train Models with `model_training_dataset.csv`**
   - Member 1 can point `ml/train_sgd.py` and `ml/train_xgboost.py` to `model_training_dataset.csv`.
   - The pre-trained pipeline in `disaster_priority_model.pkl` is already linked in `models/` and loaded by `routing/priority.py`.

3. **Step 3: Real Administrative Boundaries & OpenStreetMap Amenities (GIS)**
   - Member 2 downloads GeoJSON / Shapefiles for the target district.
   - Load hospital and school points using GeoPandas spatial joins in `gis/impact.py`.

4. **Step 4: Live OSMnx Road Graph (Routing)**
   - Member 3 activates `osmnx.graph_from_place()` in `routing/route.py` for dynamic road edge costs and flood level penalty.

5. **Step 5: Live LLM Emergency Action Plan**
   - Set environment variable `GEMINI_API_KEY="your-key-here"` or enter it in the sidebar in `app.py`.
   - Generates live multimodal/grounded action plans.