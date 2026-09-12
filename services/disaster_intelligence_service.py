"""
Disaster Intelligence Orchestrator Service.
Central pipeline that coordinates location resolution, live weather fetching,
hydrological calculation, historical lookups, ML predictions, impact analysis,
evacuation routing, shelter recommendations, and AI Action Plan synthesis.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from config.settings import (
    RISK_PREDICTIONS_PATH,
    IMPACT_RESULTS_PATH,
    PRIORITY_RESULTS_PATH,
    SHELTER_RESULTS_PATH,
    ROUTE_RESULTS_PATH,
    OUTPUTS_DIR
)
from services.location_service import LocationService
from services.weather_service import WeatherService
from services.rainfall_service import RainfallService
from services.river_service import RiverService
from services.historical_service import HistoricalDataService
from services.prediction_service import PredictionService
from services.population_service import PopulationService
from services.infrastructure_service import InfrastructureService
from services.shelter_service import ShelterService
from services.routing_service import RoutingService
from services.ai_action_plan_service import AIActionPlanService
from routing.priority import compute_priority_score, get_priority_classification


class DisasterIntelligenceService:
    """Master service orchestrating end-to-end disaster intelligence for any location."""

    def __init__(self):
        self.location_service = LocationService()
        self.weather_service = WeatherService()
        self.rainfall_service = RainfallService()
        self.river_service = RiverService()
        self.historical_service = HistoricalDataService()
        self.prediction_service = PredictionService()
        self.population_service = PopulationService()
        self.infra_service = InfrastructureService()
        self.shelter_service = ShelterService()
        self.routing_service = RoutingService()
        self.ai_service = AIActionPlanService()

    def analyze_location(
        self,
        location_input: Any,
        model_choice: str = "XGBoost",
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates full location-based intelligence analysis.
        """
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Resolve Location Coordinates & Terrain Metadata
        loc = self.location_service.resolve_location(location_input)
        lat = loc["latitude"]
        lon = loc["longitude"]
        district = loc["district"]
        state = loc["state"]
        elev = loc["elevation_m"]

        # 2. Fetch Live/Deterministic Weather
        weather = self.weather_service.get_weather_for_location(lat, lon)

        # 3. Compute Location-Specific Rainfall Metrics
        rainfall = self.rainfall_service.get_rainfall_data(weather, district, elev)

        # 4. Compute River Hydrology vs. Danger Marks
        river = self.river_service.get_river_data(loc, rainfall)

        # 5. Fetch Historical Disaster Records (from model_training_dataset.csv)
        historical = self.historical_service.get_historical_disaster_data(district, state)

        # 6. Execute ML Risk Prediction on Dynamic Location Features
        risk_zones = self.prediction_service.predict_risk_zones(
            loc, rainfall, river, historical, model_choice=model_choice
        )

        # 7. Calculate Demographics & Population Impact
        population = self.population_service.calculate_population_impact(loc, risk_zones, historical)

        # 8. Calculate Infrastructure Exposure
        infrastructure = self.infra_service.get_infrastructure_data(loc, risk_zones)

        # 9. Compute Response Priorities (40% Risk + 25% Pop + 20% Infra + 15% Access)
        priorities = []
        max_pop = max([z["affected_population"] for z in population["zone_breakdowns"]] or [1])
        max_infra = max([z["hospitals_at_risk"] * 2 + z["schools_at_risk"] + z["bridges_at_risk"] for z in infrastructure["zone_breakdown"]] or [1])

        for idx, z in enumerate(risk_zones):
            pop_item = population["zone_breakdowns"][idx]
            infra_item = infrastructure["zone_breakdown"][idx]

            pop_val = pop_item["affected_population"]
            infra_val = infra_item["hospitals_at_risk"] * 2 + infra_item["schools_at_risk"] + infra_item["bridges_at_risk"]
            access_val = 0.35 if z["elevation_m"] < 5.0 else (0.60 if z["elevation_m"] < 25.0 else 0.85)

            p_score = compute_priority_score(
                z["risk_score"],
                min(pop_val / max(max_pop, 1), 1.0),
                min(infra_val / max(max_infra, 1), 1.0),
                access_val
            )
            tier, urgency, action = get_priority_classification(p_score)

            priorities.append({
                "priority_rank": idx + 1,
                "zone_id": z["zone_id"],
                "zone_name": z["zone_name"],
                "area_locality": z["area_locality"],
                "district": district,
                "priority_score": p_score,
                "priority_tier": tier,
                "priority_level": urgency,
                "recommended_action": action,
                "risk_score": z["risk_score"],
                "affected_population": pop_val,
                "critical_infrastructure_count": infra_val,
                "priority_reasons": z["reasons"]
            })

        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        for idx, p in enumerate(priorities, start=1):
            p["priority_rank"] = idx

        # 10. Calculate Overall Disaster Severity Score (0-100)
        avg_risk = float(np.mean([z["risk_score"] for z in risk_zones])) if risk_zones else 50.0
        severity = self.prediction_service.calculate_severity_score(rainfall, river, historical, avg_risk)

        # 11. Discover and Rank Safe Shelters
        shelters = self.shelter_service.get_shelters_for_location(loc)

        # 12. Calculate Evacuation Routes to Top Shelter
        top_shelter = shelters[0] if shelters else {"name": "Relief Hub", "latitude": lat + 0.02, "longitude": lon + 0.03}
        routes = self.routing_service.calculate_routes(loc, top_shelter)

        # 13. Generate Dynamic AI Incident Action Plan
        top_pri = priorities[0] if priorities else {"area_locality": "Primary Sector", "recommended_action": "Deploy units"}
        plan_text, plan_src = self.ai_service.generate_plan(
            loc, weather, rainfall, river, severity, population, infrastructure, top_pri, top_shelter, routes, api_key=api_key
        )

        # 14. Save outputs to enforce the CSV/JSON contract
        try:
            # risk_predictions.csv
            df_risk_out = pd.DataFrame(risk_zones)
            df_risk_out["district"] = district
            df_risk_out["state"] = state
            df_risk_out["rainfall_mm"] = rainfall["last24Hours"]
            df_risk_out.to_csv(RISK_PREDICTIONS_PATH, index=False)

            # impact_results.json
            impact_out = []
            for idx, z in enumerate(risk_zones):
                p_item = population["zone_breakdowns"][idx]
                i_item = infrastructure["zone_breakdown"][idx]
                impact_out.append({
                    "zone": z["zone_id"],
                    "zone_id": z["zone_id"],
                    "zone_name": z["zone_name"],
                    "area_locality": z["area_locality"],
                    "district": district,
                    "city": loc["city"],
                    "latitude": z["latitude"],
                    "longitude": z["longitude"],
                    "elevation_m": z["elevation_m"],
                    "total_population": p_item["total_population"],
                    "population": p_item["affected_population"],
                    "affected_population": p_item["affected_population"],
                    "children": p_item["children"],
                    "elderly": p_item["elderly"],
                    "vulnerable_population": p_item["vulnerable_population"],
                    "evacuation_required": p_item["evacuation_required"],
                    "hospitals": i_item["hospitals_at_risk"],
                    "total_hospitals": i_item["hospitals_total"],
                    "schools": i_item["schools_at_risk"],
                    "total_schools": i_item["schools_total"],
                    "bridges": i_item["bridges_at_risk"],
                    "power_stations": i_item["power_at_risk"],
                    "risk_score": z["risk_score"],
                    "risk_reasons": z["reasons"],
                    "river_name": river["nearest_river"],
                    "river_level_m": river["current_level_m"],
                    "river_danger_mark_m": river["danger_mark_m"],
                    "river_status": river["status"]
                })
            with open(IMPACT_RESULTS_PATH, "w", encoding="utf-8") as f:
                json.dump(impact_out, f, indent=2)

            # priority_results.json
            with open(PRIORITY_RESULTS_PATH, "w", encoding="utf-8") as f:
                json.dump(priorities, f, indent=2)

            # shelter.json
            with open(SHELTER_RESULTS_PATH, "w", encoding="utf-8") as f:
                json.dump(shelters, f, indent=2)

            # route.json
            with open(ROUTE_RESULTS_PATH, "w", encoding="utf-8") as f:
                json.dump(routes, f, indent=2)
        except Exception as e:
            print(f"[WARN] Error persisting output contract files: {e}")

        # Data source transparency badges
        data_sources = {
            "weather": weather.get("source", "🟢 LIVE API"),
            "rainfall": rainfall.get("source", "🟢 LIVE IMD / OPEN-METEO"),
            "river": river.get("source", "🟡 HYDROLOGICAL CWC MODEL"),
            "historical": historical.get("source", "🟡 HISTORICAL DATASET"),
            "ml_model": risk_zones[0].get("model_used", "🔵 XGBOOST ML MODEL") if risk_zones else "🔵 ML MODEL",
            "population": population.get("source", "🟣 ESTIMATED CENSUS MODEL"),
            "infrastructure": infrastructure.get("source", "🟡 NDEM / OSM GIS"),
            "routes": routes.get("source", "🔵 RISK-WEIGHTED A* ALGORITHM"),
            "action_plan": plan_src
        }

        return {
            "location": loc,
            "weather": weather,
            "rainfall": rainfall,
            "river": river,
            "historical": historical,
            "risk_zones": risk_zones,
            "severity": severity,
            "population": population,
            "infrastructure": infrastructure,
            "priorities": priorities,
            "shelters": shelters,
            "routes": routes,
            "action_plan": plan_text,
            "action_plan_source": plan_src,
            "data_sources": data_sources
        }
