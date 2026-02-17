"""Clean jobs.csv, run NER, and insert into Azure SQL."""
import json
import re
import pandas as pd
from sqlalchemy.orm import Session
from app.database import engine, Base
from app.models.job import Job
from app.services.ner_service import extract_skills

CSV_PATH = "data/raw/jobs.csv"


def clean_title(title: str) -> str:
    return re.sub(r"\s+", " ", str(title)).strip()


def main():
    Base.metadata.create_all(bind=engine)
    df = pd.read_csv(CSV_PATH)
    df["Job Title"] = df["Job Title"].apply(clean_title)
    df.dropna(subset=["Job Title"], inplace=True)

    with Session(engine) as session:
        for _, row in df.iterrows():
            skills = extract_skills(str(row.get("Job Description", "")))
            job = Job(
                job_title=row["Job Title"],
                skills_extracted=skills,
            )
            session.add(job)
        session.commit()
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
