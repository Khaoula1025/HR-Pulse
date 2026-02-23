"""
embedding_pipeline.py
---------------------
Generates sentence embeddings for Job Description,
reduces dimensions with PCA, and merges into the dataset.

Depends on:
    - backend/data/processed/jobs_cleaned.csv  (output of preprocessing.py)

Output:
    - backend/data/processed/job_desc_embeddings.npy   raw (N, 384) embeddings
    - backend/data/processed/jobs_with_embeddings.csv  dataset + emb columns

Usage:
    python embedding_pipeline.py
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer


# =============================================================================
# CONFIG
# =============================================================================

MODEL_NAME      = "all-MiniLM-L6-v2"
BATCH_SIZE      = 32
NORMALIZE       = True    # L2-normalize for stable magnitudes
MAX_CHARS       = 1800    # ~512 token limit for this model
PCA_COMPONENTS  = 50      # 384 → 50 dims (increase to 100+ for linear models)

INPUT_PATH      = "backend/data/processed/jobs_cleaned.csv"
EMBEDDINGS_PATH = "backend/data/processed/job_desc_embeddings.npy"
OUTPUT_PATH     = "backend/data/processed/jobs_with_embeddings.csv"

TEXT_COL        = "Job Description"


# =============================================================================
# PIPELINE
# =============================================================================

def run_embedding_pipeline() -> pd.DataFrame:

    # ── Step 1: Load ──────────────────────────────────────────────────────────
    print("Step 1: Loading data...")
    df = pd.read_csv(INPUT_PATH)
    print(f"  Shape: {df.shape}")

    # ── Step 2: Prepare texts ─────────────────────────────────────────────────
    print("\nStep 2: Preparing texts...")
    texts = (
        df[TEXT_COL]
        .fillna("")
        .apply(lambda t: t[:MAX_CHARS])
        .tolist()
    )
    print(f"  Texts    : {len(texts)}")
    print(f"  Nulls    : {df[TEXT_COL].isna().sum()} (replaced with empty string)")
    print(f"  Truncated: {(df[TEXT_COL].fillna('').apply(len) > MAX_CHARS).sum()} (cut at {MAX_CHARS} chars)")

    # ── Step 3: Generate embeddings ───────────────────────────────────────────
    print(f"\nStep 3: Encoding with {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=NORMALIZE,
        convert_to_numpy=True,
    ).astype(np.float32)
    print(f"  Shape: {embeddings.shape} | dtype: {embeddings.dtype}")

    # ── Step 4: Save raw embeddings ───────────────────────────────────────────
    print(f"\nStep 4: Saving raw embeddings -> {EMBEDDINGS_PATH}")
    np.save(EMBEDDINGS_PATH, embeddings)

    # ── Step 5: PCA reduction ─────────────────────────────────────────────────
    print(f"\nStep 5: PCA {embeddings.shape[1]} -> {PCA_COMPONENTS} dims...")
    pca = PCA(n_components=PCA_COMPONENTS, random_state=42)
    embeddings_reduced = pca.fit_transform(embeddings).astype(np.float32)
    print(f"  Variance retained: {pca.explained_variance_ratio_.sum():.2%}")

    # ── Step 6: Merge & save ──────────────────────────────────────────────────
    print(f"\nStep 6: Merging and saving -> {OUTPUT_PATH}")
    emb_cols = [f"emb_{i}" for i in range(PCA_COMPONENTS)]
    emb_df   = pd.DataFrame(embeddings_reduced, columns=emb_cols, index=df.index)
    df_final = pd.concat([df, emb_df], axis=1)
    df_final.to_csv(OUTPUT_PATH, index=False)

    print(f"\nDone. Final shape: {df_final.shape}")
    print(f"Add to NUMERIC_FEATURES in train.py:")
    print(f"  NUMERIC_FEATURES += [f'emb_{{i}}' for i in range({PCA_COMPONENTS})]")

    return df_final


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run_embedding_pipeline()