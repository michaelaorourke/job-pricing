"""
Conversation model for chat history
"""

from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = {"schema": "compensation"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(String(255))
    job_analysis_id = Column(UUID(as_uuid=True), ForeignKey('compensation.job_analyses.id'))

    # Conversation data
    messages = Column(JSON, default=list)
    openai_thread_id = Column(String(255))

    # Usage tracking
    total_tokens_used = Column(Integer, default=0)
    total_cost_usd = Column(DECIMAL(10, 6), default=0)

    # Context
    context = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True))

    # Relationships
    job_analysis = relationship("JobAnalysis", backref="conversations")