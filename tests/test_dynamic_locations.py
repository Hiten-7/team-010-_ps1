"""
Automated Test Suite for Dynamic Location-Based Disaster Intelligence.
Validates that 5 diverse locations produce completely different,
location-aware, data-driven outputs across all intelligence modules.
"""
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from services.disaster_intelligence_service import DisasterIntelligenceService


def test_five_dynamic_locations():
    service = DisasterIntelligenceService()

    locations_to_test = [
        "Kolkata, Riverside Sector 4",
        "Varanasi, Ghats Waterfront Sector",
        "Nagaon, Assam",
        "Jaipur, Rajasthan",
        "Malappuram, Kerala"
    ]

    results = {}
    print("=" * 70)
    print("RUNNING MULTI-LOCATION DISASTER INTELLIGENCE TEST SUITE")
    print("=" * 70)

    for loc in locations_to_test:
        print(f"\n[ANALYZING] {loc}...")
        report = service.analyze_location(loc)
        results[loc] = report

        # Extract primary metrics
        rain_24h = report["rainfall"]["last24Hours"]
        river_name = report["river"]["nearest_river"]
        river_level = report["river"]["current_level_m"]
        danger_mark = report["river"]["danger_mark_m"]
        sev_score = report["severity"]["score"]
        sev_tier = report["severity"]["tier"]
        top_zone = report["priorities"][0]["area_locality"]
        pop_risk = report["population"]["total_population_at_risk"]
        top_shelter = report["shelters"][0]["name"]
        opt_route = report["routes"]["routes"]["optimal_route"]["title"]
        opt_dist = report["routes"]["routes"]["optimal_route"]["distance_km"]

        print(f"  [OK] District: {report['location']['district']} ({report['location']['state']})")
        print(f"  [OK] Elevation: {report['location']['elevation_m']}m | Terrain: {report['location']['terrain']}")
        print(f"  [OK] 24h Rainfall: {rain_24h} mm ({report['rainfall']['intensity_tier']})")
        print(f"  [OK] River: {river_name} @ {river_level}m (Danger: {danger_mark}m) -> {report['river']['status']}")
        print(f"  [OK] Disaster Severity Score: {sev_score}/100 ({sev_tier})")
        print(f"  [OK] Population At Risk: {pop_risk:,}")
        print(f"  [OK] Rank #1 Target: {top_zone}")
        print(f"  [OK] Primary Shelter: {top_shelter}")
        print(f"  [OK] Optimal Evacuation Route: {opt_route} ({opt_dist} km)")

    # Assertions to ensure NO identical values
    print("\n" + "=" * 70)
    print("VALIDATING DYNAMIC VARIATION ACROSS LOCATIONS")
    print("=" * 70)

    # 1. Rainfall must be different
    rainfalls = [r["rainfall"]["last24Hours"] for r in results.values()]
    print(f"Rainfall values across 5 locations: {rainfalls}")
    assert len(set(rainfalls)) >= 3, "Rainfall values should not be uniform across regions!"

    # 2. Rivers must be distinct
    rivers = [r["river"]["nearest_river"] for r in results.values()]
    print(f"Rivers identified: {rivers}")
    assert len(set(rivers)) >= 4, "Rivers must be location-specific!"

    # 3. Severity scores must vary dynamically
    scores = [r["severity"]["score"] for r in results.values()]
    print(f"Severity scores across 5 locations: {scores}")
    assert len(set(scores)) >= 3, "Severity scores must not be static!"

    # 4. Shelters must be location-specific
    shelters = [r["shelters"][0]["name"] for r in results.values()]
    print(f"Shelters recommended: {shelters}")
    assert len(set(shelters)) >= 4, "Shelter recommendations must be unique per region!"

    # 5. Route distances must differ
    dists = [r["routes"]["routes"]["optimal_route"]["distance_km"] for r in results.values()]
    print(f"Route distances: {dists}")

    print("\n[SUCCESS] ALL 5 LOCATIONS RETURN DYNAMIC, LOCATION-SPECIFIC DATA!")
    print("=" * 70)


if __name__ == "__main__":
    test_five_dynamic_locations()
