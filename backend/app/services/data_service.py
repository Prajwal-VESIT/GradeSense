"""
Data service — loads and queries the UCI Student Performance dataset.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.config import DATASET_PATH

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Dataset loading
# ──────────────────────────────────────────────
@lru_cache(maxsize=1)
def load_dataset() -> pd.DataFrame:
    """
    Load student-mat.csv from the raw data directory.

    Returns:
        pd.DataFrame with all columns from the CSV.

    Raises:
        FileNotFoundError: if the dataset file is missing.
    """
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_PATH}. "
            "Please place student-mat.csv in data/raw/."
        )

    # The UCI file uses semicolons as separators; fallback to comma if needed
    df = pd.read_csv(DATASET_PATH, sep=";")
    if df.shape[1] == 1:
        df = pd.read_csv(DATASET_PATH, sep=",")
    logger.info("Dataset loaded: %d rows, %d columns", len(df), len(df.columns))
    return df


def is_dataset_available() -> bool:
    """Check whether the dataset CSV exists on disk."""
    return DATASET_PATH.exists()


# ──────────────────────────────────────────────
# Summary & statistics
# ──────────────────────────────────────────────
def get_dataset_summary() -> Dict[str, Any]:
    """
    Return high-level metadata about the dataset.

    Returns a dict suitable for the DatasetSummary schema.
    """
    df = load_dataset()

    columns_info = []
    for col in df.columns:
        columns_info.append(
            {
                "name": col,
                "dtype": str(df[col].dtype),
                "missing": int(df[col].isna().sum()),
                "unique": int(df[col].nunique()),
            }
        )

    # Descriptive stats for numeric columns only
    summary_stats = df.describe().to_dict()
    # Convert numpy types to native Python types for JSON serialisation
    for col_key, stats in summary_stats.items():
        for stat_key, val in stats.items():
            if isinstance(val, (np.integer, np.int64)):
                summary_stats[col_key][stat_key] = int(val)
            elif isinstance(val, (np.floating, np.float64)):
                summary_stats[col_key][stat_key] = float(val)

    return {
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "columns": columns_info,
        "summary_stats": summary_stats,
    }


def get_descriptive_stats() -> Dict[str, Any]:
    """Full descriptive statistics for every column."""
    df = load_dataset()

    stats: Dict[str, Any] = {}
    for col in df.columns:
        col_stats: Dict[str, Any] = {
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isna().sum()),
            "unique": int(df[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_stats.update(
                {
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "median": float(df[col].median()),
                    "q1": float(df[col].quantile(0.25)),
                    "q3": float(df[col].quantile(0.75)),
                    "skew": float(df[col].skew()),
                    "kurtosis": float(df[col].kurtosis()),
                }
            )
        else:
            value_counts = df[col].value_counts().to_dict()
            col_stats["value_counts"] = {
                str(k): int(v) for k, v in value_counts.items()
            }
        stats[col] = col_stats

    return stats


# ──────────────────────────────────────────────
# Grade distribution
# ──────────────────────────────────────────────
def get_grade_distribution() -> Dict[str, Any]:
    """
    Compute the distribution of the target variable G3.

    Returns a dict matching the GradeDistribution schema.
    """
    df = load_dataset()
    g3 = df["G3"]

    # Bins: count of students per integer grade
    bins = g3.value_counts().sort_index()
    bins_dict = {str(int(k)): int(v) for k, v in bins.items()}

    return {
        "grades": g3.tolist(),
        "bins": bins_dict,
        "mean": float(g3.mean()),
        "median": float(g3.median()),
        "std": float(g3.std()),
        "min": int(g3.min()),
        "max": int(g3.max()),
        "quartiles": {
            "q1": float(g3.quantile(0.25)),
            "q2": float(g3.quantile(0.50)),
            "q3": float(g3.quantile(0.75)),
        },
    }


# ──────────────────────────────────────────────
# Correlation
# ──────────────────────────────────────────────
def get_correlation_data(method: str = "pearson") -> Dict[str, Any]:
    """
    Compute the correlation matrix for all numeric columns.

    Args:
        method: 'pearson', 'kendall', or 'spearman'.

    Returns a dict matching the CorrelationData schema.
    """
    df = load_dataset()
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr(method=method)

    return {
        "features": corr.columns.tolist(),
        "correlation_matrix": corr.values.tolist(),
        "method": method,
    }


# ──────────────────────────────────────────────
# Paginated records
# ──────────────────────────────────────────────
def get_sample_records(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Return paginated (and optionally filtered) dataset records.

    Args:
        page: 1-indexed page number.
        page_size: rows per page (max 100).
        search: free-text search across all columns.
        filters: column-level equality filters, e.g. {"school": "GP"}.

    Returns a dict matching the PaginatedRecords schema.
    """
    df = load_dataset().copy()

    # Apply column filters
    if filters:
        for col, val in filters.items():
            if col in df.columns:
                df = df[df[col].astype(str) == str(val)]

    # Apply free-text search
    if search:
        mask = df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(),
            axis=1,
        )
        df = df[mask]

    total_records = len(df)
    page_size = min(max(page_size, 1), 100)
    total_pages = max(1, (total_records + page_size - 1) // page_size)
    page = min(max(page, 1), total_pages)

    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]

    # Convert numpy types for JSON compatibility
    records = page_df.to_dict(orient="records")
    clean_records: List[Dict[str, Any]] = []
    for rec in records:
        clean: Dict[str, Any] = {}
        for k, v in rec.items():
            if isinstance(v, (np.integer, np.int64)):
                clean[k] = int(v)
            elif isinstance(v, (np.floating, np.float64)):
                clean[k] = float(v)
            else:
                clean[k] = v
        clean_records.append(clean)

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": total_pages,
        "records": clean_records,
    }
