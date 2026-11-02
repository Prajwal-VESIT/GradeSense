"""
Model service for GradeSense backend.
Handles loading model artifacts, comparison metrics, and metadata.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib

from app.config import (
    MODELS_DIR,
    OUTPUTS_DIR,
    MODEL_COMPARISON_FILE,
    MODEL_METADATA_FILE,
    MODEL_FILENAMES,
)

logger = logging.getLogger(__name__)


def get_model_file_path(scenario: str) -> Optional[Path]:
    """Find the path of the saved model pipeline for a given scenario."""
    # Check configured filename first, then common alternatives
    candidate_names = [
        MODEL_FILENAMES.get(scenario, ""),
        f"{scenario}_model.joblib",
        f"{scenario}_pipeline.joblib",
        f"best_model_{scenario}.joblib",
    ]
    for name in candidate_names:
        if name:
            p = MODELS_DIR / name
            if p.exists():
                return p
    return None


def is_model_available(scenario: str) -> bool:
    """Check if model pipeline artifact exists for a scenario."""
    return get_model_file_path(scenario) is not None


def get_models_availability() -> Dict[str, bool]:
    """Return availability dict for both scenarios."""
    return {
        "early_performance": is_model_available("early_performance"),
        "grade_assisted": is_model_available("grade_assisted"),
    }


def load_model_pipeline(scenario: str) -> Any:
    """Load and return the fitted scikit-learn pipeline for a scenario."""
    path = get_model_file_path(scenario)
    if not path or not path.exists():
        raise FileNotFoundError(
            f"Trained model for scenario '{scenario}' was not found in {MODELS_DIR}. "
            "Please run 'python src/train_models.py' to generate model artifacts."
        )
    logger.info("Loading model pipeline from %s", path)
    return joblib.load(path)


def get_model_comparison() -> List[Dict[str, Any]]:
    """Load model comparison data from outputs/model_comparison.json."""
    comp_path = OUTPUTS_DIR / MODEL_COMPARISON_FILE
    if not comp_path.exists():
        # Fallback if training hasn't been executed
        return []
    with open(comp_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_model_metadata() -> Dict[str, Any]:
    """Load model metadata from models/model_metadata.json."""
    meta_path = MODELS_DIR / MODEL_METADATA_FILE
    if not meta_path.exists():
        return {}
    with open(meta_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
