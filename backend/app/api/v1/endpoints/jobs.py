import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.job import Job
from app.db.session import get_db
from app.schemas.job import JobResponse

router = APIRouter()

@router.get("/", response_model=List[JobResponse])
def read_jobs(
    db: Session = Depends(get_db),
    skill: Optional[str] = Query(None)
):
    query = db.query(Job)
    if skill:
        query = query.filter(Job.skills_extracted.contains(skill))
    
    db_jobs = query.all()
    
    # Convert JSON string from Azure SQL back to List for Pydantic
    for job in db_jobs:
        if isinstance(job.skills_extracted, str):
            job.skills_extracted = json.loads(job.skills_extracted)
            
    return db_jobs