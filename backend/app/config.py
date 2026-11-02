"""
Configuration module for the GradeSense backend application.

Defines paths, CORS settings, and API metadata used throughout the app.
"""

from pathlib import Path
from typing import List

# ──────────────────────────────────────────────
# Directory layout
# ──────────────────────────────────────────────
# backend/ lives one level below the project root
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent  # => GradeSense/
BACKEND_DIR: Path = BASE_DIR / "backend"
DATA_DIR: Path = BASE_DIR / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
MODELS_DIR: Path = BASE_DIR / "models"
OUTPUTS_DIR: Path = BASE_DIR / "outputs"
FIGURES_DIR: Path = OUTPUTS_DIR / "figures"

# Dataset filename
DATASET_FILENAME: str = "student-mat.csv"
DATASET_PATH: Path = RAW_DATA_DIR / DATASET_FILENAME

# Model filenames (saved by the training notebooks)
MODEL_FILENAMES: dict = {
    "early_performance": "early_performance_pipeline.joblib",
    "grade_assisted": "grade_assisted_pipeline.joblib",
}

# Output artefact filenames
MODEL_COMPARISON_FILE: str = "model_comparison.json"
MODEL_METADATA_FILE: str = "model_metadata.json"
ERROR_ANALYSIS_FILE: str = "error_analysis.json"
FEATURE_IMPORTANCE_FILE: str = "feature_importance.json"

# ──────────────────────────────────────────────
# CORS
# ──────────────────────────────────────────────
CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ──────────────────────────────────────────────
# API metadata
# ──────────────────────────────────────────────
API_TITLE: str = "GradeSense API"
API_DESCRIPTION: str = (
    "Student Performance Prediction API — "
    "predicts final grades (G3) on the UCI Student Performance dataset."
)
API_VERSION: str = "1.0.0"
