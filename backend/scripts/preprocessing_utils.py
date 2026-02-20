import re
import numpy as np
import pandas as pd



def replace_negative_ones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replaces -1 sentinel values with NaN (numeric) or 'Unknown' (categorical).
    Binarizes the Competitors column due to ~75% missingness.
    """
    df = df.copy()
    # Numeric: -1 → NaN (preserves valid imputation downstream)
    for col in ["Rating", "Founded"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").replace(-1, np.nan)

    # Categorical: -1 → "Unknown"
    for col in ["Headquarters", "Size", "Type of ownership", "Industry", "Sector", "Revenue"]:
        df[col] = df[col].astype(str).replace("-1", "Unknown")

    # Unify Revenue unknown labels
    df["Revenue"] = df["Revenue"].replace("Unknown / Non-Applicable", "Unknown")

    # Competitors: too sparse (~75% missing) → binarize
    df["has_competitors"] = (df["Competitors"] != "-1").astype(int)
    df = df.drop(columns=["Competitors"])

    return df

#2- JOB DESCRIPTION 

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

# 3. COMPANY NAME — remove rating 

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
    r"data scien":               "Data Scientist",
    r"data engineer":            "Data Engineer",
    r"data analyst":             "Data Analyst",
    r"machine learning|ml engineer": "ML Engineer",
    r"data modeler":             "Data Modeler",
    r"research scien":           "Research Scientist",
    r"business intel":           "BI Analyst",
    r"statistician":             "Statistician",
}
def parse_job_title(title: str) -> dict:
    """
    Cleans a job title and extracts seniority + core role in one pass.
    
    e.g. 'Sr Data Scientist - Bay Area, CA' → {
        'clean_title': 'sr data scientist',
        'seniority':   'Senior',
        'core_role':   'Data Scientist'
    }
    """
    if pd.isna(title):
        return {"clean_title": title, "seniority": "Mid-level", "core_role": "Other"}

    # Clean
    clean = re.sub(r"\s*[-–]\s*[A-Z][a-zA-Z\s,]+(?:[A-Z]{2})\s*$", "", title)
    clean = clean.lower().strip()
    clean = re.sub(r"[^a-z0-9\s\-/]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    # Extract seniority
    seniority = "Mid-level"
    for pattern, label in SENIORITY_MAP.items():
        if re.search(pattern, clean):
            seniority = label
            break

    # Extract core role
    core_role = "Other"
    for pattern, role in ROLE_MAP.items():
        if re.search(pattern, clean):
            core_role = role
            break

    return {"clean_title": clean, "seniority": seniority, "core_role": core_role}

# 5. SALARY — audit + parse to numeric midpoint

def process_salary(df: pd.DataFrame, column_name: str, audit: bool = True) -> pd.Series:
    """
    Audits and parses salary strings into float midpoints.
    '$137K-$171K (Glassdoor est.)' → 154000.0
    """
    if audit:
        unexpected_pattern = r"[^0-9\$KkMmBb\-\s\.\(\)a-zA-Z]"
        million_rows = df[df[column_name].str.contains(r'M', na=False, case=False)]
        billion_rows = df[df[column_name].str.contains(r'B', na=False, case=False)]
        strange_rows = df[df[column_name].str.contains(unexpected_pattern, na=False)]
        print(f"--- Salary Audit: '{column_name}' ---")
        print(f"  Total rows            : {len(df)}")
        print(f"  Rows with M (millions): {len(million_rows)}")
        print(f"  Rows with B (billions): {len(billion_rows)}")
        print(f"  Rows with odd symbols : {len(strange_rows)}")
        if not strange_rows.empty:
            print(f"  Examples: {strange_rows[column_name].head(3).values}")
        print()

    def _parse(salary_str: str) -> float | None:
        if not isinstance(salary_str, str) or salary_str.lower() == "nan":
            return None
        try:
            multiplier = 1_000_000 if "M" in salary_str.upper() else 1_000
            numbers = re.findall(r"\d+\.?\d*", salary_str)
            if len(numbers) >= 2:
                return (float(numbers[0]) + float(numbers[1])) * multiplier / 2
            elif len(numbers) == 1:
                return float(numbers[0]) * multiplier
        except Exception:
            pass
        return None

    return df[column_name].apply(_parse)


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


# 8. LOCATION & HEADQUARTERS — parse + engineer binary features

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


# 9. TYPE OF OWNERSHIP — group and encode

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