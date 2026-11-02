"""
Pydantic schemas for request/response validation across the GradeSense API.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────
class ScenarioEnum(str, Enum):
    """Prediction scenario selector."""
    early_performance = "early_performance"
    grade_assisted = "grade_assisted"


# ──────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────
class HealthResponse(BaseModel):
    """Response for the health-check endpoint."""
    status: str = Field(..., description="API health status")
    dataset_available: bool = Field(..., description="Whether the dataset CSV is found")
    models_available: Dict[str, bool] = Field(
        ..., description="Per-scenario availability of trained model files"
    )
    version: str = Field(..., description="API version string")


# ──────────────────────────────────────────────
# Dataset / Data exploration
# ──────────────────────────────────────────────
class ColumnInfo(BaseModel):
    """Metadata for a single column."""
    name: str
    dtype: str
    missing: int
    unique: int


class DatasetSummary(BaseModel):
    """High-level summary of the loaded dataset."""
    n_rows: int
    n_cols: int
    columns: List[ColumnInfo]
    summary_stats: Dict[str, Any]


class PaginatedRecords(BaseModel):
    """Paginated dataset records."""
    page: int
    page_size: int
    total_records: int
    total_pages: int
    records: List[Dict[str, Any]]


# ──────────────────────────────────────────────
# Analytics
# ──────────────────────────────────────────────
class QuartileInfo(BaseModel):
    """Quartile boundaries."""
    q1: float
    q2: float
    q3: float


class GradeDistribution(BaseModel):
    """Distribution statistics for the target variable G3."""
    grades: List[int]
    bins: Dict[str, int]
    mean: float
    median: float
    std: float
    min: int
    max: int
    quartiles: QuartileInfo


class CorrelationData(BaseModel):
    """Correlation matrix payload."""
    features: List[str]
    correlation_matrix: List[List[float]]
    method: str = "pearson"


class AnalyticalInsight(BaseModel):
    """A single analytical insight derived from the data."""
    category: str
    title: str
    description: str
    value: Optional[Any] = None
    chart_data: Optional[Dict[str, Any]] = None


class StatisticalTestResult(BaseModel):
    """Result of a statistical hypothesis test."""
    test_name: str
    description: str
    statistic: float
    p_value: float
    significant: bool
    interpretation: str


class FeatureImportanceEntry(BaseModel):
    """Importance score for a single feature."""
    feature: str
    importance: float
    rank: int


# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────
class ModelComparisonEntry(BaseModel):
    """Performance metrics for one model in one scenario."""
    model_name: str
    scenario: str
    cv_mae: Optional[float] = None
    test_mae: Optional[float] = None
    test_mse: Optional[float] = None
    test_rmse: Optional[float] = None
    test_r2: Optional[float] = None
    is_selected: bool = False


class ModelMetadata(BaseModel):
    """Metadata about the deployed model for a scenario."""
    scenario: str
    model_name: str
    features: List[str]
    metrics: Dict[str, float]
    training_info: Optional[Dict[str, Any]] = None


class ErrorAnalysisData(BaseModel):
    """Error analysis payload."""
    scenario: str
    residuals: Optional[List[float]] = None
    predictions: Optional[List[float]] = None
    actuals: Optional[List[float]] = None
    error_stats: Optional[Dict[str, float]] = None


# ──────────────────────────────────────────────
# Prediction – input features
# ──────────────────────────────────────────────

# Valid nominal values
_VALID_SCHOOLS = {"GP", "MS"}
_VALID_SEX = {"F", "M"}
_VALID_ADDRESS = {"U", "R"}
_VALID_FAMSIZE = {"LE3", "GT3"}
_VALID_PSTATUS = {"T", "A"}
_VALID_JOBS = {"teacher", "health", "services", "at_home", "other"}
_VALID_REASONS = {"home", "reputation", "course", "other"}
_VALID_GUARDIANS = {"mother", "father", "other"}
_VALID_BINARY = {"yes", "no"}


class StudentFeatures(BaseModel):
    """All student features accepted for prediction."""

    # Categorical / binary
    school: str = Field(..., description="Student's school: GP or MS")
    sex: str = Field(..., description="Student's sex: F or M")
    address: str = Field(..., description="Home address type: U or R")
    famsize: str = Field(..., description="Family size: LE3 or GT3")
    Pstatus: str = Field(..., description="Parent cohabitation status: T or A")
    Mjob: str = Field(..., description="Mother's job")
    Fjob: str = Field(..., description="Father's job")
    reason: str = Field(..., description="Reason to choose this school")
    guardian: str = Field(..., description="Student's guardian")
    schoolsup: str = Field(..., description="Extra educational support: yes/no")
    famsup: str = Field(..., description="Family educational support: yes/no")
    paid: str = Field(..., description="Extra paid classes: yes/no")
    activities: str = Field(..., description="Extra-curricular activities: yes/no")
    nursery: str = Field(..., description="Attended nursery school: yes/no")
    higher: str = Field(..., description="Wants higher education: yes/no")
    internet: str = Field(..., description="Internet access at home: yes/no")
    romantic: str = Field(..., description="In a romantic relationship: yes/no")

    # Numeric
    age: int = Field(..., ge=15, le=22, description="Student age (15-22)")
    Medu: int = Field(..., ge=0, le=4, description="Mother's education (0-4)")
    Fedu: int = Field(..., ge=0, le=4, description="Father's education (0-4)")
    traveltime: int = Field(..., ge=1, le=4, description="Travel time (1-4)")
    studytime: int = Field(..., ge=1, le=4, description="Study time (1-4)")
    failures: int = Field(..., ge=0, le=4, description="Past failures (0-4)")
    famrel: int = Field(..., ge=1, le=5, description="Family relationship quality (1-5)")
    freetime: int = Field(..., ge=1, le=5, description="Free time (1-5)")
    goout: int = Field(..., ge=1, le=5, description="Going out (1-5)")
    Dalc: int = Field(..., ge=1, le=5, description="Workday alcohol (1-5)")
    Walc: int = Field(..., ge=1, le=5, description="Weekend alcohol (1-5)")
    health: int = Field(..., ge=1, le=5, description="Health status (1-5)")
    absences: int = Field(..., ge=0, le=93, description="Absences (0-93)")

    # Optional – only used in grade_assisted scenario
    G1: Optional[int] = Field(None, ge=0, le=20, description="First period grade (0-20)")
    G2: Optional[int] = Field(None, ge=0, le=20, description="Second period grade (0-20)")

    # ── validators ──────────────────────────────
    @field_validator("school")
    @classmethod
    def validate_school(cls, v: str) -> str:
        if v not in _VALID_SCHOOLS:
            raise ValueError(f"school must be one of {_VALID_SCHOOLS}")
        return v

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: str) -> str:
        if v not in _VALID_SEX:
            raise ValueError(f"sex must be one of {_VALID_SEX}")
        return v

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        if v not in _VALID_ADDRESS:
            raise ValueError(f"address must be one of {_VALID_ADDRESS}")
        return v

    @field_validator("famsize")
    @classmethod
    def validate_famsize(cls, v: str) -> str:
        if v not in _VALID_FAMSIZE:
            raise ValueError(f"famsize must be one of {_VALID_FAMSIZE}")
        return v

    @field_validator("Pstatus")
    @classmethod
    def validate_pstatus(cls, v: str) -> str:
        if v not in _VALID_PSTATUS:
            raise ValueError(f"Pstatus must be one of {_VALID_PSTATUS}")
        return v

    @field_validator("Mjob", "Fjob")
    @classmethod
    def validate_jobs(cls, v: str) -> str:
        if v not in _VALID_JOBS:
            raise ValueError(f"Job must be one of {_VALID_JOBS}")
        return v

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if v not in _VALID_REASONS:
            raise ValueError(f"reason must be one of {_VALID_REASONS}")
        return v

    @field_validator("guardian")
    @classmethod
    def validate_guardian(cls, v: str) -> str:
        if v not in _VALID_GUARDIANS:
            raise ValueError(f"guardian must be one of {_VALID_GUARDIANS}")
        return v

    @field_validator(
        "schoolsup", "famsup", "paid", "activities",
        "nursery", "higher", "internet", "romantic",
    )
    @classmethod
    def validate_binary(cls, v: str) -> str:
        if v not in _VALID_BINARY:
            raise ValueError(f"Value must be one of {_VALID_BINARY}")
        return v


# ──────────────────────────────────────────────
# Prediction – request / response
# ──────────────────────────────────────────────
class PredictionRequest(BaseModel):
    """Single-student prediction request."""
    scenario: ScenarioEnum
    features: StudentFeatures

    @field_validator("features")
    @classmethod
    def validate_grade_fields(cls, v: StudentFeatures, info) -> StudentFeatures:
        """Ensure G1/G2 are provided when scenario is grade_assisted."""
        # info.data may not have 'scenario' yet during model_validator ordering,
        # so we do this check at the route level as well.
        return v


class PredictionResponse(BaseModel):
    """Response for a single prediction."""
    predicted_grade: float
    grade_category: str
    scenario: str
    model_used: str
    interpretation: str
    metrics_summary: Optional[Dict[str, float]] = None
    input_summary: Dict[str, Any]


class BatchPredictionRequest(BaseModel):
    """Batch prediction request – multiple students."""
    scenario: ScenarioEnum
    records: List[StudentFeatures] = Field(
        ..., min_length=1, max_length=500,
        description="List of student feature sets (1-500)",
    )


class BatchPredictionResult(BaseModel):
    """Result for one record in a batch."""
    index: int
    predicted_grade: float
    grade_category: str


class BatchPredictionError(BaseModel):
    """Error for one record in a batch."""
    index: int
    error: str


class BatchPredictionResponse(BaseModel):
    """Response for batch predictions."""
    scenario: str
    total: int
    successful: int
    failed: int
    predictions: List[BatchPredictionResult]
    errors: List[BatchPredictionError]
