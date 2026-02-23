import os
import json
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

INPUT_PATH   = "backend/data/processed/jobs_with_skills.csv"
TABLE_NAME   = "job_skills"
DATABASE_URL = os.getenv("DATABASE_URL")
# CONNECT
def get_engine():

    url = os.getenv("DATABASE_URL")

    engine = create_engine(url, fast_executemany=True)
    print("  Connected to Azure SQL")
    return engine

# CREATE TABLE
CREATE_TABLE_SQL = f"""
IF NOT EXISTS (
    SELECT * FROM sysobjects
    WHERE name = '{TABLE_NAME}' AND xtype = 'U'
)
CREATE TABLE {TABLE_NAME} (
    id               INT           PRIMARY KEY,
    job_title        NVARCHAR(255) NOT NULL,
    skills_extracted NVARCHAR(MAX)
);
"""


def create_table(engine):
    with engine.begin() as conn:
        conn.execute(text(CREATE_TABLE_SQL))
    print(f"  Table '{TABLE_NAME}' ready")

# PREPARE DATA
def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and clean the 3 columns required by the brief:
      - id               : unique integer identifier
      - job_title        : cleaned job title string
      - skills_extracted : JSON string (list of skills)
    """
    result = pd.DataFrame()

    # id — use the index column from the CSV
    result["id"] = df["index"].astype(int)

    # job_title — already cleaned by preprocessing
    result["job_title"] = df["job_title"].fillna("unknown").str.strip().str[:255]

    # skills_extracted — already a JSON string from ner_extraction.py
    # Validate each row: parse and re-serialize to ensure clean JSON
    def normalize_skills(val):
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    # Keep only strings, deduplicate, sort for consistency
                    clean = sorted(set(str(s).strip() for s in parsed if s))
                    return json.dumps(clean)
            except (json.JSONDecodeError, TypeError):
                pass
        return json.dumps([])  # empty list if invalid

    result["skills_extracted"] = df["skills_extracted"].apply(normalize_skills)

    return result

# INSERT
def insert_data(df_clean: pd.DataFrame, engine) -> int:
    """
    Insert rows using MERGE (upsert) to avoid duplicate key errors
    if the script is run multiple times.
    """
    rows_inserted = 0

    with engine.begin() as conn:
        for _, row in df_clean.iterrows():
            upsert_sql = text(f"""
                MERGE {TABLE_NAME} AS target
                USING (VALUES (:id, :job_title, :skills_extracted))
                    AS source (id, job_title, skills_extracted)
                ON target.id = source.id
                WHEN MATCHED THEN
                    UPDATE SET
                        job_title        = source.job_title,
                        skills_extracted = source.skills_extracted
                WHEN NOT MATCHED THEN
                    INSERT (id, job_title, skills_extracted)
                    VALUES (source.id, source.job_title, source.skills_extracted);
            """)
            conn.execute(upsert_sql, {
                "id":               int(row["id"]),
                "job_title":        row["job_title"],
                "skills_extracted": row["skills_extracted"],
            })
            rows_inserted += 1

            if rows_inserted % 100 == 0:
                print(f"  Inserted {rows_inserted}/{len(df_clean)} rows...", end="\r")

    return rows_inserted

# VERIFY
def verify(engine):
    """Run a quick sanity check after insertion."""
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).scalar()
        sample = conn.execute(
            text(f"SELECT TOP 3 id, job_title, LEFT(skills_extracted, 80) FROM {TABLE_NAME}")
        ).fetchall()

    print(f"\n  Total rows in table: {count}")
    print(f"\n  Sample rows:")
    for row in sample:
        print(f"    id={row[0]} | title={row[1]} | skills={row[2]}...")

# MAIN
def run():
    print("\n" + "=" * 60)
    print("  STEP 1: Load data")
    print("=" * 60)
    df = pd.read_csv(INPUT_PATH)
    print(f"  Loaded {len(df)} rows from {INPUT_PATH}")

    print("\n" + "=" * 60)
    print("  STEP 2: Connect to Azure SQL")
    print("=" * 60)
    engine = get_engine()

    print("\n" + "=" * 60)
    print("  STEP 3: Create table (if not exists)")
    print("=" * 60)
    create_table(engine)

    print("\n" + "=" * 60)
    print("  STEP 4: Prepare data")
    print("=" * 60)
    df_clean = prepare_data(df)
    print(f"  Rows to insert : {len(df_clean)}")
    print(f"  Columns        : {df_clean.columns.tolist()}")
    print(f"\n  Sample row:")
    row = df_clean.iloc[0]
    print(f"    id             : {row['id']}")
    print(f"    job_title      : {row['job_title']}")
    print(f"    skills_extracted: {row['skills_extracted'][:80]}...")

    print("\n" + "=" * 60)
    print("  STEP 5: Insert into Azure SQL")
    print("=" * 60)
    n = insert_data(df_clean, engine)
    print(f"\n  Inserted {n} rows successfully")

    print("\n" + "=" * 60)
    print("  STEP 6: Verify")
    print("=" * 60)
    verify(engine)

    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60)


if __name__ == "__main__":
    run()