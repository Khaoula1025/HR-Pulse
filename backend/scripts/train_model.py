"""Train a salary regression model from jobs.csv."""
import re
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from pathlib import Path

CSV_PATH = "data/raw/jobs.csv"
MODEL_PATH = Path("ml/salary_model.pkl")


def parse_salary(salary_str: str) -> float | None:
    matches = re.findall(r"\$(\d+)K", str(salary_str))
    if len(matches) >= 2:
        return (int(matches[0]) + int(matches[1])) / 2
    return None


def main():
    df = pd.read_csv(CSV_PATH)
    df["salary_avg"] = df["Salary Estimate"].apply(parse_salary)
    df.dropna(subset=["salary_avg"], inplace=True)

    # Simple feature: description length (extend with real features)
    df["desc_len"] = df["Job Description"].apply(lambda x: len(str(x).split()))
    X = df[["desc_len"]].values
    y = df["salary_avg"].values

    model = LinearRegression()
    model.fit(X, y)

    MODEL_PATH.parent.mkdir(exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
