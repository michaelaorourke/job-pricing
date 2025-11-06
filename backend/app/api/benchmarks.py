"""
Benchmark data API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
import uuid

from app.models.database import get_db
from app.models.job_analysis import JobAnalysis
from app.models.salary_range import SalaryRange
from app.models.benchmark import Benchmark

router = APIRouter()

@router.get("/details/{job_id}")
async def get_benchmark_details(job_id: str, db: Session = Depends(get_db)):
    """Get detailed benchmark data used for salary calculation"""

    # Get job analysis
    job_analysis = db.query(JobAnalysis).filter(JobAnalysis.id == uuid.UUID(job_id)).first()
    if not job_analysis:
        raise HTTPException(status_code=404, detail="Job analysis not found")

    # Get salary range calculation
    salary_range = db.query(SalaryRange).filter(
        SalaryRange.job_analysis_id == uuid.UUID(job_id)
    ).order_by(SalaryRange.created_at.desc()).first()

    # Get benchmark data used (matching level and zone)
    mercer_benchmarks = db.query(Benchmark).filter(
        Benchmark.source_type == 'mercer',
        Benchmark.level == job_analysis.detected_level,
        Benchmark.zone == job_analysis.zone
    ).all()

    lattice_benchmarks = db.query(Benchmark).filter(
        Benchmark.source_type == 'lattice',
        Benchmark.level == job_analysis.detected_level,
        Benchmark.zone == job_analysis.zone
    ).all()

    # Calculate averages for each source
    mercer_stats = calculate_benchmark_stats(mercer_benchmarks)
    lattice_stats = calculate_benchmark_stats(lattice_benchmarks)

    # Prepare response
    return {
        "job_analysis": {
            "id": str(job_analysis.id),
            "position": job_analysis.job_title,
            "level": job_analysis.detected_level,
            "level_name": get_level_name(job_analysis.detected_level),
            "zone": job_analysis.zone,
            "zone_name": get_zone_name(job_analysis.zone),
            "location": job_analysis.location,
            "experience_range": f"{job_analysis.years_experience_min or 0}-{job_analysis.years_experience_max or 0} years",
            "skills": job_analysis.skills_extracted or []
        },
        "benchmark_data": {
            "mercer": {
                "count": len(mercer_benchmarks),
                "p50_range": {
                    "min": mercer_stats['min_p50'],
                    "max": mercer_stats['max_p50'],
                    "avg": mercer_stats['avg_p50']
                },
                "p25_avg": mercer_stats['avg_p25'],
                "p75_avg": mercer_stats['avg_p75'],
                "data_points": [
                    {
                        "job_title": b.job_title or "Software Engineer",
                        "location": b.location,
                        "p25": float(b.p25_salary) if b.p25_salary else None,
                        "p50": float(b.p50_salary) if b.p50_salary else None,
                        "p75": float(b.p75_salary) if b.p75_salary else None,
                        "data_date": b.data_date.isoformat() if b.data_date else None
                    } for b in mercer_benchmarks[:5]  # Top 5 matches
                ]
            },
            "lattice": {
                "count": len(lattice_benchmarks),
                "p50_range": {
                    "min": lattice_stats['min_p50'],
                    "max": lattice_stats['max_p50'],
                    "avg": lattice_stats['avg_p50']
                },
                "p25_avg": lattice_stats['avg_p25'],
                "p75_avg": lattice_stats['avg_p75'],
                "data_points": [
                    {
                        "job_title": b.job_title or "Software Engineer",
                        "location": b.location,
                        "p25": float(b.p25_salary) if b.p25_salary else None,
                        "p50": float(b.p50_salary) if b.p50_salary else None,
                        "p75": float(b.p75_salary) if b.p75_salary else None,
                        "data_date": b.data_date.isoformat() if b.data_date else None
                    } for b in lattice_benchmarks[:5]  # Top 5 matches
                ]
            }
        },
        "calculation_breakdown": {
            "base_p50": {
                "mercer_avg": mercer_stats['avg_p50'],
                "lattice_avg": lattice_stats['avg_p50'],
                "combined_avg": (mercer_stats['avg_p50'] + lattice_stats['avg_p50']) / 2 if mercer_stats['avg_p50'] and lattice_stats['avg_p50'] else 0
            },
            "adjustments": {
                "geographic_factor": float(salary_range.geographic_factor) if salary_range else 1.0,
                "geographic_adjustment": get_geographic_description(job_analysis.location),
                "skills_premium": float(salary_range.skills_premium) if salary_range else 0.0,
                "market_adjustment": float(salary_range.market_adjustment) if salary_range else 0.0
            },
            "final_calculation": {
                "base": (mercer_stats['avg_p50'] + lattice_stats['avg_p50']) / 2 if mercer_stats['avg_p50'] and lattice_stats['avg_p50'] else 0,
                "after_geographic": None,  # Will calculate
                "after_skills": None,  # Will calculate
                "final_target": float(salary_range.recommended_target) if salary_range else 0
            }
        },
        "salary_range": {
            "minimum": float(salary_range.recommended_min) if salary_range else 0,
            "target": float(salary_range.recommended_target) if salary_range else 0,
            "maximum": float(salary_range.recommended_max) if salary_range else 0,
            "confidence_score": float(salary_range.confidence_score) if salary_range else 0
        }
    }

def calculate_benchmark_stats(benchmarks: List[Benchmark]) -> Dict:
    """Calculate statistics from benchmark data"""
    if not benchmarks:
        return {
            'avg_p25': 0, 'avg_p50': 0, 'avg_p75': 0,
            'min_p50': 0, 'max_p50': 0
        }

    p25_values = [float(b.p25_salary) for b in benchmarks if b.p25_salary]
    p50_values = [float(b.p50_salary) for b in benchmarks if b.p50_salary]
    p75_values = [float(b.p75_salary) for b in benchmarks if b.p75_salary]

    return {
        'avg_p25': sum(p25_values) / len(p25_values) if p25_values else 0,
        'avg_p50': sum(p50_values) / len(p50_values) if p50_values else 0,
        'avg_p75': sum(p75_values) / len(p75_values) if p75_values else 0,
        'min_p50': min(p50_values) if p50_values else 0,
        'max_p50': max(p50_values) if p50_values else 0
    }

def get_level_name(level: int) -> str:
    """Convert level number to name"""
    levels = {
        1: "Entry Level", 2: "Junior", 3: "Mid-Level",
        4: "Experienced", 5: "Senior", 6: "Lead",
        7: "Staff/Principal", 8: "Director", 9: "VP", 10: "C-Level"
    }
    return levels.get(level, f"Level {level}")

def get_zone_name(zone: int) -> str:
    """Convert zone number to name"""
    zones = {
        1: "Primary Market (SF/NYC/Seattle)",
        2: "Secondary Market",
        3: "Tertiary Market"
    }
    return zones.get(zone, f"Zone {zone}")

def get_geographic_description(location: str) -> str:
    """Get geographic adjustment description"""
    if any(city in location.lower() for city in ['san francisco', 'new york', 'seattle']):
        return "40% premium for primary tech market"
    elif any(city in location.lower() for city in ['austin', 'denver', 'portland']):
        return "20% premium for secondary tech market"
    else:
        return "Base market rate"