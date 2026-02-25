# from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.endpoints import jobs, predictor
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="HR-Pulse API")

app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(predictor.router, prefix="/predict", tags=["predictor"])

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development; in production use ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

