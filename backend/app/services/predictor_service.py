import pickle
from pathlib import Path
import numpy as np

MODEL_PATH = Path(__file__).resolve().parents[2] / "ml" / "salary_model.pkl"
_model = None


def _load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
    return _model


def predict_salary(job_title: str, skills: list[str]) -> float:
    model = _load_model()
    if model is None:
        return 0.0
    # Basic feature: number of skills as proxy (extend as needed)
    features = np.array([[len(skills)]])
    return float(model.predict(features)[0])
