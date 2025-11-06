"""
Job Analysis model
"""

from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .database import Base

class JobAnalysis(Base):
    __tablename__ = "job_analyses"
    __table_args__ = {"schema": "compensation"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Job information
    job_title = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    raw_description = Column(Text)

    # Parsed data
    parsed_data = Column(JSON, nullable=False)
    openai_analysis = Column(JSON)
    embedding = Column(Text)  # Will be vector(1536) with pgvector

    # Classification
    detected_level = Column(Integer)
    detected_band = Column(Integer)
    zone = Column(Integer)
    location = Column(String(255))
    remote_type = Column(String(50))  # 'onsite', 'hybrid', 'remote'

    # Requirements
    years_experience_min = Column(Integer)
    years_experience_max = Column(Integer)
    skills_extracted = Column(JSON)
    education_requirements = Column(JSON)
    certifications = Column(JSON)

    # Organization
    job_family = Column(String(100))
    department = Column(String(100))
    reports_to = Column(String(255))
    team_size = Column(Integer)

    # Analysis metadata
    confidence_score = Column(Float)
    analysis_version = Column(String(20))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    analyzed_at = Column(DateTime(timezone=True))