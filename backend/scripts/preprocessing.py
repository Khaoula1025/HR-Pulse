"""
preprocessing.py
----------------
Calls all cleaning functions from preprocessing_utils.py
and runs the full pipeline.

Usage:
    python preprocessing.py

Output:
    backend/data/processed/jobs_cleaned.csv
"""

import pandas as pd
from preprocessing_utils import (
    replace_negative_ones,
    clean_for_embedding,
    clean_company_name,
    parse_job_title,
    process_salary,
    encode_size,
    encode_revenue,
    parse_location,
    US_STATES,
    OWNERSHIP_MAP,
    handle_outliers_and_nulls,
)

INPUT_PATH  = "backend/data/raw/jobs.csv"
OUTPUT_PATH = "backend/data/processed/jobs_cleaned.csv"


# =============================================================================
# PIPELINE
# =============================================================================

def run_pipeline(input_path: str, output_path: str) -> pd.DataFrame:

    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"Shape: {df.shape}\n")

    # Step 1: Replace -1 sentinels
    print("Step 1: Replacing -1 sentinel values...")
    df = replace_negative_ones(df)

    # Step 2: Job Description
    print("Step 2: Cleaning Job Description for embedding...")
    df["Job Description"] = df["Job Description"].apply(clean_for_embedding)

    # Step 3: Company Name
    print("Step 3: Cleaning Company Name...")
    df["Company Name"] = df["Company Name"].apply(clean_company_name)

    # Step 4: Job Title -> job_title + seniority + core_role
    # job_title  : cleaned text string  -> used for embeddings, NOT direct encoding
    # seniority  : categorical (8 levels) -> training feature
    # core_role  : categorical (8 roles)  -> training feature
    print("Step 4: Processing Job Title...")
    parsed = df["Job Title"].apply(parse_job_title).apply(pd.Series)
    df["job_title"] = parsed["job_title"]
    df["seniority"] = parsed["seniority"]
    df["core_role"] = parsed["core_role"]
    df = df.drop(columns=["Job Title"])

    # Step 5: Salary
    print("Step 5: Parsing Salary Estimate...")
    df["Salary"] = df["Salary Estimate"].apply(process_salary)
    df = df.drop(columns=["Salary Estimate"])

    # Step 6: Size
    print("Step 6: Encoding Size...")
    size_encoded      = df["Size"].apply(encode_size)
    df["size_ordinal"] = size_encoded.apply(lambda x: x[0])
    df["size_is_top"]  = size_encoded.apply(lambda x: x[1])
    df = df.drop(columns=["Size"])

    # Step 7: Revenue
    print("Step 7: Encoding Revenue...")
    rev_encoded           = df["Revenue"].apply(encode_revenue)
    df["revenue_ordinal"] = rev_encoded.apply(lambda x: x[0])
    df["revenue_is_top"]  = rev_encoded.apply(lambda x: x[1])
    df = df.drop(columns=["Revenue"])

    # Step 8: Location & Headquarters
    print("Step 8: Parsing Location and Headquarters...")
    df[["job_city", "job_state"]] = df["Location"].apply(
        lambda x: pd.Series(parse_location(x))
    )
    df[["hq_city", "hq_state"]] = df["Headquarters"].apply(
        lambda x: pd.Series(parse_location(x))
    )
    df["is_remote"]           = df["Location"].str.lower().eq("remote").astype(int)
    df["is_at_hq"]            = (df["Location"] == df["Headquarters"]).astype(int)
    df["hq_is_international"] = df["hq_state"].apply(
        lambda s: 0 if pd.isna(s) or s in US_STATES else 1
    )
    df = df.drop(columns=["Location", "Headquarters", "job_city", "hq_city"])

    # Step 9: Type of Ownership
    print("Step 9: Grouping Type of Ownership...")
    df["type_of_ownership"] = df["Type of ownership"].map(OWNERSHIP_MAP)
    df = df.drop(columns=["Type of ownership"])

    # Step 10: Drop redundant columns
    print("Step 10: Dropping redundant columns...")
    df = df.drop(columns=["Industry"])

    # Step 11: Handle outliers & nulls
    print("Step 11: Handling outliers and nulls...")
    df = handle_outliers_and_nulls(df)

    # Done
    print(f"\nPipeline complete. Final shape: {df.shape}")
    print(f"Saving to {output_path}...")
    df.to_csv(output_path, index=False)
    print("Done.")

    return df


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    df_clean = run_pipeline(INPUT_PATH, OUTPUT_PATH)

    print("\n=== COLUMN OVERVIEW ===")
    print(df_clean.dtypes.to_string())

    print("\n=== MISSING VALUES ===")
    missing = df_clean.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    print(missing.to_string() if not missing.empty else "None")

    print("\n=== SAMPLE (5 rows, key columns) ===")
    print(df_clean[[
        "Company Name", "job_title", "core_role", "seniority",
        "Salary", "job_state", "size_ordinal", "revenue_ordinal",
        "type_of_ownership", "is_remote",
    ]].head().to_string())