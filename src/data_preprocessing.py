"""
GradeSense - Data Preprocessing Module
=======================================
This module handles downloading, loading, inspecting, and preprocessing the
UCI Student Performance dataset (student-mat.csv).

It builds scikit-learn ColumnTransformer pipelines for two scenarios:
  (A) Early-Performance  — predict G3 WITHOUT G1, G2 (prior grades)
  (B) Grade-Assisted     — predict G3 WITH G1, G2

Author : [Student Name]
Course : VESIT SEM VII — Data Science
"""

import os
import sys
import json
import zipfile
import io
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Path configuration — all paths relative to the project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"

# Ensure directories exist
for d in [DATA_RAW_DIR, DATA_PROCESSED_DIR, OUTPUTS_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATASET_URL = (
    "https://archive.ics.uci.edu/static/public/320/student+performance.zip"
)
RAW_CSV = DATA_RAW_DIR / "student-mat.csv"
TARGET = "G3"  # final grade (0-20)
RANDOM_STATE = 42

# All columns that exist in the dataset (from UCI documentation)
ALL_COLUMNS = [
    "school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
    "Mjob", "Fjob", "reason", "guardian", "traveltime", "studytime",
    "failures", "schoolsup", "famsup", "paid", "activities", "nursery",
    "higher", "internet", "romantic", "famrel", "freetime", "goout", "Dalc",
    "Walc", "health", "absences", "G1", "G2", "G3",
]

# Categorical features (binary yes/no and multi-class nominal)
CATEGORICAL_FEATURES = [
    "school", "sex", "address", "famsize", "Pstatus",
    "Mjob", "Fjob", "reason", "guardian",
    "schoolsup", "famsup", "paid", "activities", "nursery",
    "higher", "internet", "romantic",
]

# Numeric features (ordinal Likert-type scales and true numeric)
NUMERIC_FEATURES = [
    "age", "Medu", "Fedu", "traveltime", "studytime", "failures",
    "famrel", "freetime", "goout", "Dalc", "Walc", "health", "absences",
]

# Grade features used only in Scenario B
GRADE_FEATURES = ["G1", "G2"]


# ---------------------------------------------------------------------------
# Feature lists per scenario
# ---------------------------------------------------------------------------
def get_feature_lists():
    """Return feature lists for each scenario.

    Returns
    -------
    dict with keys 'early_performance' and 'grade_assisted', each mapping to
    sub-dicts with 'numeric' and 'categorical' feature name lists.
    """
    return {
        "early_performance": {
            "numeric": list(NUMERIC_FEATURES),         # no G1, G2
            "categorical": list(CATEGORICAL_FEATURES),
        },
        "grade_assisted": {
            "numeric": list(NUMERIC_FEATURES) + GRADE_FEATURES,  # includes G1, G2
            "categorical": list(CATEGORICAL_FEATURES),
        },
    }


# ---------------------------------------------------------------------------
# Dataset download
# ---------------------------------------------------------------------------
def download_dataset(force: bool = False) -> Path:
    """Download the UCI Student Performance dataset and extract student-mat.csv.

    Parameters
    ----------
    force : bool
        Re-download even if file already exists.

    Returns
    -------
    Path to the raw CSV file.
    """
    if RAW_CSV.exists() and not force:
        print(f"[INFO] Dataset already present at {RAW_CSV}")
        return RAW_CSV

    print(f"[INFO] Downloading dataset from {DATASET_URL} ...")
    try:
        resp = requests.get(DATASET_URL, timeout=60)
        resp.raise_for_status()
    except Exception as exc:
        msg = (
            f"[ERROR] Could not download the dataset: {exc}\n"
            f"Please manually download from:\n"
            f"  {DATASET_URL}\n"
            f"Extract 'student-mat.csv' into:\n"
            f"  {DATA_RAW_DIR}\n"
        )
        print(msg)
        raise RuntimeError(msg) from exc

    # The ZIP contains files at various levels (or nested inside student.zip)
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        target_name = None
        for name in zf.namelist():
            if name.endswith("student-mat.csv"):
                target_name = name
                break
        if target_name:
            csv_bytes = zf.read(target_name)
        elif "student.zip" in zf.namelist():
            inner_zf = zipfile.ZipFile(io.BytesIO(zf.read("student.zip")))
            for name in inner_zf.namelist():
                if name.endswith("student-mat.csv"):
                    target_name = name
                    break
            if target_name:
                csv_bytes = inner_zf.read(target_name)
            else:
                raise FileNotFoundError("student-mat.csv not found in inner student.zip")
        else:
            raise FileNotFoundError("student-mat.csv not found inside the ZIP")

        RAW_CSV.write_bytes(csv_bytes)
        print(f"[INFO] Saved {RAW_CSV}  ({len(csv_bytes):,} bytes)")

    return RAW_CSV


# ---------------------------------------------------------------------------
# Data loading & inspection
# ---------------------------------------------------------------------------
def load_data(csv_path: Path = RAW_CSV) -> pd.DataFrame:
    """Load student-mat.csv with the correct separator.

    The UCI CSV uses semicolons as delimiters, but comma-separated fallback is supported.
    """
    df = pd.read_csv(csv_path, sep=";")
    if df.shape[1] == 1:
        df = pd.read_csv(csv_path, sep=",")
    print(f"[INFO] Loaded {csv_path.name}: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


def inspect_data(df: pd.DataFrame) -> dict:
    """Print and return a summary inspection of the dataframe.

    Returns a dict with keys: shape, dtypes, missing, duplicates, describe.
    """
    report = {}

    # Shape
    report["shape"] = {"rows": int(df.shape[0]), "columns": int(df.shape[1])}
    print(f"\n--- Dataset Shape: {df.shape} ---")

    # Data types
    report["dtypes"] = df.dtypes.astype(str).to_dict()
    print(f"\n--- Data Types ---\n{df.dtypes}")

    # Missing values
    missing = df.isnull().sum()
    report["missing_values"] = missing[missing > 0].to_dict()
    print(f"\n--- Missing Values ---")
    if missing.sum() == 0:
        print("  No missing values found.")
    else:
        print(missing[missing > 0])

    # Duplicates
    n_dup = int(df.duplicated().sum())
    report["duplicates"] = n_dup
    print(f"\n--- Duplicates: {n_dup} ---")

    # Descriptive statistics (numeric only)
    desc = df.describe().to_dict()
    # Convert numpy types to native Python for JSON serialisation
    report["describe"] = {
        col: {k: float(v) for k, v in stats.items()} for col, stats in desc.items()
    }
    print(f"\n--- Descriptive Statistics ---\n{df.describe().T}")

    return report


# ---------------------------------------------------------------------------
# Build preprocessing pipeline (ColumnTransformer)
# ---------------------------------------------------------------------------
def build_preprocessor(numeric_cols: list, categorical_cols: list) -> ColumnTransformer:
    """Build a scikit-learn ColumnTransformer.

    Numeric pipeline  : median imputation  → standard scaling
    Categorical pipeline: most-frequent imputation → one-hot encoding

    Parameters
    ----------
    numeric_cols : list of str
    categorical_cols : list of str

    Returns
    -------
    ColumnTransformer ready for .fit() / .transform()
    """
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ],
        remainder="drop",  # drop any columns not listed
    )
    return preprocessor


