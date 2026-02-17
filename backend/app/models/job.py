from sqlalchemy import Column, Integer, String, JSON
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=False)
    skills_extracted = Column(JSON, nullable=True)
