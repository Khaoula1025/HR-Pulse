import pandas as pd
import re

def inspect_df(df: pd.DataFrame) -> None:
    print("SHAPE:", df.shape)
    print("\nCOLUMNS:", df.columns.tolist())
    print("\nDTYPES:\n", df.dtypes)
    print("\nNULLS:\n", df.isnull().sum())
    print("\nDUPLICATES:", df.duplicated().sum())
    print("\nSAMPLE:\n", df.head(3))
    print("\nSTATS:\n", df.describe(include="all"))

#inspect_df(pd.read_csv("backend/data/raw/jobs.csv"))


def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Drop duplicates and empty rows
    df = df.drop_duplicates()
    df = df.dropna(subset=["Job Title", "Job Description"])

    # Clean job title (strip whitespace, lowercase)
    df["job_title"] = df["Job Title"].str.strip().str.lower()

    return df









