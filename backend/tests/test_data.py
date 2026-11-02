"""
Unit tests for data loading, preprocessing, and leakage prevention.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ensure src and backend are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from src.data_preprocessing import (
    load_data,
    prepare_data,
    build_preprocessor,
    TARGET,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    GRADE_FEATURES,
)


def test_dataset_loads_correctly():
    """Verify student-mat.csv loads with 395 rows and 33 columns."""
    df = load_data()
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 395
    assert df.shape[1] == 33


def test_target_variable_exists_and_valid():
    """Verify G3 exists, is non-null, and all values lie in [0, 20]."""
    df = load_data()
    assert TARGET in df.columns
    assert df[TARGET].isnull().sum() == 0
    assert df[TARGET].min() >= 0
    assert df[TARGET].max() <= 20


def test_feature_lists_exclude_target():
    """Ensure G3 is never present in numeric or categorical feature lists."""
    assert TARGET not in NUMERIC_FEATURES
    assert TARGET not in CATEGORICAL_FEATURES
    assert TARGET not in GRADE_FEATURES


def test_prepare_data_splits_and_leakage():
    """Verify train/test sets do not overlap and no target leakage occurs."""
    df = load_data()
    data = prepare_data(df)

    assert "early_performance" in data
    assert "grade_assisted" in data

    for sc_name, sc_data in data.items():
        X_train = sc_data["X_train"]
        X_test = sc_data["X_test"]
        y_train = sc_data["y_train"]
        y_test = sc_data["y_test"]

        # 80/20 split check
        assert len(X_train) == 316
        assert len(X_test) == 79
        assert len(y_train) == 316
        assert len(y_test) == 79

        # Target must NOT be in feature columns
        assert TARGET not in X_train.columns
        assert TARGET not in X_test.columns

        # Verify no index overlap between train and test
        assert len(set(X_train.index).intersection(set(X_test.index))) == 0

        # Scenario A must NOT contain G1 or G2
        if sc_name == "early_performance":
            assert "G1" not in X_train.columns
            assert "G2" not in X_train.columns


def test_preprocessor_pipeline_transformation():
    """Verify ColumnTransformer fits on train and transforms without NaN."""
    df = load_data()
    data = prepare_data(df)
    sc = data["early_performance"]

    preprocessor = build_preprocessor(sc["numeric_cols"], sc["categorical_cols"])
    X_train_trans = preprocessor.fit_transform(sc["X_train"])
    X_test_trans = preprocessor.transform(sc["X_test"])

    assert not np.isnan(X_train_trans).any()
    assert not np.isnan(X_test_trans).any()
    assert X_train_trans.shape[0] == 316
    assert X_test_trans.shape[0] == 79
