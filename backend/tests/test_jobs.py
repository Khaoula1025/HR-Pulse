from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# ─── 2. Test: construction des features du modèle ────────────────────────────
def test_build_feature_row():
    from app.services.predictor_service import build_feature_row
    from app.schemas.prediction import PredictRequest

    req = PredictRequest(
        rating=3.5,
        founded=2010,
        size_ordinal=2,
        revenue_ordinal=3,
        has_competitors=1,
        is_at_hq=1,
        hq_is_international=0,
        skills=["python", "sql"],
        sector="Tech",
        seniority="mid",
        core_role="data_scientist",
        type_of_ownership="Private",
        job_state="CA",
    )

    df = build_feature_row(req)
    assert df.shape[0] == 1               # une seule ligne
    assert "skill_python" in df.columns   # colonne skill présente
    assert df["skill_python"].iloc[0] == 1
    assert df["skill_count"].iloc[0] == 2


# ─── 3. Test: API FastAPI sans DB (mock) ─────────────────────────────────────
@patch("app.api.deps.get_db")
def test_health_endpoint(mock_db):
    from app.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


# ─── 4. Test: prédiction avec modèle mocké ───────────────────────────────────
@patch("app.services.predictor_service.get_model")
def test_predict_mock(mock_get_model):
    mock_model = MagicMock()
    mock_model.predict.return_value = [120000.0]
    mock_model.feature_names_in_ = []
    mock_get_model.return_value = mock_model

    from app.services.predictor_service import predict
    from app.schemas.prediction import PredictRequest

    req = PredictRequest(
        rating=3.5,
        founded=2010,
        size_ordinal=2,
        revenue_ordinal=3,
        has_competitors=1,
        is_at_hq=1,
        hq_is_international=0,
        skills=["python"],
        sector="Tech",
        seniority="mid",
        core_role="data_scientist",
        type_of_ownership="Private",
        job_state="CA",
    )

    result = predict(req)
    assert result["predicted_salary"] == 120000
    assert result["range_min"] < result["predicted_salary"]
    assert result["range_max"] > result["predicted_salary"]
    assert result["currency"] == "USD"