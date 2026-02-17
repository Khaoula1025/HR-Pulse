from pydantic import BaseModel
from typing import Optional, List


class JobBase(BaseModel):
    job_title: str
    skills_extracted: Optional[List[str]] = []


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: int

    class Config:
        from_attributes = True


class SalaryPredictRequest(BaseModel):
    job_title: str
    skills: List[str]


class SalaryPredictResponse(BaseModel):
    estimated_salary: float
