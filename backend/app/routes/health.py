"""
Health check route for GradeSense API.
"""

from fastapi import APIRouter
from app.config import API_VERSION
from app.schemas import HealthResponse
from app.services.data_service import is_dataset_available
from app.services.model_service import get_models_availability

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return system operational status and data/model availability."""
    dataset_ok = is_dataset_available()
    models_status = get_models_availability()

    return HealthResponse(
        status="ok",
        dataset_available=dataset_ok,
        models_available=models_status,
        version=API_VERSION,
    )
