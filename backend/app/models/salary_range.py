"""
Salary Range model
"""

from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, DECIMAL, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base

class SalaryRange(Base):
    __tablename__ = "salary_ranges"
    __table_args__ = {"schema": "compensation"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_analysis_id = Column(UUID(as_uuid=True), ForeignKey('compensation.job_analyses.id'))
    job_title = Column(String(255), nullable=False)
    job_family = Column(String(100))
    level = Column(Integer)
    band = Column(Integer)
    zone = Column(Integer)
    location = Column(String(255))

    # Experience requirements
    years_experience_min = Column(Integer)
    years_experience_max = Column(Integer)

    # Base salary ranges
    base_salary_min = Column(DECIMAL(12, 2))
    base_salary_p25 = Column(DECIMAL(12, 2))
    base_salary_p50 = Column(DECIMAL(12, 2))
    base_salary_p75 = Column(DECIMAL(12, 2))
    base_salary_max = Column(DECIMAL(12, 2))

    # Total compensation
    total_comp_min = Column(DECIMAL(12, 2))
    total_comp_target = Column(DECIMAL(12, 2))
    total_comp_max = Column(DECIMAL(12, 2))

    # Adjustments
    geographic_factor = Column(DECIMAL(5, 3), default=1.0)
    market_adjustment = Column(DECIMAL(5, 3), default=1.0)
    skills_premium = Column(DECIMAL(5, 3), default=0.0)

    # Final recommendations
    recommended_min = Column(DECIMAL(12, 2))
    recommended_target = Column(DECIMAL(12, 2))
    recommended_max = Column(DECIMAL(12, 2))

    # Data sources used
    data_sources = Column(JSON)
    confidence_score = Column(DECIMAL(3, 2))

    # AI Analysis
    openai_analysis = Column(JSON)
    ai_justification = Column(Text)
    market_insights = Column(JSON)

    # Metadata
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(String(255))

    # Relationships
    job_analysis = relationship("JobAnalysis", backref="salary_ranges")