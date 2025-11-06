"""
Benchmark model for market salary data
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, DECIMAL, Date
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
import uuid

from .database import Base

class Benchmark(Base):
    __tablename__ = "benchmarks"
    __table_args__ = {"schema": "compensation"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    source_type = Column(String(50), nullable=False)  # 'mercer', 'lattice', 'glassdoor'
    source_file = Column(String(255))
    job_family = Column(String(100))
    job_code = Column(String(50))
    job_title = Column(String(255))
    level = Column(Integer)
    band = Column(Integer)
    zone = Column(Integer)
    geography = Column(String(255))
    location = Column(String(255))
    market_segment = Column(String(100))
    industry = Column(String(100))
    company_count = Column(Integer)
    employee_count = Column(Integer)

    # Compensation percentiles
    p10_salary = Column(DECIMAL(12, 2))
    p25_salary = Column(DECIMAL(12, 2))
    p50_salary = Column(DECIMAL(12, 2))
    p75_salary = Column(DECIMAL(12, 2))
    p90_salary = Column(DECIMAL(12, 2))
    mean_salary = Column(DECIMAL(12, 2))

    # Market indicators
    trend_indicator = Column(String(50))
    trend_velocity = Column(String(20))

    # Metadata
    data_date = Column(Date)
    currency = Column(String(10), default='USD')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))