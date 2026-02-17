from app.services.predictor_service import predict_salary


def test_predict_salary_no_model():
    result = predict_salary("Data Scientist", ["Python", "SQL"])
    assert isinstance(result, float)
