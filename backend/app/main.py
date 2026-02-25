# from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.endpoints import jobs, predictor


app = FastAPI(title="HR-Pulse API")

app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(predictor.router, prefix="/predict", tags=["predictor"])


@app.get("/health")
def health():
    return {"status": "ok"}
