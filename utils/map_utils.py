"""
Map utilities for disaster visualization using Folium.
Renders risk zones, hospitals, schools, relief shelters, and evacuation routes.
"""
import sys
from pathlib import Path
from typing import Optional

# Allow absolute imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import DEFAULT_MAP_CENTER, DEFAULT_ZOOM, RISK_COLORS

try:
    import folium
    from folium import plugins
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False


def create_disaster_command_map(
    zones: list = None,
    shelters: list = None,
    routes: dict = None,
    center: list = None,
    zoom: int = DEFAULT_ZOOM
) -> Optional["folium.Map"]:
    """
    Generate an emergency management Folium map with layers for:
    - Heat / Risk Circles around affected zones
    - Critical Infrastructure markers (Hospitals, Schools)
    - Safe Shelter markers
    - Route polylines (Fast vs. Safe vs. Recommended)
    """
    if not HAS_FOLIUM:
        return None

    map_center = center or DEFAULT_MAP_CENTER
    m = folium.Map(
        location=map_center,
        zoom_start=zoom,
        tiles="OpenStreetMap"
    )

    # 1. Plot Disaster Risk Zones
    if zones:
        for z in zones:
            lat = z.get("latitude")
            lon = z.get("longitude")
            if lat is None or lon is None:
                continue

            score = z.get("risk_score", 50.0)
            level = z.get("risk_level", "MODERATE")
            color = RISK_COLORS.get(level, "#F39C12")

            # Risk Zone Boundary Circle
            folium.Circle(
                location=[lat, lon],
                radius=1500 + (score * 15),  # Radius in meters based on risk score
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.35,
                tooltip=f"<b>{z.get('zone_name', 'Zone')}</b><br>Risk: {score:.1f} ({level})<br>Pop: {z.get('population', 'N/A'):,}"
            ).add_to(m)

            # Zone Center Marker
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="red" if score > 70 else "orange", icon="exclamation-triangle", prefix="fa"),
                popup=folium.Popup(f"""
                <div style="width:200px">
                    <h4>{z.get('zone_name', 'Sector')}</h4>
                    <b>Risk Score:</b> {score:.1f} / 100 ({level})<br>
                    <b>Affected Population:</b> {z.get('population', 0):,}<br>
                    <b>At-Risk Hospitals:</b> {z.get('hospitals', 0)}<br>
                    <b>At-Risk Schools:</b> {z.get('schools', 0)}<br>
                    <b>Bridges Affected:</b> {z.get('bridges', 0)}
                </div>
                """, max_width=250)
            ).add_to(m)

    # 2. Plot Designated Safe Shelters
    if shelters:
        for s in shelters:
            s_lat = s.get("shelter_latitude", s.get("latitude"))
            s_lon = s.get("shelter_longitude", s.get("longitude"))
            if s_lat is None or s_lon is None:
                continue

            folium.Marker(
                location=[s_lat, s_lon],
                icon=folium.Icon(color="green", icon="shield", prefix="fa"),
                tooltip=f"<b>SAFE SHELTER:</b> {s.get('shelter_name', s.get('name', 'Relief Hub'))}",
                popup=folium.Popup(f"""
                <div style="width:220px">
                    <h4 style="color:#27ae60;">{s.get('shelter_name', s.get('name', 'Relief Hub'))}</h4>
                    <b>Status:</b> {s.get('status', 'ACTIVE')}<br>
                    <b>Available Capacity:</b> {s.get('available_capacity', s.get('capacity', 'N/A'))} persons<br>
                    <b>Shelter Flood Risk:</b> {s.get('shelter_risk', 'LOW')}<br>
                    <b>Distance:</b> {s.get('distance_km', 'N/A')} km
                </div>
                """, max_width=250)
            ).add_to(m)

    # 3. Plot Evacuation Routes
    if routes and "routes" in routes:
        route_dict = routes["routes"]

        # Route A: Fast Route (Red dashed)
        if "fast_route" in route_dict:
            fr = route_dict["fast_route"]
            folium.PolyLine(
                locations=fr["coordinates"],
                color="#E74C3C",
                weight=4,
                dash_array="8, 8",
                tooltip=f"Route A (Fastest: {fr.get('distance_km')} km, {fr.get('travel_time_min')} min) - HIGH FLOOD RISK"
            ).add_to(m)

        # Route B: Safe Route (Blue line)
        if "safe_route" in route_dict:
            sr = route_dict["safe_route"]
            folium.PolyLine(
                locations=sr["coordinates"],
                color="#3498DB",
                weight=4,
                tooltip=f"Route B (Highland Safe: {sr.get('distance_km')} km, {sr.get('travel_time_min')} min) - LOW FLOOD RISK"
            ).add_to(m)

        # Route C: Optimal Risk-Aware Route (Bright Emerald Green, Bold)
        if "optimal_route" in route_dict:
            opt = route_dict["optimal_route"]
            folium.PolyLine(
                locations=opt["coordinates"],
                color="#2ECC71",
                weight=6,
                tooltip=f"Route C (RECOMMENDED PRIMARY: {opt.get('distance_km')} km, {opt.get('travel_time_min')} min) - LOW FLOOD RISK"
            ).add_to(m)

    # Add Fullscreen toggle and LayerControl
    plugins.Fullscreen().add_to(m)
    folium.LayerControl().add_to(m)

    return m