# ---------------------------------------------------------------------------
# Prepare train / test splits for both scenarios
# ---------------------------------------------------------------------------
def prepare_data(df: pd.DataFrame, test_size: float = 0.20):
    """Split data into train/test and return feature matrices per scenario.

    Returns
    -------
    data : dict  keyed by scenario name, each containing:
        X_train, X_test, y_train, y_test, numeric_cols, categorical_cols, preprocessor
    """
    feature_lists = get_feature_lists()
    y = df[TARGET].values

    data = {}
    for scenario, cols in feature_lists.items():
        numeric_cols = cols["numeric"]
        categorical_cols = cols["categorical"]
        all_features = numeric_cols + categorical_cols

        X = df[all_features]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=RANDOM_STATE,
        )
        preprocessor = build_preprocessor(numeric_cols, categorical_cols)

        data[scenario] = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "numeric_cols": numeric_cols,
            "categorical_cols": categorical_cols,
            "preprocessor": preprocessor,
            "feature_names": all_features,
        }
        print(
            f"[INFO] Scenario '{scenario}': "
            f"train={X_train.shape[0]}, test={X_test.shape[0]}, "
            f"features={X_train.shape[1]}"
        )

    return data


# ---------------------------------------------------------------------------
# Save processed artefacts
# ---------------------------------------------------------------------------
def save_processed(df: pd.DataFrame, report: dict):
    """Save processed CSV and inspection report."""
    # Save clean CSV (original data, just with consistent format)
    processed_csv = DATA_PROCESSED_DIR / "student_mat_clean.csv"
    df.to_csv(processed_csv, index=False)
    print(f"[INFO] Saved processed CSV → {processed_csv}")

    # Save inspection report as JSON
    report_path = OUTPUTS_DIR / "preprocessing_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"[INFO] Saved preprocessing report → {report_path}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    """Run the full preprocessing pipeline."""
    print("=" * 60)
    print("GradeSense — Data Preprocessing Pipeline")
    print("=" * 60)

    # Step 1: Download (or locate) the dataset
    download_dataset()

    # Step 2: Load
    df = load_data()

    # Step 3: Inspect
    report = inspect_data(df)

    # Step 4: Save processed data & report
    save_processed(df, report)

    # Step 5: Quick sanity check — prepare splits (not saved, just verified)
    data = prepare_data(df)

    print("\n" + "=" * 60)
    print("Preprocessing complete ✓")
    print("=" * 60)
    return df, data


if __name__ == "__main__":
    main()
