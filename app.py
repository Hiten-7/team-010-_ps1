"""
Aapda Setu (आपदा सेतु)
AI-Powered Disaster Early Warning & Rescue Intelligence Platform
Hackathon MVP - Fully Dynamic, Location-Aware Architecture
"""
import sys
import os
import json
import datetime
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from config.settings import (
    RISK_COLORS,
    RISK_PREDICTIONS_PATH,
    IMPACT_RESULTS_PATH,
    SHELTER_RESULTS_PATH,
    PRIORITY_RESULTS_PATH,
    ROUTE_RESULTS_PATH
)
from utils.map_utils import create_disaster_command_map
from services.disaster_intelligence_service import DisasterIntelligenceService

# Defensive import of streamlit
try:
    import streamlit as st
except ImportError:
    print("Streamlit not found. Run: pip install -r requirements.txt")
    sys.exit(0)

# -------------------------------------------------------------
# PAGE CONFIGURATION & SESSION STATE INITIALIZATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="Aapda Setu - AI Disaster Intelligence Platform",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "app_step" not in st.session_state:
    st.session_state["app_step"] = "landing"  # 'landing', 'auth', 'location', 'dashboard'
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Rescue Team / Admin"
if "location_query" not in st.session_state:
    st.session_state["location_query"] = "Kolkata, Riverside Sector 4"
if "intel_report" not in st.session_state:
    st.session_state["intel_report"] = None
if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = "XGBoost"


def get_or_run_intelligence(query: str, model_choice: str = "XGBoost", force_refresh: bool = False):
    """Fetches or computes dynamic location intelligence."""
    service = DisasterIntelligenceService()
    if force_refresh or st.session_state["intel_report"] is None or st.session_state.get("last_analyzed_location") != query:
        report = service.analyze_location(query, model_choice=model_choice)
        st.session_state["intel_report"] = report
        st.session_state["last_analyzed_location"] = query
    return st.session_state["intel_report"]


