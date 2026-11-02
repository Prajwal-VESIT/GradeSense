"""
Prediction endpoints for GradeSense API.
Provides single-student and batch predictions across both scenarios.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    ScenarioEnum,
)
from app.services.model_service import is_model_available
from app.services.prediction_service import predict_single, predict_batch

router = APIRouter(prefix="", tags=["Predictions"])


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Generate student final grade prediction for Scenario A or Scenario B.

    Scenario A (Early-Performance): Predicts G3 without G1 or G2.
    Scenario B (Grade-Assisted): Predicts G3 incorporating G1 and G2.
    """
    scenario_str = request.scenario.value

    # Check model file exists
    if not is_model_available(scenario_str):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Trained model for scenario '{scenario_str}' is unavailable. "
                "Please run 'python src/train_models.py' before requesting predictions."
            ),
        )

    # Validate grade presence if grade_assisted
    if request.scenario == ScenarioEnum.grade_assisted:
        if request.features.G1 is None or request.features.G2 is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Features G1 and G2 are mandatory when using the 'grade_assisted' scenario.",
            )

    try:
        return predict_single(scenario=request.scenario, features=request.features)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(exc)}",
        )


@router.post("/predict/batch", response_model=BatchPredictionResponse)
def batch_predict(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """
    Generate predictions for a collection of student feature records (1 to 500).
    Processes each record independently and surfaces individual record errors.
    """
    scenario_str = request.scenario.value

    if not is_model_available(scenario_str):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Trained model for scenario '{scenario_str}' is unavailable. "
                "Please run 'python src/train_models.py' before requesting batch predictions."
            ),
        )

    try:
        return predict_batch(scenario=request.scenario, records=request.records)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch inference execution failed: {str(exc)}",
        )
