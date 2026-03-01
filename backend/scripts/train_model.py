import json
import warnings
import pandas as pd
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

warnings.filterwarnings("ignore")

# CONFIG

INPUT_PATH = "backend/data/processed/jobs_with_skills.csv"
MODEL_DIR  = Path("backend/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE    = 0.2

# Core structured features
NUMERIC_FEATURES = [
    "Rating",
    "Founded",
    "size_ordinal",
    "revenue_ordinal",
    "has_competitors",
    "is_at_hq",
    "hq_is_international",
]

CATEGORICAL_FEATURES = [
    "Sector",
    "seniority",
    "core_role",
    "type_of_ownership",
    "job_state",
]

SKILL_FLAGS = {
    "skill_python":          "python",
    "skill_sql":             "sql",
    "skill_spark":           "spark",
    "skill_aws":             "aws",
    "skill_azure":           "azure",
    "skill_machine_learning":"machine learning",
    "skill_deep_learning":   "deep learning",
    "skill_tensorflow":      "tensorflow",
    "skill_pytorch":         "pytorch",
    "skill_tableau":         "tableau",
    "skill_java":            "java",
    "skill_scala":           "scala",
    "skill_hadoop":          "hadoop",
    "skill_git":             "git",
    "skill_linux":           "linux",
    "skill_docker":          "docker",
}

SKILL_COLS = list(SKILL_FLAGS.keys())


# FEATURE ENGINEERING

def build_skill_features(df: pd.DataFrame) -> pd.DataFrame:

    def parse_skills(val):
        if isinstance(val, str):
            try:
                return [s.lower().strip() for s in json.loads(val)]
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    skills_lists = df["skills_extracted"].apply(parse_skills)

    for col, skill in SKILL_FLAGS.items():
        df[col] = skills_lists.apply(lambda lst: int(skill in lst))

    df["skill_count"] = skills_lists.apply(len)

    return df


# SKLEARN PIPELINE

def build_pipeline(model) -> Pipeline:
    all_numeric  = NUMERIC_FEATURES + SKILL_COLS + ["skill_count"]
    categorical  = CATEGORICAL_FEATURES

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1
        )),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer,     all_numeric),
        ("cat", categorical_transformer, categorical),
    ])

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model",        model),
    ])


# TRAINING

def train_and_evaluate():
    print("\n" + "=" * 60)
    print("  STEP 1: Load data")
    print("=" * 60)
    df = pd.read_csv(INPUT_PATH)
    print(f"  Shape: {df.shape}")

    print("\n" + "=" * 60)
    print("  STEP 2: Build skill binary features")
    print("=" * 60)
    df = build_skill_features(df)
    for col in SKILL_COLS:
        pct = df[col].mean() * 100
        print(f"  {col:35s}: {pct:.0f}%")
    print(f"  {'skill_count (mean)':35s}: {df['skill_count'].mean():.1f}")

    print("\n" + "=" * 60)
    print("  STEP 3: Prepare X and y")
    print("=" * 60)
    all_features = NUMERIC_FEATURES + SKILL_COLS + ["skill_count"] + CATEGORICAL_FEATURES

    df = df.dropna(subset=["Salary"])
    X = df[all_features]
    y = df["Salary"]

    n_numeric = len(NUMERIC_FEATURES) + len(SKILL_COLS) + 1  # +1 for skill_count
    print(f"  Samples : {len(X)}")
    print(f"  Features: {len(all_features)} "
          f"({n_numeric} numeric/skill, {len(CATEGORICAL_FEATURES)} categorical)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"  Train: {len(X_train)} | Test: {len(X_test)}")

    print("\n" + "=" * 60)
    print("  STEP 4: Train models")
    print("=" * 60)

    models = {
        "Ridge": Ridge(alpha=10.0),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, max_depth=8,
            min_samples_leaf=5, random_state=RANDOM_STATE
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=200, max_depth=4,
            learning_rate=0.05, min_samples_leaf=5,
            random_state=RANDOM_STATE
        ),
    }

    results = {}
    for name, model in models.items():
        pipe = build_pipeline(model)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        r2  = r2_score(y_test, y_pred)

        cv_scores = cross_val_score(
            pipe, X, y, cv=5,
            scoring="neg_mean_absolute_error"
        )
        cv_mae = -cv_scores.mean()
        cv_std = cv_scores.std()

        results[name] = {"pipe": pipe, "mae": mae, "r2": r2, "cv_mae": cv_mae}

        print(f"\n  {name}")
        print(f"    MAE    : ${mae:,.0f}")
        print(f"    R²     : {r2:.4f}")
        print(f"    CV MAE : ${cv_mae:,.0f} (±${cv_std:,.0f})")

    print("\n" + "=" * 60)
    print("  STEP 5: Best model")
    print("=" * 60)
    best_name = min(results, key=lambda k: results[k]["mae"])
    best      = results[best_name]
    print(f"  Winner : {best_name}")
    print(f"  MAE    : ${best['mae']:,.0f}")
    print(f"  R²     : {best['r2']:.4f}")

    # Feature importances from Random Forest
    rf_pipe  = results["Random Forest"]["pipe"]
    rf_model = rf_pipe.named_steps["model"]
    feature_names = NUMERIC_FEATURES + SKILL_COLS + ["skill_count"] + CATEGORICAL_FEATURES
    importances   = pd.Series(rf_model.feature_importances_, index=feature_names)

    print("\n  Top 10 features (Random Forest importance):")
    for feat, imp in importances.sort_values(ascending=False).head(10).items():
        print(f"    {feat:35s}: {imp:.4f}")

    print("\n  Skill features:")
    for feat, imp in importances[SKILL_COLS + ["skill_count"]].sort_values(ascending=False).items():
        print(f"    {feat:35s}: {imp:.4f}")

    print("\n" + "=" * 60)
    print("  STEP 6: Save best model")
    print("=" * 60)
    model_path = MODEL_DIR / "salary_model.pkl"
    joblib.dump(best["pipe"], model_path)
    print(f"  Saved: {model_path}")

    return best["pipe"], best_name, best


# PREDICT FUNCTION (used by FastAPI)

def predict_salary(model_path: str, input_data: dict) -> dict:
    """
    Load saved model and predict salary for a single job posting.

    Args:
        model_path : path to salary_model.pkl
        input_data : dict with all feature keys

    Returns:
        dict with predicted_salary, range_min, range_max, currency
    """
    pipe = joblib.load(model_path)
    df   = pd.DataFrame([input_data])
    pred = float(pipe.predict(df)[0])

    return {
        "predicted_salary": round(pred),
        "range_min":        round(pred * 0.85),
        "range_max":        round(pred * 1.15),
        "currency":         "USD",
    }


# MAIN

if __name__ == "__main__":
    pipe, best_name, metrics = train_and_evaluate()
    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60)
    print(f"  Best model : {best_name}")
    print(f"  MAE        : ${metrics['mae']:,.0f}")
    print(f"  R²         : {metrics['r2']:.4f}")
    print("  Saved to   : backend/models/salary_model.pkl")