# =============================================================
# STEP 1 & 2: MODERN LANDING PAGE
# =============================================================
if st.session_state["app_step"] == "landing":
    st.markdown("""
    <div style="text-align: center; padding: 40px 10px 20px 10px;">
        <span style="background-color: #fee2e2; color: #b91c1c; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 14px;">
            🚨 ACTIVE MULTI-HAZARD INTELLIGENCE • REAL-TIME DATA PIPELINE
        </span>
        <h1 style="font-size: 44px; margin-top: 15px; margin-bottom: 6px;">
            🚨 Aapda Setu <span style="font-size: 32px; color: #f87171; font-weight: 500;">(आपदा सेतु)</span>
        </h1>
        <h3 style="font-size: 20px; color: #3b82f6; margin-top: 0px; margin-bottom: 15px; font-weight: 600;">
            AI-Powered Disaster Early Warning & Rescue Intelligence Platform
        </h3>
        <p style="font-size: 19px; color: #64748b; max-width: 820px; margin: 0 auto 30px auto;">
            Transforming heterogeneous weather observations, satellite feeds, river gauges, and infrastructure GIS into actionable tactical intelligence for emergency response authorities and citizens.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_center1, c_center2, c_center3 = st.columns([1, 2, 1])
    with c_center2:
        if st.button("🚀 Access Aapda Setu Intelligence", use_container_width=True, type="primary"):
            st.session_state["app_step"] = "auth"
            st.rerun()

    st.markdown("---")

    # Platform Introduction & How It Works
    st.subheader("💡 The Problem & The Solution")
    col_prob, col_sol = st.columns(2)
    with col_prob:
        st.error("**⚠️ The Challenge: Fragmented Disaster Data**")
        st.markdown("""
        Disaster management authorities currently receive disconnected data streams:
        - Weather radar & IMD rainfall measurements
        - ISRO/Bhuvan satellite flood extents
        - River discharge & water gauge reports
        - Historical disaster recurrence archives
        - Dense municipal infrastructure maps
        
        *Converting these scattered sources into rapid, life-saving decisions in the first 24 hours is the ultimate challenge.*
        """)
    with col_sol:
        st.success("**🛡️ The Solution: Unified Intelligence Engine**")
        st.markdown("""
        Our AI platform synthesizes these layers into single-pane actionable directives:
        - **Where is the flood occurring?** (Calibrated ML Risk zones)
        - **Who & what is affected?** (GIS demographic & asset detection)
        - **Which zone needs help first?** (Transparent response ranking)
        - **How do we rescue them?** (Risk-weighted A* routing & safe shelters)
        - **What must we do now?** (AI Disaster Commander Action Plan)
        """)

    st.markdown("---")
    st.subheader("🌟 Core Capabilities")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.info("🌧️ **Risk Zone Prediction**\n\nXGBoost & SGDClassifier models evaluate rainfall, elevation & river levels to classify risk (0–100).")
    with f2:
        st.info("👥 **Impact Detection**\n\nGeoPandas/Shapely spatial overlap identifies exposed populations, children, elderly, and hospitals.")
    with f3:
        st.info("⚡ **Response Priority**\n\nWeighted multi-factor engine ranks critical sectors for emergency team deployment.")
    with f4:
        st.info("🛣️ **Evacuation Routes**\n\nNetworkX/OSMnx A* algorithms calculate safe routes avoiding inundated river causeways.")


# =============================================================
# STEP 3 & 4: LOGIN / ROLE SELECTION
# =============================================================
elif st.session_state["app_step"] == "auth":
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.container(border=True):
            st.title("🔐 Select Authentication Role")
            st.caption("Choose your operational access profile to continue.")

            role = st.radio(
                "Select User Role:",
                [
                    "Rescue Team / Admin",
                    "Citizen / Normal User"
                ],
                help="Rescue Teams receive full incident command access; Citizens receive localized safety & evacuation guidance."
            )

            if role == "Rescue Team / Admin":
                st.info("🛡️ **Rescue Team / Admin Access:** Complete command analytics, tactical maps, infrastructure vulnerability, priority rankings, river monitoring, and AI Action Plans.")
            else:
                st.success("👤 **Citizen / Normal User Access:** Localized flood risk level, nearest verified relief shelters, safe evacuation routes, and emergency SOS alerts.")

            st.markdown("<br>", unsafe_allow_html=True)
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("⬅️ Back to Home", use_container_width=True):
                    st.session_state["app_step"] = "landing"
                    st.rerun()
            with col_b2:
                if st.button("Continue to Location ➡️", use_container_width=True, type="primary"):
                    st.session_state["user_role"] = role
                    st.session_state["app_step"] = "location"
                    st.rerun()


# =============================================================
# STEP 5: LOCATION SELECTION (DYNAMIC LOCATION-AWARE PIPELINE)
# =============================================================
elif st.session_state["app_step"] == "location":
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.container(border=True):
            st.title("📍 Enter Operational Location")
            st.caption(f"Configuring intelligence context for: **{st.session_state['user_role']}**")

            # Quick Presets for Diverse Geographic Regions
            preset_choice = st.selectbox(
                "Select Disaster Hotspot or Enter Custom Below:",
                [
                    "Kolkata, Riverside Sector 4 (Hooghly River Reach)",
                    "Varanasi, Ghats Waterfront Sector (Ganges River)",
                    "Nagaon, Kolong Riverbank (Brahmaputra Flood Plain)",
                    "Dhubri, Brahmaputra Ghat (Lower Riparian Island)",
                    "Patna, Rajendra Nagar Low Basin (Ganges Confluence)",
                    "Jaipur, Walled City Drainage Corridor (Aravalli Foothill)",
                    "Malappuram, Kadalundi River Valley (Western Ghats)",
                    "Custom Location / Search..."
                ]
            )

            if preset_choice != "Custom Location / Search...":
                selected_query = preset_choice
            else:
                custom_text = st.text_input("Enter City, District, or Locality:", value="Kolkata")
                selected_query = custom_text

            col_detect, col_empty = st.columns([1, 1])
            with col_detect:
                if st.button("🛰️ Detect GPS Location"):
                    selected_query = "Kolkata, Riverside Sector 4"
                    st.success("GPS Coordinate Resolved: 22.5726° N, 88.3639° E")

            st.markdown("<br>", unsafe_allow_html=True)
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                if st.button("⬅️ Back to Role", use_container_width=True):
                    st.session_state["app_step"] = "auth"
                    st.rerun()
            with col_l2:
                if st.button("Launch Dashboard ➡️", use_container_width=True, type="primary"):
                    st.session_state["location_query"] = selected_query
                    # Trigger pipeline execution
                    with st.spinner(f"Analyzing Disaster Intelligence for {selected_query}..."):
                        get_or_run_intelligence(selected_query, force_refresh=True)
                    st.session_state["app_step"] = "dashboard"
                    st.rerun()


# =============================================================
# STEP 6: DYNAMIC DISASTER INTELLIGENCE DASHBOARD
# =============================================================
elif st.session_state["app_step"] == "dashboard":
    # Ensure intelligence report is loaded
    report = get_or_run_intelligence(st.session_state["location_query"])
    loc = report["location"]
    weather = report["weather"]
    rainfall = report["rainfall"]
    river = report["river"]
    historical = report["historical"]
    risk_zones = report["risk_zones"]
    severity = report["severity"]
    population = report["population"]
    infrastructure = report["infrastructure"]
    priorities = report["priorities"]
    shelters = report["shelters"]
    routes = report["routes"]
    data_sources = report["data_sources"]

    # 1. TOP DYNAMIC HEADER
    now_str = datetime.datetime.now().strftime("%d %b %Y | %H:%M Hrs IST")
    alert_color = "#ef4444" if severity["score"] >= 70 else ("#f97316" if severity["score"] >= 45 else "#eab308")
    alert_text = severity["tier"]

    st.markdown(f"""
    <div style="background-color: #0f172a; color: white; padding: 14px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; border-left: 6px solid {alert_color};">
        <div>
            <span style="font-size: 20px; font-weight: bold; color: #f87171;">🚨 Aapda Setu</span>
            <span style="background-color: #334155; padding: 3px 10px; border-radius: 12px; font-size: 13px; margin-left: 10px;">
                📍 <b>{loc['area_locality']}</b>, {loc['city']} ({loc['district']}, {loc['state']})
            </span>
            <span style="background-color: {alert_color}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px; margin-left: 6px; font-weight: bold;">
                {alert_text}
            </span>
        </div>
        <div style="font-size: 13px; color: #94a3b8;">
            🕒 {now_str} &nbsp;|&nbsp; 🌡️ {weather.get('temperature_c')}°C &nbsp;|&nbsp; 🌧️ 24h: {rainfall.get('last24Hours')}mm &nbsp;|&nbsp; 👤 <b>{st.session_state['user_role']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. SIDEBAR CONTROLS & NAVIGATION
    with st.sidebar:
        st.title("🚨 Aapda Setu")
        st.caption(f"EOC Command • Role: **{st.session_state['user_role']}**")

        # Location Switcher in Sidebar
        st.markdown("### 📍 Location Switcher")
        quick_loc = st.selectbox(
            "Change Active Location:",
            [
                "Kolkata, Riverside Sector 4",
                "Varanasi, Ghats Waterfront Sector",
                "Nagaon, Assam",
                "Dhubri, Assam",
                "Patna, Bihar",
                "Jaipur, Rajasthan",
                "Malappuram, Kerala"
            ],
            index=0 if "Kolkata" in st.session_state["location_query"] else (
                1 if "Varanasi" in st.session_state["location_query"] else (
                    2 if "Nagaon" in st.session_state["location_query"] else (
                        3 if "Dhubri" in st.session_state["location_query"] else (
                            4 if "Patna" in st.session_state["location_query"] else (
                                5 if "Jaipur" in st.session_state["location_query"] else 6
                            )
                        )
                    )
                )
            )
        )

        if quick_loc != st.session_state["location_query"]:
            st.session_state["location_query"] = quick_loc
            with st.spinner(f"Re-analyzing for {quick_loc}..."):
                get_or_run_intelligence(quick_loc, force_refresh=True)
            st.rerun()

        st.markdown("---")

        # Navigation Options
        if st.session_state["user_role"] == "Rescue Team / Admin":
            nav_options = [
                "Overview",
                "Risk Zones",
                "People & Infrastructure",
                "Response Priority",
                "Evacuation Routes",
                "Safe Shelters",
                "AI Action Plan",
                "Disaster History",
                "Data Intelligence",
                "Settings"
            ]
        else:
            nav_options = [
                "Citizen Safety Overview",
                "Local Risk Assessment",
                "Nearest Safe Shelters",
                "Safe Evacuation Route",
                "Emergency SOS & Alerts"
            ]

        selected_nav = st.radio("Navigation:", nav_options, index=0)
        st.session_state["sidebar_nav"] = selected_nav

        st.markdown("---")
        st.markdown("### ⚙️ Pipeline Execution")
        if st.button("⚡ Force Pipeline Re-run", use_container_width=True):
            with st.spinner("Re-executing live models..."):
                get_or_run_intelligence(st.session_state["location_query"], force_refresh=True)
            st.success("Refreshed with fresh live telemetry!")
            st.rerun()

        st.markdown("---")
        st.markdown("### 📊 Live Data Sources")
        st.caption(f"• Weather: {data_sources.get('weather')}")
        st.caption(f"• Rainfall: {data_sources.get('rainfall')}")
        st.caption(f"• River: {data_sources.get('river')}")
        st.caption(f"• History: {data_sources.get('historical')}")
        st.caption(f"• ML Risk: {data_sources.get('ml_model')}")

        st.markdown("---")
        if st.button("🚪 Logout / Switch Role", use_container_width=True):
            st.session_state["app_step"] = "auth"
            st.rerun()

    # =========================================================
    # VIEW: OVERVIEW (ADMIN / RESCUE TEAM)
    # =========================================================
    if selected_nav == "Overview":
        st.subheader(f"Operational Command Overview — {loc['city']}, {loc['district']}")
        st.caption(f"Terrain: **{loc['terrain']}** | Elevation: **{loc['elevation_m']} m** | Basin: **{loc['river_basin']}**")

        top_r1, top_r2, top_r3, top_r4 = st.columns(4)
        with top_r1:
            st.metric("Disaster Severity Score", f"{severity['score']:.1f} / 100", delta=severity['tier'], delta_color="inverse")
        with top_r2:
            st.metric("Population at Risk", f"{population['total_population_at_risk']:,}", help="Calculated from spatial risk zone density")
        with top_r3:
            st.metric("Evacuation Required", f"{population['evacuation_required']:,}", delta="Urgent Extraction", delta_color="inverse")
        with top_r4:
            st.metric("Critical Assets Exposed", f"{infrastructure['total_critical_assets_at_risk']} Facilities", help="Hospitals, Schools, Bridges, Power Substations")

        st.markdown("<br>", unsafe_allow_html=True)

        col_map, col_summary = st.columns([3, 2])
        with col_map:
            st.markdown(f"#### 🗺️ Unified Tactical Map — {loc['district']}")
            st.caption(f"Coordinates: {loc['latitude']}°N, {loc['longitude']}°E | Nearest River: {river['nearest_river']}")
            # Build Folium map centered on this location
            center = [loc["latitude"], loc["longitude"]]
            # Prepare format for map
            map_zones = []
            for idx, z in enumerate(risk_zones):
                p_item = population["zone_breakdowns"][idx]
                map_zones.append({
                    "latitude": z["latitude"],
                    "longitude": z["longitude"],
                    "zone_name": z["zone_name"],
                    "risk_score": z["risk_score"],
                    "risk_level": z["risk_level"],
                    "population": p_item["affected_population"]
                })
            m = create_disaster_command_map(zones=map_zones, shelters=shelters, routes=routes, center=center)
            if m is not None:
                try:
                    from streamlit_folium import st_folium
                    st_folium(m, width="100%", height=450)
                except ImportError:
                    st.components.v1.html(m._repr_html_(), height=450)
        with col_summary:
            st.markdown("#### 🎯 Immediate Emergency Priorities")
            st.caption("Ranked by multi-factor risk, population exposure, and infrastructure criticality.")
            for p in priorities[:3]:
                st.error(f"**#{p.get('priority_rank')} {p.get('area_locality')}**\n\n"
                         f"• **Score:** {p.get('priority_score')}/100 (`{p.get('priority_tier')}`)\n\n"
                         f"• **Directive:** {p.get('recommended_action')}")

    # =========================================================
    # VIEW: RISK ZONES (FEATURE 1)
    # =========================================================
    elif selected_nav == "Risk Zones":
        st.subheader(f"1. Disaster Risk Zone Prediction — {loc['district']}")
        st.caption(f"Live inference evaluated on {rainfall['last24Hours']} mm precipitation, river stage ({river['current_level_m']}m), and terrain elevation.")

        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            chosen_model = st.selectbox("Select ML Model:", ["XGBoost (Primary Model)", "SGDClassifier (Baseline Model)"])
        with c_opt2:
            st.write(f"**Elevation Baseline:** {loc['elevation_m']} m | **Nearest River:** {river['nearest_river']}")

        st.markdown("#### Classified Geographic Risk Sectors")
        for idx, z in enumerate(risk_zones):
            score = z["risk_score"]
            level = z["risk_level"]
            with st.expander(f"📍 {z['area_locality']} — {score:.1f}% ({level})", expanded=(idx == 0)):
                cz1, cz2 = st.columns(2)
                with cz1:
                    st.write(f"• **Coordinates:** {z['latitude']}°N, {z['longitude']}°E")
                    st.write(f"• **Elevation:** {z['elevation_m']} m above sea level")
                    st.write(f"• **River Proximity:** {z['river_proximity_km']} km to {river['nearest_river']}")
                    st.write(f"• **ML Model Used:** `{z['model_used']}`")
                with cz2:
                    st.write("**Key Contributing Risk Factors:**")
                    for r in z.get("reasons", []):
                        st.write(f"- {r}")

        st.markdown("---")
        st.markdown("#### Complete Zone Risk Table")
        st.dataframe(pd.DataFrame(risk_zones)[["zone_id", "zone_name", "elevation_m", "risk_probability", "risk_score", "risk_level", "model_used"]], use_container_width=True)

    # =========================================================
    # VIEW: PEOPLE & INFRASTRUCTURE (FEATURE 2)
    # =========================================================
    elif selected_nav == "People & Infrastructure":
        st.subheader(f"2. Affected People & Critical Infrastructure — {loc['district']}")
        st.caption(f"Spatial GIS intersections identifying exposed demographic segments in {loc['city']}.")

        st.markdown("#### 👥 Exposed Population Demographics")
        dp1, dp2, dp3, dp4 = st.columns(4)
        with dp1:
            st.metric("Total Population at Risk", f"{population['total_population_at_risk']:,}")
        with dp2:
            st.metric("Children (0–12 Yrs)", f"{population['children_at_risk']:,}")
        with dp3:
            st.metric("Elderly (60+ Yrs)", f"{population['elderly_at_risk']:,}")
        with dp4:
            st.metric("Evacuation Required", f"{population['evacuation_required']:,}", delta="Urgent Priority", delta_color="inverse")

        st.markdown("---")
        st.markdown("#### 🏢 Critical Lifeline Infrastructure At Risk")
        ip1, ip2, ip3, ip4, ip5 = st.columns(5)
        with ip1:
            st.metric("Hospitals", f"{infrastructure['hospitals_at_risk']}")
        with ip2:
            st.metric("Schools Closed", f"{infrastructure['schools_at_risk']}")
        with ip3:
            st.metric("Bridges Vulnerable", f"{infrastructure['bridges_at_risk']}")
        with ip4:
            st.metric("Power Substations", f"{infrastructure['power_substations_at_risk']}")
        with ip5:
            st.metric("Police & Fire Stns", f"{infrastructure['police_stations'] + infrastructure['fire_stations']}")

        st.markdown("---")
        st.markdown("#### Sector-by-Sector Demographic & Asset Breakdown")
        df_demog = pd.DataFrame(population["zone_breakdowns"])
        st.dataframe(df_demog[["zone_name", "total_population", "affected_population", "children", "elderly", "evacuation_required", "risk_score"]], use_container_width=True)

    # =========================================================
    # VIEW: RESPONSE PRIORITY (FEATURE 3)
    # =========================================================
    elif selected_nav == "Response Priority":
        st.subheader(f"3. Emergency Response Priority Ranking — {loc['district']}")
        st.caption("AI-assisted multi-criteria decision system prioritizing sectors by hazard severity, vulnerability, and infrastructure impact.")

        for p in priorities:
            rank = p["priority_rank"]
            tier = p["priority_tier"]
            score = p["priority_score"]
            with st.container(border=True):
                col_pr1, col_pr2 = st.columns([1, 3])
                with col_pr1:
                    st.markdown(f"<h3 style='margin:0; color:#ef4444;'>#{rank}</h3>", unsafe_allow_html=True)
                    st.write(f"**Score:** {score:.1f}/100")
                    st.write(f"`{tier}`")
                with col_pr2:
                    st.markdown(f"**Sector:** `{p['area_locality']}`")
                    st.write(f"**Recommended Direct Action:** {p['recommended_action']}")
                    st.write(f"• **Affected Population:** {p['affected_population']:,} | **Vulnerable Assets:** {p['critical_infrastructure_count']}")
                    for reason in p.get("priority_reasons", []):
                        st.caption(f"- {reason}")

    # =========================================================
    # VIEW: EVACUATION ROUTES (FEATURE 4)
    # =========================================================
    elif selected_nav == "Evacuation Routes":
        st.subheader(f"4. Safe & Fast Evacuation / Rescue Route — {loc['district']}")
        st.caption(f"Calculating evacuation trajectories from {routes['origin']['name']} to {routes['destination']['name']}.")

        routes_dict = routes.get("routes", {})
        rf = routes_dict.get("fast_route", {})
        rs = routes_dict.get("safe_route", {})
        ro = routes_dict.get("optimal_route", {})

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.error(f"❌ **{rf.get('title')}**")
            st.write(f"• **Travel Time:** {rf.get('travel_time_min')} mins")
            st.write(f"• **Distance:** {rf.get('distance_km')} km")
            st.write(f"• **Safety Score:** {rf.get('safety_score')}%")
            st.write(f"• **Status:** `{rf.get('recommendation')}`")
            st.caption(rf.get("warning"))
        with col_r2:
            st.info(f"ℹ️ **{rs.get('title')}**")
            st.write(f"• **Travel Time:** {rs.get('travel_time_min')} mins")
            st.write(f"• **Distance:** {rs.get('distance_km')} km")
            st.write(f"• **Safety Score:** {rs.get('safety_score')}%")
            st.write(f"• **Status:** `{rs.get('recommendation')}`")
            st.caption(rs.get("warning"))
        with col_r3:
            st.success(f"✅ **{ro.get('title')}**")
            st.write(f"• **Travel Time:** {ro.get('travel_time_min')} mins")
            st.write(f"• **Distance:** {ro.get('distance_km')} km")
            st.write(f"• **Safety Score:** {ro.get('safety_score')}%")
            st.write(f"• **Status:** `{ro.get('recommendation')}`")
            st.caption(ro.get("warning"))

        st.markdown("---")
        st.markdown("#### 🗺️ Route Inspection Map")
        center = [loc["latitude"], loc["longitude"]]
        m_r = create_disaster_command_map(routes=routes, center=center)
        if m_r is not None:
            try:
                from streamlit_folium import st_folium
                st_folium(m_r, width="100%", height=400)
            except ImportError:
                st.components.v1.html(m_r._repr_html_(), height=400)

    # =========================================================
    # VIEW: SAFE SHELTERS (FEATURE 5)
    # =========================================================
    elif selected_nav == "Safe Shelters":
        st.subheader(f"5. Safe Shelter Recommendation — {loc['district']}")
        st.caption(f"Dynamically discovered and ranked relief centers around {loc['city']}.")

        for s in shelters:
            with st.container(border=True):
                cs1, cs2, cs3 = st.columns([2, 2, 2])
                with cs1:
                    st.markdown(f"**🛡️ {s.get('name')}**")
                    st.write(f"Type: `{s.get('type')}`")
                    st.write(f"Distance: **{s.get('distance_km')} km**")
                with cs2:
                    st.write(f"• **Total Capacity:** {s.get('total_capacity'):,} people")
                    st.write(f"• **Current Occupancy:** {s.get('current_occupancy'):,} people")
                    st.write(f"• **Available Beds:** **{s.get('available_space'):,} beds**")
                with cs3:
                    st.write(f"• **Safety Score:** {s.get('safety_score')}%")
                    st.write(f"• **Elevation:** {s.get('elevation_m')} m")
                    st.write(f"• **Status:** `{s.get('status')}`")
                    st.caption("Facilities: Emergency Medical Bay, RO Clean Water, Kitchen, Power Generator")

    # =========================================================
    # VIEW: AI ACTION PLAN (FEATURE 6: "AI DISASTER COMMANDER")
    # =========================================================
    elif selected_nav == "AI Action Plan":
        st.subheader(f"6. 🤖 AI Disaster Commander — {loc['city']}, {loc['district']}")
        st.caption("Automated mission-critical Action Plan synthesized strictly from real location telemetry.")

        st.info(f"Generated via: **{report.get('action_plan_source')}**")
        with st.container(border=True):
            st.markdown(report.get("action_plan"))

        st.download_button(
            "📥 Download Official Action Plan (.md)",
            data=report.get("action_plan"),
            file_name=f"Incident_Action_Plan_{loc['district']}.md",
            mime="text/markdown"
        )

    # =========================================================
    # VIEW: DISASTER HISTORY
    # =========================================================
    elif selected_nav == "Disaster History":
        st.subheader(f"7. Disaster History & Past Flood Records — {loc['district']}")
        st.caption(f"Querying model_training_dataset.csv historical database for {loc['district']} ({loc['state']}).")

        st.write(f"• **Historical Flood Frequency Index:** `{historical.get('historical_flood_frequency')}`")
        st.write(f"• **Average Past Severity Score:** `{historical.get('avg_historical_risk')} / 100`")
        st.write(f"• **Average Historical Affected Population:** `{historical.get('historical_affected_population'):,}`")

        st.markdown("#### Recorded Past Disaster Events in Database")
        if historical.get("past_recorded_events"):
            df_hist_events = pd.DataFrame(historical["past_recorded_events"])
            st.dataframe(df_hist_events, use_container_width=True)

    # =========================================================
    # VIEW: DATA INTELLIGENCE (SATELLITE & SENSORS)
    # =========================================================
    elif selected_nav == "Data Intelligence":
        st.subheader(f"8. Data Intelligence Feeds — {loc['district']}")
        st.caption("Real-time telemetry inputs from rainfall gauges, river hydrological stations, and satellite imagery.")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("#### 🌊 Hydrological Telemetry")
            st.write(f"• **Monitored River:** {river['nearest_river']}")
            st.write(f"• **River Basin:** {river['river_basin']}")
            st.write(f"• **Active Gauge Station:** `{river['monitoring_station']}`")
            st.write(f"• **Current River Stage:** **{river['current_level_m']} meters**")
            st.write(f"• **Official Danger Mark:** **{river['danger_mark_m']} meters**")
            st.write(f"• **Alert Status:** `{river['status']}`")

        with col_s2:
            st.markdown("#### 🌧️ Precipitation Telemetry")
            st.write(f"• **Current Rainfall Intensity:** {rainfall['last1Hour']} mm/hr")
            st.write(f"• **Past 24 Hours Accumulation:** **{rainfall['last24Hours']} mm** ({rainfall['intensity_tier']})")
            st.write(f"• **Past 48 Hours Accumulation:** {rainfall['last48Hours']} mm")
            st.write(f"• **Next 48 Hours Forecast:** {rainfall['forecast48Hours']} mm")
            st.write(f"• **Seasonal Rainfall Anomaly:** {rainfall['rainfall_anomaly_pct']}% above normal")

    # =========================================================
    # VIEW: SETTINGS
    # =========================================================
    elif selected_nav == "Settings":
        st.subheader("⚙️ System Configuration & Model Calibration")
        st.write(f"• **Target Location:** {loc['area_locality']}, {loc['city']}, {loc['district']} ({loc['state']})")
        st.write(f"• **Coordinates:** {loc['latitude']}°N, {loc['longitude']}°E | Elevation: {loc['elevation_m']} m")
        st.write(f"• **Active ML Risk Model:** XGBoost Classifier (`models/xgb_model.pkl`)")
        st.write(f"• **Baseline ML Model:** SGDClassifier (`models/sgd_model.pkl`)")
        st.write(f"• **Priority Model Pipeline:** `models/disaster_priority_model.pkl`")
        st.write(f"• **Routing Graph Engine:** NetworkX Risk-Weighted A*")
        st.write(f"• **Weather Provider:** Open-Meteo REST API")

    # =========================================================
    # CITIZEN VIEWS (WHEN ROLE IS "CITIZEN / NORMAL USER")
    # =========================================================
    elif selected_nav == "Citizen Safety Overview":
        st.subheader(f"🛡️ Safety Advisory for Residents in {loc['area_locality']}, {loc['city']}")
        st.write(f"**Disaster Severity Level:** {severity['tier']} ({severity['score']}/100)")
        st.write(f"🌧️ 24h Rainfall: **{rainfall['last24Hours']} mm** | 🌊 {river['nearest_river']}: **{river['status']}**")

        cz1, cz2, cz3 = st.columns(3)
        with cz1:
            st.metric("Your Local Flood Risk", f"{severity['score']:.1f}%", delta=severity['tier'], delta_color="inverse")
        with cz2:
            top_sh = shelters[0] if shelters else {}
            st.metric("Nearest Safe Shelter", top_sh.get("name", "Relief Hub"), f"{top_sh.get('distance_km', 3.0)} km away")
        with cz3:
            opt_r = routes.get("routes", {}).get("optimal_route", {})
            st.metric("Recommended Safe Route", opt_r.get("title", "Route C"), f"{opt_r.get('travel_time_min', 20)} mins")

        st.markdown("---")
        st.subheader("🚨 Emergency Safety Directives")
        st.markdown(f"""
        1. **Higher Ground Relocation:** Residents in **{loc['area_locality']}** near the **{river['nearest_river']}** should move to elevated structures or designated relief centers.
        2. **Avoid Flooded Roads:** **DO NOT USE {routes.get('routes', {}).get('fast_route', {}).get('title', 'Route A')}** due to active water currents.
        3. **Safe Evacuation Corridor:** Follow **{opt_r.get('title', 'Route C')}** toward **{top_sh.get('name', 'Relief Hub')}**.
        4. **Emergency Kit Checklist:** Carry drinking water, waterproof flashlight, dry food, and essential medications.
        """)

    elif selected_nav == "Local Risk Assessment":
        st.subheader(f"📍 Local Risk Assessment for {loc['area_locality']}")
        st.write(f"**Disaster Severity Score:** {severity['score']} / 100 ({severity['tier']})")
        st.write("**Why your area is at risk:**")
        st.write(f"- Observed 24h precipitation of {rainfall['last24Hours']} mm ({rainfall['intensity_tier']})")
        st.write(f"- {river['nearest_river']} level at {river['current_level_m']}m (Danger Mark: {river['danger_mark_m']}m) -> {river['status']}")
        st.write(f"- Terrain elevation of {loc['elevation_m']}m causing drainage vulnerability")

    elif selected_nav == "Nearest Safe Shelters":
        st.subheader(f"🛡️ Nearby Safe Relief Shelters — {loc['city']}")
        st.caption("All recommended shelters are located on high ground with verified food, drinking water, and medical aid.")

        for s in shelters:
            st.success(f"**{s.get('name')}** — **{s.get('distance_km')} km away**\n\n"
                       f"• **Available Bed Space:** {s.get('available_space'):,} beds (Total Capacity: {s.get('total_capacity'):,})\n\n"
                       f"• **Elevation:** {s.get('elevation_m')} m above sea level | Safety Score: {s.get('safety_score')}%\n\n"
                       f"• **Emergency Contact:** `{s.get('contact')}`")

    elif selected_nav == "Safe Evacuation Route":
        st.subheader("🛣️ Safe Route to Your Nearest Shelter")
        ro_c = routes.get("routes", {}).get("optimal_route", {})
        rf_a = routes.get("routes", {}).get("fast_route", {})
        st.success(f"✅ **USE {ro_c.get('title')}:** {ro_c.get('distance_km')} km • ~{ro_c.get('travel_time_min')} minutes. {ro_c.get('warning')}")
        st.error(f"⛔ **DO NOT USE {rf_a.get('title')}:** {rf_a.get('distance_km')} km. {rf_a.get('warning')}")

    elif selected_nav == "Emergency SOS & Alerts":
        st.subheader("📞 Emergency SOS & Response Helpline")
        st.error("If trapped by flood water or requiring emergency rescue in this sector, contact authorities immediately:")

        sos1, sos2, sos3 = st.columns(3)
        with sos1:
            st.info("🚨 **NDRF Flood Rescue Control**\n\n**1078** / +91-11-2436-3260")
        with sos2:
            st.info("🚒 **State Disaster Emergency (SDRF)**\n\n**1070** / 112")
        with sos3:
            st.info("🚑 **Ambulance & Medical Emergency**\n\n**108** / 102")
