"""
Population Demographics Service for Disaster Intelligence Platform.
Dynamically computes total population inside risk zones, affected population,
demographic splits (children, elderly, vulnerable groups), and evacuation requirements.
"""
from typing import Dict, Any, List


class PopulationService:
    """Computes dynamic demographic impact based on location-specific census baselines."""

    @staticmethod
    def calculate_population_impact(
        location: Dict[str, Any],
        risk_zones: List[Dict[str, Any]],
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Baseline total population scaling by district/city
        district = location.get("district", "KOLKATA").upper()
        if "KOLKATA" in district:
            base_city_pop = 185000  # Assessed sector cluster
        elif "VARANASI" in district:
            base_city_pop = 145000
        elif "NAGAON" in district:
            base_city_pop = 95000
        elif "DHUBRI" in district:
            base_city_pop = 82000
        elif "PATNA" in district:
            base_city_pop = 160000
        elif "JAIPUR" in district:
            base_city_pop = 120000
        elif "MALAPPURAM" in district:
            base_city_pop = 110000
        else:
            base_city_pop = historical_data.get("historical_affected_population", 50000) * 2

        zone_impacts = []
        total_affected = 0
        total_evac_req = 0

        for z in risk_zones:
            weight = z.get("pop_weight", 0.2)
            zone_total_pop = int(base_city_pop * weight)
            prob = z.get("risk_probability", 0.5)

            # Equation: affectedPopulation = populationInsideRiskZones * riskProbability
            affected_pop = int(zone_total_pop * (prob ** 1.1))
            evac_req = int(affected_pop * min(prob * 1.15, 0.85))

            child_count = int(affected_pop * 0.22)
            elderly_count = int(affected_pop * 0.16)
            vuln_count = child_count + elderly_count

            total_affected += affected_pop
            total_evac_req += evac_req

            zone_impacts.append({
                "zone_id": z.get("zone_id"),
                "zone_name": z.get("zone_name"),
                "total_population": zone_total_pop,
                "affected_population": affected_pop,
                "children": child_count,
                "elderly": elderly_count,
                "vulnerable_population": vuln_count,
                "evacuation_required": evac_req,
                "risk_score": z.get("risk_score")
            })

        total_children = int(total_affected * 0.22)
        total_elderly = int(total_affected * 0.16)

        return {
            "total_population_at_risk": total_affected,
            "total_assessed_population": base_city_pop,
            "children_at_risk": total_children,
            "elderly_at_risk": total_elderly,
            "vulnerable_population": total_children + total_elderly,
            "evacuation_required": total_evac_req,
            "zone_breakdowns": zone_impacts,
            "source": "🟣 ESTIMATED CENSUS & SPATIAL VULNERABILITY MODEL"
        }
