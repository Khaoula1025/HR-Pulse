from sqlalchemy import Column, Integer, String, Float, Text
from app.db.session import Base

class Job(Base):
    __tablename__ = "job_skills"  # Change this from "jobs" to "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=False)
    skills_extracted = Column(Text, nullable=True) 
    # salary_estimate = Column(Float, nullable=True) # Ensure this exists in your SQL script too!