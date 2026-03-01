from fastapi import APIRouter, HTTPException , Depends
from app.schemas.prediction import PredictRequest, PredictResponse, VALID_SKILLS
from app.services.predictor_service import predict
from app.api.deps import get_current_user
router = APIRouter()


@router.post("", response_model=PredictResponse)
def predict_salary(
    req: PredictRequest,
   current_user = Depends(get_current_user)
                   ):
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