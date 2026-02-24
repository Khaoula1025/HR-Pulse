from fastapi import APIRouter, HTTPException
from app.schemas.job import PredictionInput, PredictionOutput
from app.services.predictor_service import predictor_plugin

router = APIRouter()

@router.post("/", response_model=PredictionOutput)
def get_salary_prediction(payload: PredictionInput):
    try:
        prediction = predictor_plugin.predict_salary(payload)
        return {"job_title": payload.job_title, "predicted_salary": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))