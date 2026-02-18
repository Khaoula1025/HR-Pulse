import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error
import os


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Target
    df["salary_avg"] = df["Salary Estimate"].apply(parse_salary)
    df = df.dropna(subset=["salary_avg"])

    # Numeric: company size as midpoint
    df["size_numeric"] = df["Size"].apply(clean_size)

    # Numeric: company age
    df["company_age"] = 2026 - pd.to_numeric(df["Founded"], errors="coerce")

    # Encode categoricals
    le = LabelEncoder()
    for col in ["Sector", "Type of ownership", "Location"]:
        df[col + "_enc"] = le.fit_transform(df[col].astype(str))

    return df


def train(csv_path: str, model_output: str = "models/salary_model.pkl"):
    df = pd.read_csv(csv_path)
    df = preprocess(df)

    features = [
        "Rating",
        "size_numeric",
        "company_age",
        "Sector_enc",
        "Type of ownership_enc",
        "Location_enc",
    ]

    df = df.dropna(subset=features)
    X = df[features]
    y = df["salary_avg"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    r2 = model.score(X_test, y_test)

    print(f"R2 Score : {r2:.2f}")
    print(f"MAE      : ${mae:,.0f}")

    os.makedirs(os.path.dirname(model_output), exist_ok=True)
    joblib.dump(model, model_output)
    print(f"Model saved to {model_output}")


if __name__ == "__main__":
    train("data/jobs.csv")