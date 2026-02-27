# from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.endpoints import jobs, predictor
from app.api.v1.endpoints import auth
from app.db.session import Base, engine
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="HR-Pulse API")

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️  DB not available at startup: {e}")
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(predictor.router, prefix="/predict", tags=["predictor"])



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

