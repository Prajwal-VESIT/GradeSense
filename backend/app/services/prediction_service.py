"""
Prediction service for GradeSense backend.
Transforms student features, executes inference with the loaded pipeline,
and returns structured predictions and interpretability summaries.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from app.schemas import (
    ScenarioEnum,
    StudentFeatures,
    PredictionResponse,
    BatchPredictionResult,
    BatchPredictionError,
    BatchPredictionResponse,
)
from app.services.model_service import load_model_pipeline, get_model_metadata

logger = logging.getLogger(__name__)

# Cache loaded pipelines in memory
_PIPELINE_CACHE: Dict[str, Any] = {}


def get_cached_pipeline(scenario: str) -> Any:
    """Retrieve or load cached pipeline for a given scenario."""
    if scenario not in _PIPELINE_CACHE:
        _PIPELINE_CACHE[scenario] = load_model_pipeline(scenario)
    return _PIPELINE_CACHE[scenario]


def get_grade_category(grade: float) -> str:
    """
    Classify grade (0-20 scale) according to Portuguese secondary education standards:
      16-20: Excellent / Distinction
      14-15: Good
      12-13: Satisfactory
      10-11: Sufficient / Pass
      0-9:   Insufficient / Fail
    """
    rounded = round(grade, 1)
    if rounded >= 16.0:
        return "Excellent (Distinction)"
    elif rounded >= 14.0:
        return "Good"
    elif rounded >= 12.0:
        return "Satisfactory"
    elif rounded >= 10.0:
        return "Sufficient (Pass)"
    else:
        return "Insufficient (Fail)"


def generate_interpretation(
    grade: float,
    scenario: str,
    features: StudentFeatures,
    best_model_name: str,
) -> str:
    """Generate a cautious, data-supported interpretation for the prediction."""
    category = get_grade_category(grade)
    rounded = round(grade, 1)

    if scenario == "early_performance":
        scenario_desc = (
            "This estimate is produced under Scenario A (Early-Performance Prediction), "
            "evaluating demographic, family, study habit, and attendance proxies without "
            "relying on term grades."
        )
    else:
        g1 = features.G1 if features.G1 is not None else "N/A"
        g2 = features.G2 if features.G2 is not None else "N/A"
        scenario_desc = (
            f"This estimate is produced under Scenario B (Grade-Assisted Prediction), "
            f"leveraging earlier term assessments (G1={g1}, G2={g2}) along with background attributes."
        )

    disclaimer = (
        "Note: This numerical projection reflects historical cohort patterns and is not a "
        "guaranteed academic outcome or a measure of intrinsic ability."
    )

    return (
        f"The {best_model_name} model projects an estimated final grade of {rounded}/20 ({category}). "
        f"{scenario_desc} {disclaimer}"
    )


def predict_single(scenario: ScenarioEnum, features: StudentFeatures) -> PredictionResponse:
    """
    Execute single student prediction.
    """
    scenario_str = scenario.value
    pipeline = get_cached_pipeline(scenario_str)
    meta = get_model_metadata().get(scenario_str, {})
    best_model_name = meta.get("best_model", "Trained Regressor")
    metrics_summary = meta.get("models", {}).get(best_model_name, {})

    # Convert Pydantic features to DataFrame
    data_dict = features.model_dump()
    # In early_performance, ensure G1 and G2 are excluded
    if scenario_str == "early_performance":
        data_dict.pop("G1", None)
        data_dict.pop("G2", None)

    input_df = pd.DataFrame([data_dict])

    raw_pred = float(pipeline.predict(input_df)[0])
    # Clamp to valid documented grade bounds [0, 20]
    clamped_grade = max(0.0, min(20.0, raw_pred))

    category = get_grade_category(clamped_grade)
    interpretation = generate_interpretation(
        grade=clamped_grade,
        scenario=scenario_str,
        features=features,
        best_model_name=best_model_name,
    )

    return PredictionResponse(
        predicted_grade=round(clamped_grade, 2),
        grade_category=category,
        scenario=scenario_str,
        model_used=best_model_name,
        interpretation=interpretation,
        metrics_summary={
            "MAE": metrics_summary.get("test_MAE", 0.0),
            "RMSE": metrics_summary.get("test_RMSE", 0.0),
            "R2": metrics_summary.get("test_R2", 0.0),
        } if metrics_summary else None,
        input_summary=data_dict,
    )


def predict_batch(
    scenario: ScenarioEnum, records: List[StudentFeatures]
) -> BatchPredictionResponse:
    """
    Execute batch predictions for multiple student records.
    """
    scenario_str = scenario.value
    pipeline = get_cached_pipeline(scenario_str)

    predictions: List[BatchPredictionResult] = []
    errors: List[BatchPredictionError] = []

    for idx, record in enumerate(records):
        try:
            # Validate G1, G2 presence if grade_assisted
            if scenario_str == "grade_assisted" and (record.G1 is None or record.G2 is None):
                raise ValueError("G1 and G2 period grades are required for grade_assisted scenario.")

            data_dict = record.model_dump()
            if scenario_str == "early_performance":
                data_dict.pop("G1", None)
                data_dict.pop("G2", None)

            input_df = pd.DataFrame([data_dict])
            pred_val = float(pipeline.predict(input_df)[0])
            clamped = max(0.0, min(20.0, pred_val))

            predictions.append(
                BatchPredictionResult(
                    index=idx,
                    predicted_grade=round(clamped, 2),
                    grade_category=get_grade_category(clamped),
                )
            )
        except Exception as exc:
            logger.error("Error predicting record %d: %s", idx, exc)
            errors.append(BatchPredictionError(index=idx, error=str(exc)))

    return BatchPredictionResponse(
        scenario=scenario_str,
        total=len(records),
        successful=len(predictions),
        failed=len(errors),
        predictions=predictions,
        errors=errors,
    )
