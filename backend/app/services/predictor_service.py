import joblib
import os
import pandas as pd # Highly recommended for inspecting features
from app.schemas.job import PredictionInput

# 1. Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
MODEL_PATH = os.path.join(backend_dir, "models", "salary_model.pkl")

# 2. Global Model Loading (equivalent to __init__)
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

# DEBUG: Print features on startup
if hasattr(model, 'feature_names_in_'):
    print(f"✅ Model loaded. Expected features: {model.feature_names_in_}")
elif hasattr(model, 'get_feature_names_out'):
    print(f"✅ Pipeline loaded. Features: {model.get_feature_names_out()}")
else:
    print("⚠️ Model loaded, but feature names couldn't be detected automatically.")

# 3. The Functional Predictor
def predict_salary(data: PredictionInput) -> float:
    """
    Takes PredictionInput and returns the estimated salary.
    """
    # Logic to handle the input. 
    # If your model was trained on a DataFrame, use a DataFrame here too:
    features = [[data.job_title, len(data.skills)]] 
    
    prediction = model.predict(features)
    
    # Extract the first value and round
    return round(float(prediction[0]), 2)