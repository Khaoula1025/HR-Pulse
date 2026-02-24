from fastapi import APIRouter, HTTPException
from app.schemas.prediction import PredictRequest, PredictResponse, VALID_SKILLS
from app.services.predictor_service import predict

router = APIRouter()


@router.post("", response_model=PredictResponse)
def predict_salary(req: PredictRequest):
    """
    Predict the estimated salary for a job posting.

    Provide company info, job details, location, and required skills.
    Returns a predicted salary with a ±15% confidence range.
    """
    try:
        result = predict(req)
        return PredictResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/skills")
def list_valid_skills():
    """Return the list of skills the model recognizes."""
    return {"skills": VALID_SKILLS, "count": len(VALID_SKILLS)}