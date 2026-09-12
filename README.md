<<<<<<< HEAD
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
=======
# Disaster Management Intelligence System

AI-driven predictive intelligence system that transforms scattered disaster data into actionable emergency response plans for Indian district disaster management.

## Product Vision

Equip every Indian district with AI-driven predictive intelligence that transforms scattered disaster data into actionable emergency response plans within minutes.

## Target Audience

- District disaster management officers
- Emergency response coordinators
- State government administrators
- Field rescue teams requiring rapid decision-making intelligence

## Core Features

- **District Management**: CRUD operations for managing Indian districts with geographical data
- **Disaster Tracking**: Record and track disaster events with severity levels and impact metrics
- **Alert System**: Create and manage predictive alerts with confidence scores and recommended actions

## Technology Stack

- **Backend Framework**: FastAPI 0.104.1
- **Database**: SQLAlchemy 2.0.23 (SQLite for development, PostgreSQL/MySQL for production)
- **Data Validation**: Pydantic 2.5.0
- **Server**: Uvicorn 0.24.0
- **Architecture**: Modular Monolith with clear separation of concerns

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
```bash
cd /path/to/project
```

2. **Create a virtual environment**:
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
```bash
pip install -r backend/requirements.txt
```

5. **Set up environment variables**:
```bash
cp .env.example .env
```
Edit `.env` file and update the configuration values, especially:
- `SECRET_KEY`: Use a strong random string for production
- `DATABASE_URL`: Configure your database connection

## Running the Application

### Development Mode

Run the application with auto-reload enabled:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Production Mode

For production deployment:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Districts
- `POST /api/v1/districts` - Create a new district
- `GET /api/v1/districts` - List all districts (with optional state filter)
- `GET /api/v1/districts/{district_id}` - Get district by ID
- `GET /api/v1/districts/code/{district_code}` - Get district by code
- `PUT /api/v1/districts/{district_id}` - Update district
- `DELETE /api/v1/districts/{district_id}` - Delete district

### Disasters
- `POST /api/v1/disasters` - Create a new disaster record
- `GET /api/v1/disasters` - List all disasters (with filters: district_id, disaster_type, severity)
- `GET /api/v1/disasters/{disaster_id}` - Get disaster by ID
- `PUT /api/v1/disasters/{disaster_id}` - Update disaster
- `DELETE /api/v1/disasters/{disaster_id}` - Delete disaster

### Alerts
- `POST /api/v1/alerts` - Create a new alert
- `GET /api/v1/alerts` - List all alerts (with filters: district_id, disaster_type, severity, status, active_only)
- `GET /api/v1/alerts/{alert_id}` - Get alert by ID
- `PUT /api/v1/alerts/{alert_id}` - Update alert
- `PATCH /api/v1/alerts/{alert_id}/resolve` - Mark alert as resolved
- `DELETE /api/v1/alerts/{alert_id}` - Delete alert

## Database Models

### District
- Indian district information with geographical coordinates
- Population and area data
- Unique district code

### Disaster
- Disaster event records
- Types: flood, earthquake, cyclone, drought, landslide, fire, tsunami, other
- Severity levels: low, medium, high, critical
- Impact metrics: affected population, casualties, damage estimates

### Alert
- Predictive alerts and warnings
- Confidence scores for predictions
- Recommended actions
- Validity periods
- Status tracking: active, resolved, monitoring

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for security operations
- `DEBUG`: Enable/disable debug mode
- `ALLOWED_ORIGINS`: CORS allowed origins
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── requirements.txt     # Python dependencies
│   └── routers/
│       ├── __init__.py
│       ├── disasters.py     # Disaster endpoints
│       ├── districts.py     # District endpoints
│       └── alerts.py        # Alert endpoints
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Architecture Overview

The application follows a **Modular Monolith** architecture:

- **Routers**: Handle HTTP requests and responses
- **Models**: Define database schema using SQLAlchemy ORM
- **Schemas**: Validate request/response data using Pydantic
- **Database**: Centralized database connection management
- **Config**: Environment-based configuration

## Development Guidelines

1. **Code Style**: Follow PEP 8 guidelines
2. **Error Handling**: All endpoints include proper error handling
3. **Validation**: Input validation using Pydantic schemas
4. **Logging**: Structured logging for debugging and monitoring
5. **Security**: Environment variables for sensitive data

## Database Migration

For production deployments, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init alembic
# Configure alembic.ini and create migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Security Considerations

- Change `SECRET_KEY` in production to a strong random string
- Use PostgreSQL or MySQL for production (not SQLite)
- Enable HTTPS in production
- Configure proper CORS origins
- Implement rate limiting for production APIs
- Use environment variables for all sensitive configuration

## Support

For issues, questions, or contributions, please contact the development team or refer to the project documentation.

## License

[Specify your license here]
>>>>>>> 2c96b425db9a1d91485b8ead4d5b880c75e9f248
