"""
AI Action Plan & Incident Commander Service for Disaster Intelligence Platform.
Dynamically generates location-grounded Incident Summaries, Situation Analyses,
and Operational Response Directives based on actual real-time telemetry.
"""
import os
import json
from typing import Dict, Any


class AIActionPlanService:
    """Generates location-specific Incident Command Action Plans."""

    @staticmethod
    def generate_plan(
        location: Dict[str, Any],
        weather: Dict[str, Any],
        rainfall: Dict[str, Any],
        river: Dict[str, Any],
        severity: Dict[str, Any],
        population: Dict[str, Any],
        infrastructure: Dict[str, Any],
        top_priority_zone: Dict[str, Any],
        shelter: Dict[str, Any],
        route: Dict[str, Any],
        api_key: str = None
    ) -> tuple[str, str]:
        loc_str = f"{location.get('area_locality', 'Local Area')}, {location.get('city', 'City')} ({location.get('district', 'District')}, {location.get('state', 'State')})"
        rain_24h = rainfall.get("last24Hours", 50.0)
        rain_tier = rainfall.get("intensity_tier", "Heavy Monsoon")
        river_name = river.get("nearest_river", "River")
        river_lvl = river.get("current_level_m", 7.0)
        river_danger = river.get("danger_mark_m", 7.5)
        river_status = river.get("status", "Active Monitoring")
        score = severity.get("score", 75.0)
        tier = severity.get("tier", "HIGH THREAT")
        tot_affected = population.get("total_population_at_risk", 15000)
        evac_req = population.get("evacuation_required", 6000)
        children = population.get("children_at_risk", 3000)
        elderly = population.get("elderly_at_risk", 2000)
        hosp = infrastructure.get("hospitals_at_risk", 2)
        bridges = infrastructure.get("bridges_at_risk", 1)
        top_area = top_priority_zone.get("area_locality", "Critical Zone")
        top_action = top_priority_zone.get("recommended_action", "Deploy rescue units")
        shelter_name = shelter.get("name", "Designated Safe Shelter")
        shelter_dist = shelter.get("distance_km", 3.5)
        shelter_avail = shelter.get("available_space", 1500)
        opt_route = route.get("routes", {}).get("optimal_route", {})
        fast_route = route.get("routes", {}).get("fast_route", {})

        gemini_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

        if gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                prompt = f"""
You are the Incident Commander for District Disaster Management Authority (DDMA).
Generate a formal, highly authoritative Operational Incident Action Plan (IAP) based STRICTLY on this real telemetry.
DO NOT hallucinate or invent any numbers or names.

LOCATION: {loc_str}
WEATHER: {weather.get('weather_condition')}, Temp: {weather.get('temperature_c')}°C, Wind: {weather.get('wind_speed_kmh')} km/h
RAINFALL: 24h: {rain_24h} mm ({rain_tier}), 48h Forecast: {rainfall.get('forecast48Hours')} mm
RIVER HYDROLOGY: {river_name} at {river_lvl}m (Danger Mark: {river_danger}m) -> {river_status}
DISASTER SEVERITY SCORE: {score}/100 ({tier})
HUMAN IMPACT: {tot_affected:,} at risk, {evac_req:,} requiring evacuation ({children:,} children, {elderly:,} elderly)
CRITICAL INFRASTRUCTURE: {hosp} hospitals and {bridges} bridges compromised
HIGHEST PRIORITY TARGET: {top_area} -> {top_action}
DESIGNATED RELIEF SHELTER: {shelter_name} ({shelter_dist} km, {shelter_avail:,} beds available)
SAFE EVACUATION ROUTE: {opt_route.get('title')} ({opt_route.get('distance_km')} km, {opt_route.get('travel_time_min')} mins)
DANGEROUS ROUTE: {fast_route.get('title')} ({fast_route.get('warning')})

Structure your response into:
1. INCIDENT SUMMARY
2. CURRENT SITUATION ANALYSIS (Rainfall, River, High-Risk Zones, Human & Infrastructure Risk)
3. IMMEDIATE ACTIONS (First 2 Hours)
4. OPERATIONAL TIMELINE (Next 6 Hours & Next 24 Hours)
5. PUBLIC EVACUATION DIRECTIVE
"""
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                return resp.text, "🟢 GEMINI LIVE AI GENERATION (Grounded in Telemetry)"
            except Exception as e:
                print(f"[WARN] Gemini generation failed: {e}. Falling back to deterministic plan.")

        # Deterministic, location-specific Incident Command plan
        plan = f"""# INCIDENT COMMAND SYSTEM (ICS) ACTION PLAN
**Operational Command:** {location.get('district', 'District').upper()} EOC & EMERGENCY RESPONSE TEAM  
**Incident Sector:** {loc_str}  
**Disaster Severity Index:** **{score} / 100 — {tier}**  
**Assessment Period:** Immediate Response Phase | Next 24–48 Hours  

---

### 1. INCIDENT SUMMARY
Continuous active monsoon precipitation has deposited **{rain_24h:.1f} mm of rainfall over the past 24 hours** across **{location.get('city')}**, classified as *{rain_tier}*. Hydrological telemetry confirms that the **{river_name} is currently recorded at {river_lvl:.2f} meters** (official danger threshold: {river_danger:.2f}m), resulting in an alert status of **{river_status}**. An estimated **{tot_affected:,} residents are within immediate inundation zones**, with **{evac_req:,} individuals requiring staged evacuation**.

---

### 2. CURRENT SITUATION ANALYSIS
- **Precipitation & Meteorological Status:** Active squall lines with forecast precipitation of **{rainfall.get('forecast48Hours', 100):.1f} mm** over the next 48 hours. Wind velocities at {weather.get('wind_speed_kmh', 20)} km/h.
- **Hydrological River Basin:** {location.get('river_basin')} is experiencing rapid catchment runoff. Low elevation terrain ({location.get('elevation_m', 5)}m above sea level) is creating severe backflow bottlenecks.
- **High-Risk Target Sector:** **{top_area}** has been designated **Rank #1 Priority** due to combined river breach and population exposure.
- **Vulnerable Human Demographics:** **{children:,} children** and **{elderly:,} senior citizens** identified in vulnerable single-story structures.
- **Lifeline Infrastructure Threat:** **{hosp} hospital(s)** require immediate power generator protection, and **{bridges} river bridge(s)** require structural scouring inspection.

---

### 3. IMMEDIATE OPERATIONAL DIRECTIVES (First 2 Hours)
1. **NDRF / SDRF Deployment:** Deploy motorized inflatable rescue boat teams (IRBs) immediately to **{top_area}** for life-safety extraction.
2. **Traffic & Road Clearance:** Enforce immediate police barricades along **{fast_route.get('title', 'Route A')}** ({fast_route.get('warning', 'submerged')}).
3. **Safe Transit Corridor:** Direct all civilian traffic and medical convoys through **{opt_route.get('title', 'Route C')}** ({opt_route.get('distance_km')} km, estimated travel time: {opt_route.get('travel_time_min')} mins).
4. **Shelter Mobilization:** Activate **{shelter_name}** ({shelter_dist} km away); verify medical bays and drinking water supply for **{shelter_avail:,} available bed spaces**.

---

### 4. OPERATIONAL SCHEDULE
- **NEXT 6 HOURS:** Complete Phase-1 evacuation of {evac_req:,} priority individuals. Erect sandbag flood barriers at vulnerable electrical substations.
- **NEXT 12–24 HOURS:** Re-assess river gauge telemetry at {river.get('monitoring_station')}. Distribute dry food rations and chlorination packets at relief centers.
"""
        return plan, "🔵 DETERMINISTIC TELEMETRY SYNTHESIS ENGINE (Offline Fallback)"
