"""
AI-Powered Disaster Early Warning & Rescue Intelligence Platform
Command Center Application (Streamlit)
Maintained by: Member 4 (Streamlit / Integration)
"""
import sys
import os
import json
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
from utils.data_loader import (
    load_risk_predictions,
    load_impact_results,
    load_shelter_results,
    load_priority_results,
    load_route_results,
    load_rainfall_data
)
from utils.map_utils import create_disaster_command_map
from ai.action_plan import generate_emergency_action_plan

# Defensive check for direct python execution
try:
    import streamlit as st
except ImportError:
    print("\n" + "=" * 60)
    print("Streamlit is not installed in the current Python environment.")
    print("To launch the Command Center UI, please run:")
    print("    pip install -r requirements.txt")
    print("    streamlit run app.py")
    print("=" * 60 + "\n")
    sys.exit(0)

# Set page configuration
st.set_page_config(
    page_title="Disaster Command Intelligence Platform",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Command Center Tactical Dark Styling
st.markdown("""
<style>
    /* Command center theme */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .main-header {
        background: linear-gradient(90deg, #1f2937, #111827);
        padding: 18px 24px;
        border-radius: 8px;
        border-left: 6px solid #e74c3c;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        margin: 4px 0;
    }
    .metric-label {
        font-size: 13px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-critical {
        background-color: #7f1d1d;
        color: #fecaca;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 12px;
    }
    .badge-warning {
        background-color: #78350f;
        color: #fde68a;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 12px;
    }
    .badge-safe {
        background-color: #064e3b;
        color: #a7f3d0;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 12px;
    }
    .sample-notice {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 10px 15px;
        margin-bottom: 15px;
        border-radius: 4px;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR CONTROLS & PIPELINE RUNNER
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/siren.png", width=64)
    st.title("EOC Tactical Control")
    st.caption("District Disaster Management Authority (DDMA)")
    st.markdown("---")

    # District Selector
    selected_district = st.selectbox(
        "📍 Active District",
        ["KOLKATA (WEST BENGAL)", "VARANASI (UTTAR PRADESH)", "NAGAON (ASSAM)", "DHUBRI (ASSAM)", "PATNA (BIHAR)", "MALAPPURAM (KERALA)"],
        index=0
    )

    st.markdown("### ⚙️ Pipeline Execution")
    if st.button("⚡ Run Full AI Pipeline", use_container_width=True, type="primary"):
        with st.spinner("Executing ML, GIS, Priority & Routing Engines..."):
            try:
                import ml.predict_risk as pr
                import gis.impact as gi
                import gis.shelter as gs
                import routing.priority as rp
                import routing.route as rr

                pr.run_risk_prediction()
                gi.run_impact_analysis()
                gs.recommend_shelters()
                rp.run_priority_ranking()
                rr.find_evacuation_routes()
                st.success("All 5 Engine Modules Recomputed!")
                st.rerun()
            except Exception as e:
                st.error(f"Pipeline error: {e}")

    st.markdown("---")
    st.markdown("### 📁 Telemetry Status")
    st.markdown(f"- **ML Risk:** `{'✅ Available' if RISK_PREDICTIONS_PATH.exists() else '⚠️ Fallback'}`")
    st.markdown(f"- **GIS Impact:** `{'✅ Available' if IMPACT_RESULTS_PATH.exists() else '⚠️ Fallback'}`")
    st.markdown(f"- **Shelter Rec:** `{'✅ Available' if SHELTER_RESULTS_PATH.exists() else '⚠️ Fallback'}`")
    st.markdown(f"- **Response Priority:** `{'✅ Available' if PRIORITY_RESULTS_PATH.exists() else '⚠️ Fallback'}`")
    st.markdown(f"- **Rescue Routing:** `{'✅ Available' if ROUTE_RESULTS_PATH.exists() else '⚠️ Fallback'}`")

    st.markdown("---")
    llm_api_key = st.text_input("🔑 Gemini API Key (Optional)", type="password", help="Leave blank to use deterministic offline response generator")


# ==========================================
# LOAD PIPELINE DATA
# ==========================================
df_risk, risk_is_sample = load_risk_predictions()
impacts, impact_is_sample = load_impact_results()
shelters, shelter_is_sample = load_shelter_results()
priorities, priority_is_sample = load_priority_results()
routes_data, route_is_sample = load_route_results()
rainfall_df = load_rainfall_data()

is_demo_mode = any([risk_is_sample, impact_is_sample, shelter_is_sample, priority_is_sample, route_is_sample])


# ==========================================
# HEADER SECTION
# ==========================================
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin: 0; color: #f87171;">🚨 AI-Powered Disaster Early Warning & Rescue Intelligence</h2>
            <p style="margin: 5px 0 0 0; color: #9ca3af;">Severe Monsoon Depression Event — Operational Assessment Window: Next 24-48 Hours</p>
        </div>
        <div>
            <span class="badge-critical">ALERT LEVEL: RED (ACTIVE EMERGENCY)</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if is_demo_mode:
    st.markdown("""
    <div class="sample-notice">
        ℹ️ <b>DEMO / SAMPLE DATA MODE ACTIVE:</b> Running with realistic Indian monsoon flood simulation dataset (Kolkata Metropolitan Area).
        Real ISRO Bhuvan / IMD feeds will seamlessly populate these interfaces once configured.
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# NAVIGATION TABS
# ==========================================
tabs = st.tabs([
    "📊 1. Dashboard",
    "🗺️ 2. Risk Map",
    "🏢 3. Impact Analysis",
    "⚡ 4. Emergency Priority",
    "🚑 5. Routes & Shelters",
    "📋 6. AI Action Plan"
])


# ==========================================
# TAB 1: COMMAND DASHBOARD
# ==========================================
with tabs[0]:
    st.subheader("Operational Situation Overview")

    # Calculate key metrics
    rainfall_val = rainfall_df["Rainfall_mm"].iloc[0] if not rainfall_df.empty else 215.4
    overall_risk = float(df_risk["risk_score"].max()) if not df_risk.empty else 93.4
    risk_level = "CRITICAL" if overall_risk >= 80 else ("HIGH" if overall_risk >= 60 else "MODERATE")
    pop_at_risk = sum(item.get("population", item.get("affected_population", 0)) for item in impacts)
    infra_count = sum(item.get("hospitals", 0) + item.get("schools", 0) + item.get("bridges", 0) for item in impacts)
    high_risk_zones = int((df_risk["risk_score"] >= 70.0).sum()) if not df_risk.empty else 2
    top_priority_zone = priorities[0]["zone_name"] if priorities else "Kolkata South East Lowlands"
    top_shelter = shelters[0]["shelter_name"] if shelters else "Salt Lake Stadium Relief Hub"
    opt_route = routes_data.get("routes", {}).get("optimal_route", {})
    route_name = opt_route.get("title", "Route C (Risk-Aware Bypass)")

    # Row 1: High Level Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">24h Rainfall (IMD)</div>
            <div class="metric-value" style="color: #60a5fa;">{rainfall_val:.1f} mm</div>
            <span class="badge-critical">HEAVY MONSOON</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Max Risk Score</div>
            <div class="metric-value" style="color: #ef4444;">{overall_risk:.1f} / 100</div>
            <span class="badge-critical">{risk_level}</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Population at Risk</div>
            <div class="metric-value" style="color: #f59e0b;">{pop_at_risk:,}</div>
            <span class="badge-warning">Across {len(df_risk)} Sectors</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vulnerable Infrastructure</div>
            <div class="metric-value" style="color: #a855f7;">{infra_count} Units</div>
            <span class="badge-warning">Hospitals, Schools, Bridges</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: Operational Priorities Summary
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"""
        <div class="metric-card" style="text-align: left;">
            <div class="metric-label">Highest Priority Target Zone</div>
            <div style="font-size: 18px; font-weight: bold; color: #f87171; margin-top: 5px;">
                🎯 {top_priority_zone}
            </div>
            <p style="font-size: 13px; color: #9ca3af; margin-top: 5px;">
                High flood susceptibility, dense settlement, and constrained drainage egress.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class="metric-card" style="text-align: left;">
            <div class="metric-label">Primary Designated Safe Shelter</div>
            <div style="font-size: 18px; font-weight: bold; color: #34d399; margin-top: 5px;">
                🛡️ {top_shelter}
            </div>
            <p style="font-size: 13px; color: #9ca3af; margin-top: 5px;">
                Elevated high-ground relief complex with {shelters[0].get('available_capacity', 4000):,} available capacity.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with r3:
        st.markdown(f"""
        <div class="metric-card" style="text-align: left;">
            <div class="metric-label">Tactical Recommended Route</div>
            <div style="font-size: 18px; font-weight: bold; color: #38bdf8; margin-top: 5px;">
                🛣️ {route_name}
            </div>
            <p style="font-size: 13px; color: #9ca3af; margin-top: 5px;">
                {opt_route.get('distance_km', 11.6)} km • {opt_route.get('travel_time_min', 22.4)} min • Zero flood submergence.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Sector Risk Summary Table")
    st.dataframe(
        df_risk[["zone_id", "zone_name", "risk_probability", "risk_score", "risk_level", "model_used"]],
        use_container_width=True
    )


# ==========================================
# TAB 2: INTERACTIVE RISK MAP
# ==========================================
with tabs[1]:
    st.subheader("Spatial Intelligence Map")
    st.caption("Layered Tactical Display: Risk Polygons, Hospitals, Schools, Shelters & Evacuation Routes")

    # Render Map using Folium
    m = create_disaster_command_map(
        zones=impacts,
        shelters=shelters,
        routes=routes_data
    )

    if m is not None:
        try:
            # Check if streamlit-folium is available
            from streamlit_folium import st_folium
            st_folium(m, width="100%", height=560)
        except ImportError:
            # Fallback to pure HTML embedding
            st.components.v1.html(m._repr_html_(), height=560)
    else:
        st.warning("Folium map module is loading. Please ensure 'folium' is installed.")

    st.markdown("""
    **Map Legend:**
    - 🔴 **Red Zones:** High / Very High Risk Flood Inundation Sectors
    - 🟢 **Green Markers:** Certified Safe Relief Shelters (High Ground)
    - 🟢 **Solid Green Polyline:** Recommended Risk-Aware Rescue Corridor (Route C)
    - 🔴 **Dashed Red Polyline:** Dangerous Inundated River Route (Route A - Prohibited)
    - 🔵 **Blue Polyline:** Highland Safe Bypass (Route B)
    """)


# ==========================================
# TAB 3: GIS IMPACT ANALYSIS
# ==========================================
with tabs[2]:
    st.subheader("Vulnerable Population & Infrastructure Breakdown")
    st.caption("Derived via GeoPandas / Shapely Spatial Intersections")

    df_impact = pd.DataFrame(impacts)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.dataframe(
            df_impact[[
                "zone_id", "zone_name", "population", "hospitals", "schools", "roads", "bridges", "risk_score"
            ]],
            column_config={
                "population": st.column_config.NumberColumn("Affected Pop", format="%d"),
                "hospitals": st.column_config.NumberColumn("Hospitals At Risk"),
                "schools": st.column_config.NumberColumn("Schools Compromised"),
                "roads": st.column_config.NumberColumn("Roads Compromised (km)"),
                "bridges": st.column_config.NumberColumn("Vulnerable Bridges"),
                "risk_score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100)
            },
            use_container_width=True
        )

    with col_b:
        st.bar_chart(
            df_impact.set_index("zone_id")[["population"]],
            color="#ef4444"
        )
        st.caption("Affected Population Distribution by Zone")


# ==========================================
# TAB 4: EMERGENCY RESPONSE PRIORITY
# ==========================================
with tabs[3]:
    st.subheader("Emergency Response Priority Ranking")
    st.markdown("""
    **Evaluation Formula:** `Priority Score = 40% Risk + 25% Population + 20% Critical Infrastructure + 15% Accessibility Urgency`
    """)

    df_priorities = pd.DataFrame(priorities)
    st.dataframe(
        df_priorities[[
            "priority_rank", "zone_id", "zone_name", "priority_score", "priority_level",
            "risk_score", "affected_population", "critical_infrastructure_count"
        ]],
        column_config={
            "priority_rank": st.column_config.NumberColumn("Rank", format="#%d"),
            "priority_score": st.column_config.ProgressColumn("Priority Score", min_value=0, max_value=100),
            "priority_level": st.column_config.TextColumn("Tier"),
            "affected_population": st.column_config.NumberColumn("Pop Affected", format="%d")
        },
        use_container_width=True
    )


# ==========================================
# TAB 5: ROUTES & SHELTERS
# ==========================================
with tabs[4]:
    st.subheader("Evacuation Routing & Relief Shelter Allocation")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("### 🛣️ Route Comparison Matrix")
        routes_dict = routes_data.get("routes", {})

        for r_key, r_info in routes_dict.items():
            is_rec = "RECOMMENDED PRIMARY" in r_info.get("recommendation", "")
            border_col = "#22c55e" if is_rec else ("#ef4444" if "NOT" in r_info.get("recommendation", "") else "#3b82f6")

            st.markdown(f"""
            <div style="border: 1px solid {border_col}; padding: 14px; border-radius: 8px; margin-bottom: 12px; background-color: #161b22;">
                <div style="display: flex; justify-content: space-between;">
                    <b>{r_info.get('title')}</b>
                    <span style="color: {border_col}; font-weight: bold;">{r_info.get('recommendation')}</span>
                </div>
                <div style="margin-top: 6px; font-size: 14px;">
                    📏 Distance: <b>{r_info.get('distance_km')} km</b> | ⏱️ Transit Time: <b>{r_info.get('travel_time_min')} mins</b>
                </div>
                <div style="font-size: 13px; color: #9ca3af; margin-top: 4px;">
                    ⚠️ Hazard Status: <b>{r_info.get('flood_risk_level')}</b> ({r_info.get('warning')})
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_r2:
        st.markdown("### 🛡️ Relief Shelter Capacity & Status")
        df_shelters = pd.DataFrame(shelters)
        st.dataframe(
            df_shelters[[
                "zone_name", "shelter_name", "distance_km", "shelter_risk", "available_capacity", "status"
            ]],
            column_config={
                "distance_km": st.column_config.NumberColumn("Distance (km)", format="%.1f km"),
                "available_capacity": st.column_config.NumberColumn("Available Capacity", format="%d"),
            },
            use_container_width=True
        )


# ==========================================
# TAB 6: AI EMERGENCY ACTION PLAN
# ==========================================
with tabs[5]:
    st.subheader("Mission Incident Action Plan (IAP)")
    st.caption("Synthesized strictly from ML risk probabilities, GIS impact metrics, and safe evacuation corridors.")

    if st.button("🔄 Generate Fresh Incident Action Plan", type="primary"):
        with st.spinner("Compiling tactical action directives..."):
            plan_text, source_info = generate_emergency_action_plan(api_key=llm_api_key)
            st.session_state["cached_plan"] = plan_text
            st.session_state["cached_source"] = source_info

    # Display plan
    if "cached_plan" not in st.session_state:
        plan_text, source_info = generate_emergency_action_plan(api_key=llm_api_key)
        st.session_state["cached_plan"] = plan_text
        st.session_state["cached_source"] = source_info

    st.info(f"Generated via: **{st.session_state['cached_source']}**")
    st.markdown(st.session_state["cached_plan"])

    st.download_button(
        label="📥 Download Official Emergency Action Plan (.md)",
        data=st.session_state["cached_plan"],
        file_name="Emergency_Action_Plan_Incident_Command.md",
        mime="text/markdown"
    )
