"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import redis

from app.models.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@router.get("/health/live")
async def liveness():
    """Liveness probe for Kubernetes"""
    return {"status": "alive"}

@router.get("/health/ready")
async def readiness(db: Session = Depends(get_db)):
    """Readiness probe - checks database and Redis"""
    status = {"status": "ready", "checks": {}}

    # Check database
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        status["checks"]["database"] = "ok"
    except Exception as e:
        status["status"] = "not ready"
        status["checks"]["database"] = f"error: {str(e)}"

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        status["checks"]["redis"] = "ok"
    except Exception as e:
        status["status"] = "not ready"
        status["checks"]["redis"] = f"error: {str(e)}"

    return status