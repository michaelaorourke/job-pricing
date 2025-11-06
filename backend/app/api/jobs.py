"""
Job-related API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.models.database import get_db
from app.models.job_analysis import JobAnalysis
from app.schemas.job import JobAnalysisCreate, JobAnalysisResponse
from app.services.document_processor import DocumentProcessor
from app.services.openai_service import OpenAIService

router = APIRouter()

@router.post("/upload", response_model=JobAnalysisResponse)
async def upload_job_description(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and analyze a job description"""

    # Process document
    doc_processor = DocumentProcessor()
    text = await doc_processor.extract_text(file)

    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from document")

    # Analyze with OpenAI
    openai_service = OpenAIService()
    analysis = await openai_service.analyze_job_description(text)

    # Create job analysis record
    job_analysis = JobAnalysis(
        job_title=analysis.get("title", "Unknown"),
        original_filename=file.filename,
        raw_description=text,
        parsed_data=analysis,
        openai_analysis=analysis,
        detected_level=analysis.get("level"),
        detected_band=analysis.get("band", 1),
        zone=analysis.get("zone", 1),
        location=analysis.get("location"),
        remote_type=analysis.get("remote_type", "onsite"),
        years_experience_min=analysis.get("years_exp_min"),
        years_experience_max=analysis.get("years_exp_max"),
        skills_extracted=analysis.get("skills", []),
        job_family=analysis.get("department"),
        confidence_score=analysis.get("confidence", 0.85)
    )

    db.add(job_analysis)
    db.commit()
    db.refresh(job_analysis)

    return job_analysis

@router.get("/{job_id}", response_model=JobAnalysisResponse)
async def get_job_analysis(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get job analysis by ID"""
    job = db.query(JobAnalysis).filter(JobAnalysis.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job analysis not found")

    return job

@router.get("/", response_model=List[JobAnalysisResponse])
async def list_job_analyses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all job analyses"""
    jobs = db.query(JobAnalysis)\
        .order_by(JobAnalysis.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    return jobs