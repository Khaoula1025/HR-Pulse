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
)
INPUT_PATH  = "backend/data/raw/jobs.csv"
OUTPUT_PATH = "backend/data/processed/jobs_cleaned.csv"

# PIPELINE

def run_pipeline(input_path: str, output_path: str) -> pd.DataFrame:

    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"Shape: {df.shape}\n")

    # ── Step 1: Replace -1 sentinels ─────────────────────────────────────────
    print("Step 1: Replacing -1 sentinel values...")
    df = replace_negative_ones(df)

    # ── Step 2: Job Description ───────────────────────────────────────────────
    print("Step 2: Cleaning Job Description for embedding...")
    df["Job Description"] = df["Job Description"].apply(clean_for_embedding)

    # ── Step 3: Company Name ──────────────────────────────────────────────────
    print("Step 3: Cleaning Company Name...")
    df["Company Name"] = df["Company Name"].apply(clean_company_name)

    # ── Step 4: Job Title → cleaned + seniority + core role ──────────────────
    print("Step 4: Processing Job Title...")
    parsed = df["Job Title"].apply(parse_job_title).apply(pd.Series)
    df["seniority"] = parsed["seniority"]
    df["job_title"] = parsed["core_role"] + " - " + parsed["clean_title"]
    # ── Step 5: Salary ────────────────────────────────────────────────────────
    print("Step 5: Parsing Salary Estimate...")
    df["Salary"] = process_salary(df, "Salary Estimate", audit=True)

    # ── Step 6: Size ──────────────────────────────────────────────────────────
    print("Step 6: Encoding Size...")
    size_encoded = df["Size"].apply(encode_size)
    df["size_ordinal"] = size_encoded.apply(lambda x: x[0])
    df["size_is_top"]  = size_encoded.apply(lambda x: x[1])

    # ── Step 7: Revenue ───────────────────────────────────────────────────────
    print("Step 7: Encoding Revenue...")
    rev_encoded = df["Revenue"].apply(encode_revenue)
    df["revenue_ordinal"] = rev_encoded.apply(lambda x: x[0])
    df["revenue_is_top"]  = rev_encoded.apply(lambda x: x[1])

    # ── Step 8: Location & Headquarters ──────────────────────────────────────
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
    df = df.drop(columns=["Location", "Headquarters",'Job Title'])  # drop original columns after parsing

    # ── Step 9: Type of Ownership ─────────────────────────────────────────────
    print("Step 9: Grouping Type of Ownership...")
    df["type_of_ownership"] = df["Type of ownership"].map(OWNERSHIP_MAP)

    # ── Step 10: Drop redundant columns ───────────────────────────────────────
    print("Step 10: Dropping redundant columns...")
    df = df.drop(columns=[
        "Industry",          # redundant with Sector (Sector is the parent)
        "job_city",          # too high cardinality (200+ unique cities)
        "hq_city",           # same reason
        "Type of ownership", # replaced by ownership_grouped
    ])

    # ── Done ──────────────────────────────────────────────────────────────────
    print(f"\nPipeline complete. Final shape: {df.shape}")
    print(f"Saving to {output_path}...")
    df.to_csv(output_path, index=False)
    print("Done.")

    return df

# ENTRY POINT

if __name__ == "__main__":
    df_clean = run_pipeline(INPUT_PATH, OUTPUT_PATH)

    print("\n=== COLUMN OVERVIEW ===")
    print(df_clean.dtypes.to_string())

    print("\n=== MISSING VALUES ===")
    missing = df_clean.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    print(missing.to_string() if not missing.empty else "None")
