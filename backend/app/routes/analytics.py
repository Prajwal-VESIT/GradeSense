"""
Analytics and statistical reporting routes for GradeSense API.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Query

from app.schemas import GradeDistribution, CorrelationData, AnalyticalInsight, StatisticalTestResult
from app.services.analytics_service import (
    get_analytical_insights,
    compute_statistical_tests,
)
from app.services.data_service import (
    get_grade_distribution,
    get_correlation_data,
    is_dataset_available,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/grades", response_model=GradeDistribution)
def get_grades() -> GradeDistribution:
    """Return G3 final grade distribution data, bins, quartiles, and summary stats."""
    if not is_dataset_available():
        raise HTTPException(status_code=404, detail="Dataset not available.")
    return get_grade_distribution()


@router.get("/correlations", response_model=CorrelationData)
def get_correlations(
    method: str = Query("pearson", pattern="^(pearson|spearman|kendall)$", description="Correlation method")
) -> CorrelationData:
    """Return numeric correlation matrix using Pearson, Spearman, or Kendall methods."""
    if not is_dataset_available():
        raise HTTPException(status_code=404, detail="Dataset not available.")
    return get_correlation_data(method=method)


@router.get("/insights", response_model=List[AnalyticalInsight])
def get_insights() -> List[AnalyticalInsight]:
    """Return deep data-driven analytical insights compiled from the cohort."""
    if not is_dataset_available():
        raise HTTPException(status_code=404, detail="Dataset not available.")
    return get_analytical_insights()


@router.get("/statistical-tests", response_model=List[StatisticalTestResult])
def get_statistical_tests() -> List[StatisticalTestResult]:
    """Return formal hypothesis test outcomes (Welch's t-test, ANOVA, Pearson)."""
    if not is_dataset_available():
        raise HTTPException(status_code=404, detail="Dataset not available.")
    return compute_statistical_tests()


@router.get("/statistics")
def get_statistics():
    """Return comprehensive descriptive statistics for each feature."""
    if not is_dataset_available():
        raise HTTPException(status_code=404, detail="Dataset not available.")
    from app.services.data_service import get_descriptive_stats
    return get_descriptive_stats()


@router.get("/feature-importance")
def get_feature_importance():
    """Return permutation feature importance data for both scenarios."""
    import pandas as pd
    from app.config import OUTPUTS_DIR
    res = {}
    for sc in ["early_performance", "grade_assisted"]:
        imp_path = OUTPUTS_DIR / f"feature_importance_{sc}.csv"
        if imp_path.exists():
            df_imp = pd.read_csv(imp_path)
            res[sc] = df_imp.to_dict(orient="records")
        else:
            res[sc] = []
    return res
