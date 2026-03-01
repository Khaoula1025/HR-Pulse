import os
import joblib
import pandas as pd
from pathlib import Path
from app.schemas.prediction import PredictRequest, VALID_SKILLS

MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/salary_model.pkl"))

# Load once at startup
_model = None

def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Run train.py first to generate salary_model.pkl"
            )
        _model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded. Expected features: {_model.feature_names_in_}")
    return _model
get_model()  # Load model at startup


def build_feature_row(req: PredictRequest) -> pd.DataFrame:
    """
    Map PredictRequest fields to the exact feature names the model was trained on.

    Model expects (in this order):
        Rating, Founded, size_ordinal, revenue_ordinal, has_competitors,
        is_at_hq, hq_is_international,
        skill_python, skill_sql, skill_spark, skill_aws, skill_azure,
        skill_machine_learning, skill_deep_learning, skill_tensorflow,
        skill_pytorch, skill_tableau, skill_java, skill_scala,
        skill_hadoop, skill_git, skill_linux, skill_docker,
        skill_count,
        Sector, seniority, core_role, type_of_ownership, job_state
    """
    # Normalize skills to lowercase for matching
    skills_lower = [s.lower().replace(" ", "_") for s in req.skills]

    # Build skill binary flags
    skill_cols = {
        f"skill_{s}": int(s in skills_lower) for s in VALID_SKILLS
    }

    row = {
        # Numeric — exact column names from training
        "Rating":             req.rating,
        "Founded":            req.founded,
        "size_ordinal":       req.size_ordinal,
        "revenue_ordinal":    req.revenue_ordinal,
        "has_competitors":    req.has_competitors,
        "is_at_hq":           req.is_at_hq,
        "hq_is_international":req.hq_is_international,

        # Skill binary columns
        **skill_cols,

        # skill_count = number of skills provided
        "skill_count":        len(req.skills),

        # Categorical — exact column names from training
        "Sector":             req.sector,
        "seniority":          req.seniority,
        "core_role":          req.core_role,
        "type_of_ownership":  req.type_of_ownership,
        "job_state":          req.job_state.upper(),
    }

    return pd.DataFrame([row])


def predict(req: PredictRequest) -> dict:
    """
    Run salary prediction for a single job.

    Returns:
        predicted_salary, range_min, range_max, currency,
        skills_used, input_summary
    """
    model = get_model()
    df    = build_feature_row(req)

    predicted = float(model.predict(df)[0])

    # ±15% confidence range (reflects ~17% MAE on this dataset)
    range_min = round(predicted * 0.85)
    range_max = round(predicted * 1.15)

    skills_used = [s for s in req.skills if s.lower().replace(" ", "_") in VALID_SKILLS]

    return {
        "predicted_salary": round(predicted),
        "range_min":        range_min,
        "range_max":        range_max,
        "currency":         "USD",
        "skills_used":      skills_used,
        "input_summary": {
            "sector":    req.sector,
            "seniority": req.seniority,
            "core_role": req.core_role,
            "state":     req.job_state.upper(),
            "skills":    req.skills,
        },
    }