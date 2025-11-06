"""
Salary analysis API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.models.database import get_db
from app.models.job_analysis import JobAnalysis
from app.models.salary_range import SalaryRange
from app.schemas.salary import SalaryCalculationRequest, SalaryCalculationResponse
from app.services.salary_engine import SalaryEngine

router = APIRouter()

@router.post("/calculate/{job_id}", response_model=SalaryCalculationResponse)
async def calculate_salary(
    job_id: str,
    request: Optional[SalaryCalculationRequest] = None,
    db: Session = Depends(get_db)
):
    """Calculate salary range for a job"""

    # Get job analysis
    job = db.query(JobAnalysis).filter(JobAnalysis.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job analysis not found")

    # Calculate salary
    salary_engine = SalaryEngine(db)
    salary_data = salary_engine.calculate_salary(job, request)

    # Save salary range
    salary_range = SalaryRange(
        job_analysis_id=job.id,
        job_title=job.job_title,
        job_family=job.job_family,
        level=job.detected_level,
        band=job.detected_band,
        zone=job.zone,
        location=job.location,
        years_experience_min=job.years_experience_min,
        years_experience_max=job.years_experience_max,
        base_salary_min=salary_data["min"],
        base_salary_p25=salary_data["p25"],
        base_salary_p50=salary_data["target"],
        base_salary_p75=salary_data["p75"],
        base_salary_max=salary_data["max"],
        recommended_min=salary_data["recommended_min"],
        recommended_target=salary_data["recommended_target"],
        recommended_max=salary_data["recommended_max"],
        geographic_factor=salary_data.get("geographic_factor", 1.0),
        market_adjustment=salary_data.get("market_adjustment", 1.0),
        data_sources=salary_data.get("sources", []),
        confidence_score=salary_data.get("confidence", 0.85),
        ai_justification=salary_data.get("justification"),
        market_insights=salary_data.get("insights", {})
    )

    db.add(salary_range)
    db.commit()
    db.refresh(salary_range)

    return salary_range

@router.get("/salary/{job_id}", response_model=SalaryCalculationResponse)
async def get_salary_calculation(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get latest salary calculation for a job"""

    salary_range = db.query(SalaryRange)\
        .filter(SalaryRange.job_analysis_id == job_id)\
        .order_by(SalaryRange.created_at.desc())\
        .first()

    if not salary_range:
        raise HTTPException(status_code=404, detail="Salary calculation not found")

    return salary_range

@router.get("/market-data")
async def get_market_data(
    job_family: Optional[str] = None,
    level: Optional[int] = None,
    zone: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get market benchmark data"""

    from app.models.benchmark import Benchmark

    query = db.query(Benchmark)

    if job_family:
        query = query.filter(Benchmark.job_family == job_family)
    if level:
        query = query.filter(Benchmark.level == level)
    if zone:
        query = query.filter(Benchmark.zone == zone)

    benchmarks = query.limit(50).all()

    return benchmarks