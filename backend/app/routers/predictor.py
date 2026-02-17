from fastapi import APIRouter
from app.schemas.job import SalaryPredictRequest, SalaryPredictResponse
from app.services.predictor_service import predict_salary

router = APIRouter()


@router.post("/", response_model=SalaryPredictResponse)
def predict(request: SalaryPredictRequest):
    salary = predict_salary(request.job_title, request.skills)
    return SalaryPredictResponse(estimated_salary=salary)
