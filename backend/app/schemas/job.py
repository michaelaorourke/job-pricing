"""
Job-related Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

class JobAnalysisBase(BaseModel):
    """Base job analysis schema"""
    job_title: str
    original_filename: Optional[str] = None
    detected_level: Optional[int] = None
    detected_band: Optional[int] = None
    zone: Optional[int] = None
    location: Optional[str] = None
    remote_type: Optional[str] = "onsite"
    years_experience_min: Optional[int] = None
    years_experience_max: Optional[int] = None
    job_family: Optional[str] = None
    department: Optional[str] = None
    confidence_score: Optional[float] = None

class JobAnalysisCreate(JobAnalysisBase):
    """Schema for creating job analysis"""
    raw_description: str
    parsed_data: Dict
    skills_extracted: Optional[List[str]] = []

class JobAnalysisResponse(JobAnalysisBase):
    """Schema for job analysis response"""
    id: UUID
    parsed_data: Dict
    openai_analysis: Optional[Dict] = None
    skills_extracted: Optional[List[str]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobAnalysisUpdate(BaseModel):
    """Schema for updating job analysis"""
    job_title: Optional[str] = None
    detected_level: Optional[int] = None
    detected_band: Optional[int] = None
    zone: Optional[int] = None
    location: Optional[str] = None
    confidence_score: Optional[float] = None