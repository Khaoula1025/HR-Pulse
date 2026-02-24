from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.job import Job
from app.schemas.job import JobResponse

router = APIRouter()


@router.get("/", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


@router.get("/search", response_model=List[JobResponse])
def search_by_skill(
    skill: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if skill:
        return db.query(Job).filter(
            Job.skills_extracted.contains(skill)
        ).all()
    return db.query(Job).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.id == job_id).first()
