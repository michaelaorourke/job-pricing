"""
Salary calculation engine
"""

from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from decimal import Decimal
import logging

from app.models.benchmark import Benchmark
from app.models.job_analysis import JobAnalysis

logger = logging.getLogger(__name__)

class SalaryEngine:
    """Calculate salary ranges based on market data and job analysis"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_salary(
        self,
        job: JobAnalysis,
        override_params: Optional[Dict] = None
    ) -> Dict:
        """Calculate salary range for a job"""

        # Use override parameters if provided
        if override_params:
            level = override_params.get("level", job.detected_level)
            zone = override_params.get("zone", job.zone)
            location = override_params.get("location", job.location)
        else:
            level = job.detected_level
            zone = job.zone
            location = job.location

        # Get market data
        market_data = self._get_market_benchmarks(
            job_family=job.job_family,
            level=level,
            zone=zone
        )

        if not market_data:
            # Fallback to estimation
            return self._estimate_salary(job, level, zone)

        # Calculate base salary from market data
        base_salary = self._calculate_base_from_market(market_data)

        # Apply adjustments
        geo_factor = self._get_geographic_factor(location, zone)
        market_adjustment = self._get_market_adjustment(job)
        skills_premium = self._calculate_skills_premium(job.skills_extracted)

        # Calculate final ranges
        adjusted_base = base_salary["p50"] * geo_factor * (1 + market_adjustment) * (1 + skills_premium)

        result = {
            "min": float(base_salary["p10"]),
            "p25": float(base_salary["p25"]),
            "target": float(adjusted_base),
            "p75": float(base_salary["p75"]),
            "max": float(base_salary["p90"]),
            "recommended_min": float(adjusted_base * 0.85),
            "recommended_target": float(adjusted_base),
            "recommended_max": float(adjusted_base * 1.15),
            "geographic_factor": geo_factor,
            "market_adjustment": market_adjustment,
            "skills_premium": skills_premium,
            "sources": market_data["sources"],
            "confidence": self._calculate_confidence(market_data),
            "justification": self._generate_justification(job, market_data, adjusted_base),
            "insights": {
                "market_position": self._get_market_position(adjusted_base, base_salary),
                "competitive_analysis": self._competitive_analysis(job, market_data),
                "retention_risk": self._assess_retention_risk(adjusted_base, market_data)
            }
        }

        return result

    def _get_market_benchmarks(
        self,
        job_family: str,
        level: int,
        zone: int
    ) -> Optional[Dict]:
        """Query market benchmark data"""

        benchmarks = self.db.query(Benchmark).filter(
            Benchmark.level == level,
            Benchmark.zone == zone
        )

        # Try exact job family match first
        if job_family:
            family_matches = benchmarks.filter(
                Benchmark.job_family == job_family
            ).all()

            if family_matches:
                return self._aggregate_benchmarks(family_matches)

        # Fallback to all matches at level/zone
        all_matches = benchmarks.limit(10).all()

        if all_matches:
            return self._aggregate_benchmarks(all_matches)

        return None

    def _aggregate_benchmarks(self, benchmarks: List[Benchmark]) -> Dict:
        """Aggregate multiple benchmark records"""

        sources = set()
        p10_values = []
        p25_values = []
        p50_values = []
        p75_values = []
        p90_values = []

        for benchmark in benchmarks:
            sources.add(benchmark.source_type)

            if benchmark.p10_salary:
                p10_values.append(float(benchmark.p10_salary))
            if benchmark.p25_salary:
                p25_values.append(float(benchmark.p25_salary))
            if benchmark.p50_salary:
                p50_values.append(float(benchmark.p50_salary))
            if benchmark.p75_salary:
                p75_values.append(float(benchmark.p75_salary))
            if benchmark.p90_salary:
                p90_values.append(float(benchmark.p90_salary))

        # Calculate averages
        return {
            "p10": sum(p10_values) / len(p10_values) if p10_values else 0,
            "p25": sum(p25_values) / len(p25_values) if p25_values else 0,
            "p50": sum(p50_values) / len(p50_values) if p50_values else 0,
            "p75": sum(p75_values) / len(p75_values) if p75_values else 0,
            "p90": sum(p90_values) / len(p90_values) if p90_values else 0,
            "sources": list(sources),
            "data_points": len(benchmarks)
        }

    def _calculate_base_from_market(self, market_data: Dict) -> Dict:
        """Calculate base salary from market data"""

        return {
            "p10": market_data["p10"],
            "p25": market_data["p25"],
            "p50": market_data["p50"],
            "p75": market_data["p75"],
            "p90": market_data["p90"]
        }

    def _get_geographic_factor(self, location: str, zone: int) -> float:
        """Get geographic cost adjustment factor"""

        # Location-specific adjustments
        location_factors = {
            "San Francisco": 1.4,
            "New York": 1.35,
            "Seattle": 1.25,
            "Boston": 1.25,
            "Los Angeles": 1.2,
            "Austin": 1.1,
            "Denver": 1.05,
            "Chicago": 1.05,
            "Remote": 1.0
        }

        # Check if location is in our factors
        for city, factor in location_factors.items():
            if location and city.lower() in location.lower():
                return factor

        # Default by zone
        return 1.2 if zone == 1 else 1.0

    def _get_market_adjustment(self, job: JobAnalysis) -> float:
        """Calculate market demand adjustment"""

        # High-demand indicators
        hot_skills = ["ai", "machine learning", "kubernetes", "rust", "golang"]
        high_demand_titles = ["staff", "principal", "architect", "director"]

        adjustment = 0.0

        # Check for hot skills
        if job.skills_extracted:
            for skill in job.skills_extracted:
                if any(hot in skill.lower() for hot in hot_skills):
                    adjustment += 0.05

        # Check for high-demand titles
        if job.job_title:
            if any(title in job.job_title.lower() for title in high_demand_titles):
                adjustment += 0.1

        return min(adjustment, 0.25)  # Cap at 25% premium

    def _calculate_skills_premium(self, skills: List[str]) -> float:
        """Calculate premium based on specialized skills"""

        if not skills:
            return 0.0

        premium_skills = {
            "kubernetes": 0.05,
            "aws": 0.03,
            "machine learning": 0.08,
            "ai": 0.08,
            "blockchain": 0.05,
            "security": 0.05,
            "golang": 0.04,
            "rust": 0.04
        }

        total_premium = 0.0
        for skill in skills:
            skill_lower = skill.lower()
            for premium_skill, value in premium_skills.items():
                if premium_skill in skill_lower:
                    total_premium += value

        return min(total_premium, 0.20)  # Cap at 20%

    def _calculate_confidence(self, market_data: Dict) -> float:
        """Calculate confidence score"""

        confidence = 0.5  # Base confidence

        # More data points = higher confidence
        if market_data.get("data_points", 0) > 5:
            confidence += 0.2
        elif market_data.get("data_points", 0) > 2:
            confidence += 0.1

        # Multiple sources = higher confidence
        if len(market_data.get("sources", [])) > 1:
            confidence += 0.15

        # Recent data = higher confidence
        confidence += 0.15  # Assuming data is recent

        return min(confidence, 0.95)

    def _estimate_salary(self, job: JobAnalysis, level: int, zone: int) -> Dict:
        """Estimate salary when no market data available"""

        # Base salary by level (zone 1)
        base_by_level = {
            1: 70000,
            2: 90000,
            3: 110000,
            4: 130000,
            5: 160000,
            6: 190000,
            7: 230000,
            8: 280000,
            9: 350000,
            10: 450000
        }

        base = base_by_level.get(level, 120000)

        # Adjust for zone
        if zone == 2:
            base *= 0.85

        # Adjust for tech vs non-tech
        if job.detected_band == 1:  # Tech
            base *= 1.15

        return {
            "min": float(base * 0.8),
            "p25": float(base * 0.9),
            "target": float(base),
            "p75": float(base * 1.15),
            "max": float(base * 1.3),
            "recommended_min": float(base * 0.9),
            "recommended_target": float(base),
            "recommended_max": float(base * 1.15),
            "geographic_factor": 1.0,
            "market_adjustment": 0.0,
            "skills_premium": 0.0,
            "sources": ["estimated"],
            "confidence": 0.3,
            "justification": "Estimated based on level and location due to limited market data",
            "insights": {}
        }

    def _generate_justification(self, job: JobAnalysis, market_data: Dict, salary: float) -> str:
        """Generate AI-like justification for salary recommendation"""

        justification = f"Based on market analysis for {job.job_title} "
        justification += f"(Level {job.detected_level}) in {job.location or 'this location'}, "
        justification += f"the recommended salary of ${salary:,.0f} reflects "

        factors = []
        if market_data.get("sources"):
            factors.append(f"data from {', '.join(market_data['sources'])}")

        if job.years_experience_min:
            factors.append(f"{job.years_experience_min}-{job.years_experience_max} years experience requirement")

        if job.skills_extracted and len(job.skills_extracted) > 3:
            factors.append(f"specialized skills in {', '.join(job.skills_extracted[:3])}")

        justification += ", ".join(factors)
        justification += f". This positions the role competitively in the current market."

        return justification

    def _get_market_position(self, salary: float, base_data: Dict) -> str:
        """Determine market positioning"""

        if salary <= base_data["p25"]:
            return "Below market (conservative)"
        elif salary <= base_data["p50"]:
            return "At market median (competitive)"
        elif salary <= base_data["p75"]:
            return "Above market (aggressive)"
        else:
            return "Top of market (premium)"

    def _competitive_analysis(self, job: JobAnalysis, market_data: Dict) -> Dict:
        """Analyze competitive positioning"""

        return {
            "market_demand": "High" if job.detected_level >= 5 else "Moderate",
            "talent_availability": "Limited" if job.detected_level >= 6 else "Good",
            "competing_companies": market_data.get("data_points", 0),
            "recommendation": "Offer at or above P50 to be competitive"
        }

    def _assess_retention_risk(self, salary: float, market_data: Dict) -> str:
        """Assess retention risk based on salary"""

        p50 = market_data.get("p50", salary)

        if salary < p50 * 0.9:
            return "High - significantly below market"
        elif salary < p50:
            return "Medium - slightly below market"
        elif salary < p50 * 1.1:
            return "Low - at market rate"
        else:
            return "Very low - above market"