"""
Salary-related Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class SalaryCalculationRequest(BaseModel):
    """Request for salary calculation"""
    level: Optional[int] = None
    zone: Optional[int] = None
    location: Optional[str] = None
    skills_override: Optional[List[str]] = None
    years_experience: Optional[int] = None

class SalaryCalculationResponse(BaseModel):
    """Response for salary calculation"""
    id: Optional[UUID] = None
    job_analysis_id: Optional[UUID] = None
    job_title: str
    job_family: Optional[str] = None
    level: Optional[int] = None
    band: Optional[int] = None
    zone: Optional[int] = None
    location: Optional[str] = None

    # Salary ranges
    base_salary_min: Optional[Decimal] = None
    base_salary_p25: Optional[Decimal] = None
    base_salary_p50: Optional[Decimal] = None
    base_salary_p75: Optional[Decimal] = None
    base_salary_max: Optional[Decimal] = None

    # Recommendations
    recommended_min: Optional[Decimal] = None
    recommended_target: Optional[Decimal] = None
    recommended_max: Optional[Decimal] = None

    # Adjustments
    geographic_factor: Optional[Decimal] = Field(default=Decimal("1.0"))
    market_adjustment: Optional[Decimal] = Field(default=Decimal("1.0"))
    skills_premium: Optional[Decimal] = Field(default=Decimal("0.0"))

    # Metadata
    data_sources: Optional[List[str]] = []
    confidence_score: Optional[Decimal] = None
    ai_justification: Optional[str] = None
    market_insights: Optional[Dict] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MarketDataResponse(BaseModel):
    """Market benchmark data response"""
    source_type: str
    job_family: Optional[str] = None
    level: Optional[int] = None
    zone: Optional[int] = None
    location: Optional[str] = None

    p10_salary: Optional[Decimal] = None
    p25_salary: Optional[Decimal] = None
    p50_salary: Optional[Decimal] = None
    p75_salary: Optional[Decimal] = None
    p90_salary: Optional[Decimal] = None
    mean_salary: Optional[Decimal] = None

    trend_indicator: Optional[str] = None
    data_date: Optional[datetime] = None

    class Config:
        from_attributes = True