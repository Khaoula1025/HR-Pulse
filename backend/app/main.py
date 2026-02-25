# from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.endpoints import jobs, predictor
from app.api.v1.endpoints import auth
from app.models import user
from app.db.session import Base, engine

app = FastAPI(title="HR-Pulse API")

Base.metadata.create_all(bind=engine)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(predictor.router, prefix="/predict", tags=["predictor"])



@app.get("/health")
def health():
    return {"status": "ok"}
