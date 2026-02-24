# from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import jobs, predictor
# from app.telemetry.otel import setup_telemetry


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     setup_telemetry()
#     yield


app = FastAPI(title="HR-Pulse API")

app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(predictor.router, prefix="/predict", tags=["predictor"])


@app.get("/health")
def health():
    return {"status": "ok"}
