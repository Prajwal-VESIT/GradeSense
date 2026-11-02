"""
Unit tests for model training, metrics, persistence, and pipeline inference.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from src.data_preprocessing import load_data, prepare_data, build_preprocessor
from src.train_models import get_models, compute_metrics
from app.services.model_service import load_model_pipeline, is_model_available


def test_required_models_instantiation():
    """Verify all 6 regression models are instantiated properly."""
    models = get_models()
    expected = [
        "DummyRegressor",
        "LinearRegression",
        "Ridge",
        "RandomForest",
        "GradientBoosting",
        "HistGradientBoosting",
    ]
    for m in expected:
        assert m in models


def test_metric_computation():
    """Verify MAE, MSE, RMSE, R2 are calculated correctly."""
    y_true = np.array([10.0, 12.0, 14.0, 16.0])
    y_pred = np.array([10.0, 11.0, 15.0, 16.0])

    metrics = compute_metrics(y_true, y_pred)
    assert metrics["MAE"] == 0.5
    assert metrics["MSE"] == 0.5
    assert metrics["RMSE"] == pytest.approx(np.sqrt(0.5), 0.001)
    assert metrics["R2"] > 0.8


def test_saved_model_reload_and_prediction():
    """Verify saved models exist, reload properly, and predict on valid records."""
    assert is_model_available("early_performance")
    assert is_model_available("grade_assisted")

    pipe_early = load_model_pipeline("early_performance")
    pipe_assisted = load_model_pipeline("grade_assisted")

    df = load_data()
    data = prepare_data(df)

    # Test early performance prediction
    sample_early = data["early_performance"]["X_test"].iloc[:5]
    preds_early = pipe_early.predict(sample_early)
    assert len(preds_early) == 5
    assert all(isinstance(p, (float, np.floating)) for p in preds_early)

    # Test grade assisted prediction
    sample_assisted = data["grade_assisted"]["X_test"].iloc[:5]
    preds_assisted = pipe_assisted.predict(sample_assisted)
    assert len(preds_assisted) == 5
    assert all(isinstance(p, (float, np.floating)) for p in preds_assisted)
