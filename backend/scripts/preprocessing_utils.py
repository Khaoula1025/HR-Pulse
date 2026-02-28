import re
import numpy as np
import pandas as pd

# 1. replace -1 sentinels with NaN (numeric) or 'Unknown' (categorical)
def replace_negative_ones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replaces -1 sentinel values with NaN (numeric) or 'Unknown' (categorical).
    Binarizes the Competitors column due to ~75% missingness.
    """
    df = df.copy()

    # Numeric: -1 → NaN
    for col in ["Rating", "Founded"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").replace(-1, np.nan)

    # Categorical: -1 → "Unknown"
    for col in ["Headquarters", "Size", "Type of ownership", "Industry", "Sector", "Revenue"]:
        df[col] = df[col].astype(str).replace("-1", "Unknown")

    # Unify Revenue unknown labels
    df["Revenue"] = df["Revenue"].replace("Unknown / Non-Applicable", "Unknown")

    # Competitors: ~75% missing → binarize
    df["has_competitors"] = (df["Competitors"] != "-1").astype(int)
    df = df.drop(columns=["Competitors"])

    return df

# 2. JOB DESCRIPTION — embedding-ready cleaning
EEO_CUTOFF_PATTERNS = [
    # Slash variants
    r"is an (eeo|affirmative action)\s*[/\\]",
    r"eeo\s*[/\\]\s*(aa|affirmative action)",
    r"equal opportunity\s*[/\\]\s*affirmative action",
    r"equal opportunity and affirmative action employer",
    r"eeo\s*/\s*minorities",
    r"are equal opportunity\s*/?\s*affirmative",
    # Standard EEO / legal
    r"equal opportunity\/?affirmative action employer",
    r"affirmative action\/?equal opportunity employer",
    r"proud to be an (equal opportunity|affirmative action)",
    r"is an equal opportunity",
    r"we are an equal opportunity employer",
    r"equal opportunity employer",
    r"equal employment opportunity",
    r"provides equal employment opportunities",
    r"eeo law poster",
    r"we do not discriminate",
    r"if you have a disability under the americans with disability",
    r"applicants and employees are considered for positions",
    r"all qualified applicants will receive consideration for employment",
    r"committed to accommodating persons with disabilities",
    r"affirmative action by covered prime contractors",
    # Privacy
    r"california residents,?\s*please follow this link",
    r"california consumer privacy act",
    r"\bCCPA\b",
    # Company branding
    r"who we are\b",
    r"our culture is shaped by",
    r"our core values\b",
    r"about us\s*:",
    r"headquartered in .{0,60}(is|,) (a|the) (global|world|leading|premier|largest)",
    # Recruiting noise
    r"earn a referral bonus",
    r"does not accept (nor respond to )?unsolicited resumes",
    r"unsolicited resumes from (search firm|vendor|recruit)",
    r"not responsible for any fees related to unsolicited resumes",
    # Artifacts
    r"SDL\d{4}",
    r"req #\s*:?\s*[A-Z0-9]+",
    r"from complexity to clarity",
    # Benefits fluff
    r"work.?life balance and encourage",
    r"comprehensive benefits package",
]


def clean_for_embedding(text: str) -> str:
    """
    Minimal cleaning for job descriptions destined for HuggingFace embedding.
    Preserves linguistic structure; removes only technical noise and boilerplate.
    """
    if pd.isna(text):
        return ""

    # Remove XML/HTML artifacts
    text = re.sub(r"<!\[CDATA\[.*?\]\]>", " ", text, flags=re.DOTALL)
    text = re.sub(r"\]\]>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove URLs and emails
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove non-ASCII characters
    text = text.encode("ascii", errors="ignore").decode()

    # Cut at earliest boilerplate trigger
    earliest_cut = len(text)
    for pattern in EEO_CUTOFF_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            earliest_cut = min(earliest_cut, match.start())
    text = text[:earliest_cut].strip()

    # Remove duplicate paragraphs (Glassdoor scraping artifact)
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    seen = []
    for p in paragraphs:
        if p not in seen:
            seen.append(p)
    text = " ".join(seen)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text

# 3. COMPANY NAME — strip embedded Glassdoor rating
def clean_company_name(name: str) -> str:
    """'Healthfirst\\n3.1' → 'Healthfirst'"""
    if pd.isna(name):
        return name
    return name.split("\n")[0].strip()

# 4. JOB TITLE — normalize + extract structured features
SENIORITY_MAP = {
    r"\bsr\.?\b|\bsenior\b":       "Senior",
    r"\bjr\.?\b|\bjunior\b":       "Junior",
    r"\blead\b|\bstaff\b":         "Lead",
    r"\bprincipal\b":              "Principal",
    r"\bhead\b|\bdirector\b":      "Director",
    r"\bvp\b|\bvice president\b":  "VP",
    r"\bmanager\b|\bmgr\.?\b":     "Manager",
    r"\bentry[\s-]level\b":        "Junior",
}

ROLE_MAP = {
    r"data scien":                   "Data Scientist",
    r"data engineer":                "Data Engineer",
    r"data analyst":                 "Data Analyst",
    r"machine learning|ml engineer": "ML Engineer",
    r"data modeler":                 "Data Modeler",
    r"research scien":               "Research Scientist",
    r"business intel":               "BI Analyst",
    r"statistician":                 "Statistician",
}


def parse_job_title(title: str) -> dict:
    """
    Cleans a job title and extracts seniority + core role in one pass.

    Returns a dict with three keys:
      - job_title  : cleaned, lowercased title (used for embeddings if needed)
      - seniority  : seniority level extracted from raw title
      - core_role  : standardized role category (8 categories + 'Other')

    Keeping job_title and core_role as separate columns is intentional:
      - job_title  → too high cardinality (169 unique) for direct encoding;
                     useful only as text input for embeddings
      - core_role  → 8 clean categories, directly encodable as a feature
    """
    if pd.isna(title):
        return {"job_title": title, "seniority": "Mid-level", "core_role": "Other"}

    # Extract seniority from RAW title before lowercasing/cleaning
    seniority = "Mid-level"
    for pattern, label in SENIORITY_MAP.items():
        if re.search(pattern, title, flags=re.IGNORECASE):
            seniority = label
            break

    # Clean title
    clean = re.sub(r"\s*[-–]\s*[A-Z][a-zA-Z\s,]+(?:[A-Z]{2})\s*$", "", title)
    clean = clean.lower().strip()
    clean = re.sub(r"[^a-z0-9\s\-/]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    # Extract core role from cleaned title
    core_role = "Other"
    for pattern, role in ROLE_MAP.items():
        if re.search(pattern, clean):
            core_role = role
            break

    return {"job_title": clean, "seniority": seniority, "core_role": core_role}

# 5. SALARY — parse string to numeric midpoint
def process_salary(salary_str: str) -> float | None:
    """
    Parses a salary string into a float midpoint.
    Handles K (thousands) and M (millions) multipliers correctly:
    M multiplier is only applied when K is absent to avoid the
    '$145K-$225K(Employer est.)' → $185,000,000 bug.

    Examples:
        '$137K-$171K (Glassdoor est.)' → 154000.0
        '$1.2M-$1.5M (Glassdoor est.)' → 1350000.0
        '$145K-$225K(Employer est.)'   → 185000.0
    """
    if not isinstance(salary_str, str) or salary_str.lower() == "nan":
        return None
    try:
        upper = salary_str.upper()
        if "M" in upper and "K" not in upper:
            multiplier = 1_000_000
        else:
            multiplier = 1_000

        numbers = re.findall(r"\d+\.?\d*", salary_str)
        if len(numbers) >= 2:
            return (float(numbers[0]) + float(numbers[1])) * multiplier / 2
        elif len(numbers) == 1:
            return float(numbers[0]) * multiplier
        return None
    except Exception:
        return None

# 6. SIZE — ordinal encoding
SIZE_ORDINAL = {
    "1 to 50 employees":       1,
    "51 to 200 employees":     2,
    "201 to 500 employees":    3,
    "501 to 1000 employees":   4,
    "1001 to 5000 employees":  5,
    "5001 to 10000 employees": 6,
    "10000+ employees":        7,
    "Unknown":                 np.nan,
}


def encode_size(size: str) -> tuple:
    """
    Returns (ordinal_rank, is_top_size).
    is_top_size = 1 for '10000+' (open-ended, no honest midpoint).
    """
    size = str(size).strip()
    ordinal = SIZE_ORDINAL.get(size, np.nan)
    is_top  = 1 if size == "10000+ employees" else 0
    return ordinal, is_top

# 7. REVENUE — ordinal encoding
REVENUE_ORDINAL = {
    "Less than $1 million (USD)":        1,
    "$1 to $5 million (USD)":            2,
    "$5 to $10 million (USD)":           3,
    "$10 to $25 million (USD)":          4,
    "$25 to $50 million (USD)":          5,
    "$50 to $100 million (USD)":         6,
    "$100 to $500 million (USD)":        7,
    "$500 million to $1 billion (USD)":  8,
    "$1 to $2 billion (USD)":            9,
    "$2 to $5 billion (USD)":            10,
    "$5 to $10 billion (USD)":           11,
    "$10+ billion (USD)":                12,
    "Unknown":                           np.nan,
}


def encode_revenue(revenue: str) -> tuple:
    """
    Returns (ordinal_rank, is_top_revenue).
    is_top_revenue = 1 for '$10+ billion' (open-ended, no honest midpoint).
    """
    revenue = str(revenue).strip()
    ordinal = REVENUE_ORDINAL.get(revenue, np.nan)
    is_top  = 1 if revenue == "$10+ billion (USD)" else 0
    return ordinal, is_top

# 8. LOCATION & HEADQUARTERS
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC"
}


def parse_location(loc: str) -> tuple:
    """'New York, NY' → ('New York', 'NY')"""
    if pd.isna(loc) or loc in ("Unknown", "-1"):
        return np.nan, np.nan
    parts = [p.strip() for p in loc.split(",")]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return parts[0], np.nan

# 9. TYPE OF OWNERSHIP
OWNERSHIP_MAP = {
    "Company - Private":              "Private",
    "Company - Public":               "Public",
    "Subsidiary or Business Segment": "Private",
    "Private Practice / Firm":        "Private",
    "Nonprofit Organization":         "Nonprofit",
    "Government":                     "Government",
    "College / University":           "Government",
    "Hospital":                       "Nonprofit",
    "Self-employed":                  "Other",
    "Contract":                       "Other",
    "Other Organization":             "Other",
    "Unknown":                        "Unknown",
}

# 10. OUTLIER & NULL HANDLING
def handle_outliers_and_nulls(
    df: pd.DataFrame,
    iqr_multiplier: float = 1.5,
    z_threshold: float = 3.0,
) -> pd.DataFrame:
    """
    Handles outliers and missing values — call at the end of the pipeline
    after all columns have been created.

    Outlier strategy:
      - Salary    : winsorized at IQR bounds
      - Rating    : z-score clip at ±3 std (valid range 0–5)
      - Founded   : IQR winsorize (very old years valid but distorting)

    Null strategy:
      - Numeric / ordinal  → median imputation
      - Categorical        → fill with 'Unknown'
    """
    df = df.copy()

    def iqr_bounds(series: pd.Series):
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        return Q1 - iqr_multiplier * IQR, Q3 + iqr_multiplier * IQR

    # ------------------------------------------------------------------
    # 1. SALARY — drop nulls then winsorize
    # ------------------------------------------------------------------
    if "Salary" in df.columns:
        nulls = df["Salary"].isna().sum()
        if nulls > 0:
            df = df.dropna(subset=["Salary"])

        lower, upper = iqr_bounds(df["Salary"])
        df["Salary"] = df["Salary"].clip(lower=lower, upper=upper)

    # ------------------------------------------------------------------
    # 2. RATING — z-score clip then median impute
    # ------------------------------------------------------------------
    if "Rating" in df.columns:
        valid_rating = df["Rating"].dropna()
        if len(valid_rating) > 1:
            mean_r, std_r = valid_rating.mean(), valid_rating.std()
            df["Rating"] = df["Rating"].clip(
                lower=mean_r - z_threshold * std_r,
                upper=mean_r + z_threshold * std_r,
            )
        df["Rating"] = df["Rating"].fillna(df["Rating"].median())

    # ------------------------------------------------------------------
    # 3. FOUNDED — IQR winsorize then median impute
    # ------------------------------------------------------------------
    if "Founded" in df.columns:
        valid_founded = df["Founded"].dropna()
        if len(valid_founded) > 1:
            lower_f, upper_f = iqr_bounds(valid_founded)
            df["Founded"] = df["Founded"].clip(lower=lower_f, upper=upper_f)
        df["Founded"] = df["Founded"].fillna(df["Founded"].median())

    # ------------------------------------------------------------------
    # 4. ORDINAL FEATURES — median impute
    # ------------------------------------------------------------------
    for col in ["size_ordinal", "revenue_ordinal"]:
        if col in df.columns and df[col].isna().sum() > 0:
            df[col] = df[col].fillna(df[col].median())

    # ------------------------------------------------------------------
    # 5. CATEGORICAL FEATURES — fill with 'Unknown'
    # ------------------------------------------------------------------
    cat_cols = ["job_state", "hq_state", "type_of_ownership",
                "Sector", "seniority", "core_role"]
    for col in cat_cols:
        if col in df.columns and df[col].isna().sum() > 0:
            df[col] = df[col].fillna("Unknown")

    return df