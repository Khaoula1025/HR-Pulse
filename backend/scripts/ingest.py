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
def check_logic(df: pd.DataFrame):
    print("--- Logical Consistency Check ---")
    # Check for the common Glassdoor '-1' placeholder
    minus_ones = (df == -1).sum().sum() + (df == "-1").sum().sum()
    print(f"Total '-1' placeholders found: {minus_ones}")
    
    # Check for impossible ratings
    out_of_bounds_rating = df[(df['Rating'] < 0) | (df['Rating'] > 5)].shape[0]
    print(f"Ratings outside 0-5 range: {out_of_bounds_rating}")
    
    # Check for unrealistic years
    current_year = 2026
    future_founded = df[df['Founded'] > current_year].shape[0]
    print(f"Companies founded in the future: {future_founded}")

def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Drop duplicates and empty rows
    df = df.drop_duplicates()
    df = df.dropna(subset=["Job Title", "Job Description"])

    # Clean job title (strip whitespace, lowercase)
    df["job_title"] = df["Job Title"].str.strip().str.lower()

    return df









