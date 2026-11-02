"""
Model comparison and metadata routes for GradeSense API.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException

from app.services.model_service import (
    get_model_comparison,
    get_model_metadata,
    get_models_availability,
)

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("/comparison")
def get_comparison() -> List[Dict[str, Any]]:
    """Return quantitative benchmark metrics (MAE, MSE, RMSE, R2) for all trained models."""
    comparison = get_model_comparison()
    if not comparison:
        raise HTTPException(
            status_code=404,
            detail="Model comparison artifacts not found. Please train models via 'python src/train_models.py'.",
        )
    return comparison


@router.get("/metadata")
def get_metadata() -> Dict[str, Any]:
    """Return metadata about selected models, hyperparameter configurations, and evaluation metrics."""
    metadata = get_model_metadata()
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Model metadata not found. Please train models via 'python src/train_models.py'.",
        )
    return metadata


@router.get("/error-analysis")
def get_error_analysis():
    """Return detailed error diagnostics by grade range and large error cases."""
    import json
    from app.config import OUTPUTS_DIR
    eval_path = OUTPUTS_DIR / "evaluation_results.json"
    if not eval_path.exists():
        raise HTTPException(status_code=404, detail="Evaluation results not found.")
    with open(eval_path, "r", encoding="utf-8") as f:
        return json.load(f)
