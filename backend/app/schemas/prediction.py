from pydantic import BaseModel, Field


VALID_SKILLS = [
    "python", "sql", "spark", "aws", "azure", "machine_learning",
    "deep_learning", "tensorflow", "pytorch", "tableau", "java",
    "scala", "hadoop", "git", "linux", "docker",
]


class PredictRequest(BaseModel):
    # Company info
    rating:            float       = Field(..., ge=0.0, le=5.0,  description="Company Glassdoor rating (0-5)")
    founded:           int         = Field(..., ge=1800, le=2024, description="Year the company was founded")
    size_ordinal:      int         = Field(..., ge=1, le=8,       description="Company size bucket (1=<50, 8=10000+)")
    revenue_ordinal:   int         = Field(..., ge=1, le=9,       description="Revenue bucket (1=<1M, 9=10B+)")
    type_of_ownership: str         = Field(...,                   description="e.g. 'Private', 'Public', 'Nonprofit'")
    has_competitors:   int         = Field(..., ge=0, le=1,       description="1 if company has listed competitors")

    # Job location
    job_state:         str         = Field(..., min_length=2, max_length=2, description="US state code, e.g. 'CA'")
    is_at_hq:          int         = Field(default=0, ge=0, le=1, description="1 if job is at company HQ")
    hq_is_international: int       = Field(default=0, ge=0, le=1, description="1 if HQ is outside the US")

    # Role info
    sector:            str         = Field(...,                   description="Industry sector, e.g. 'Information Technology'")
    seniority:         str         = Field(...,                   description="'Junior', 'Mid', 'Senior', 'Lead', 'Manager'")
    core_role:         str         = Field(...,                   description="e.g. 'Data Scientist', 'Data Engineer', 'ML Engineer'")

    # Skills — list of skill names from VALID_SKILLS
    skills:            list[str]   = Field(default=[], description=f"Skills required. Valid values: {VALID_SKILLS}")

    model_config = {
        "json_schema_extra": {
            "example": {
                "rating": 4.2,
                "founded": 2005,
                "size_ordinal": 4,
                "revenue_ordinal": 5,
                "type_of_ownership": "Private",
                "has_competitors": 1,
                "job_state": "CA",
                "is_at_hq": 1,
                "hq_is_international": 0,
                "sector": "Information Technology",
                "seniority": "Senior",
                "core_role": "Data Scientist",
                "skills": ["python", "sql", "machine_learning", "spark", "aws"]
            }
        }
    }


class PredictResponse(BaseModel):
    predicted_salary: int
    range_min:        int
    range_max:        int
    currency:         str = "USD"
    skills_used:      list[str]
    input_summary:    dict