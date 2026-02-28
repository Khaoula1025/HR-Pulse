from typing import List, Optional
import json
from pydantic import BaseModel, field_validator

class JobBase(BaseModel):
    job_title: str
    skills_extracted: List[str]

class JobCreate(JobBase):
    salary_estimate: Optional[float] = None


class JobResponse(BaseModel):
    id: int
    job_title: str
    skills_extracted: List[str]
    salary_estimate: Optional[float] = None

    @field_validator("skills_extracted", mode="before")
    @classmethod
    def parse_json_string(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v
    
    class Config:
        from_attributes = True

class PredictionInput(BaseModel):
    job_title: str
    skills: List[str]

class PredictionOutput(BaseModel):
    job_title: str
    predicted_salary: float