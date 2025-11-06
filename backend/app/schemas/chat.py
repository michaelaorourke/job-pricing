"""
Chat-related Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

class ChatMessage(BaseModel):
    """Chat message schema"""
    content: str
    role: Optional[str] = "user"

class ChatResponse(BaseModel):
    """Chat response schema"""
    response: str
    tokens_used: Optional[int] = None

class ChatSession(BaseModel):
    """Chat session schema"""
    session_id: str
    job_id: str
    created_at: Optional[datetime] = None

class ConversationHistory(BaseModel):
    """Conversation history schema"""
    session_id: str
    messages: List[Dict]
    context: Dict
    created_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True