"""
GradeSense - Model Evaluation & Error Analysis
================================================
Loads saved models and test data, computes detailed evaluation metrics,
generates diagnostic plots, and analyses error patterns.

Author : [Student Name]
Course : VESIT SEM VII — Data Science
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.data_preprocessing import (
    download_dataset,
    load_data,
    prepare_data,
    PROJECT_ROOT,
    OUTPUTS_DIR,
    MODELS_DIR,
    RANDOM_STATE,
)

FIGURES_DIR = OUTPUTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)


# ---------------------------------------------------------------------------
# Metric computation
# ---------------------------------------------------------------------------
def compute_metrics(y_true, y_pred) -> dict:
    """Return MAE, MSE, RMSE, R² as a dict."""
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    return {
        "MAE": round(float(mae), 4),
        "MSE": round(float(mse), 4),
        "RMSE": round(float(rmse), 4),
        "R2": round(float(r2), 4),
    }


# ---------------------------------------------------------------------------
# Error analysis helpers
# ---------------------------------------------------------------------------
def error_by_grade_range(y_true, y_pred) -> pd.DataFrame:
    """Compute MAE per grade range bucket."""
    df = pd.DataFrame({"actual": y_true, "predicted": y_pred})
    df["residual"] = df["actual"] - df["predicted"]
    df["abs_error"] = df["residual"].abs()

    # Define grade ranges
    bins = [0, 5, 10, 15, 20]
    labels = ["0-5 (Fail)", "6-10 (Low)", "11-15 (Mid)", "16-20 (High)"]
    df["grade_range"] = pd.cut(df["actual"], bins=bins, labels=labels, include_lowest=True)

    summary = df.groupby("grade_range", observed=False).agg(
        count=("abs_error", "size"),
        mean_abs_error=("abs_error", "mean"),
        std_abs_error=("abs_error", "std"),
        mean_residual=("residual", "mean"),
    ).reset_index()
    return summary


def identify_large_errors(y_true, y_pred, threshold: float = 3.0) -> pd.DataFrame:
    """Find cases where the absolute error exceeds threshold."""
    df = pd.DataFrame({
        "actual": y_true,
        "predicted": np.round(y_pred, 2),
        "residual": np.round(y_true - y_pred, 2),
        "abs_error": np.round(np.abs(y_true - y_pred), 2),
    })
    large = df[df["abs_error"] > threshold].sort_values("abs_error", ascending=False)
    return large


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_actual_vs_predicted(scenario: str, y_true, y_pred, model_name: str):
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(y_true, y_pred, alpha=0.6, edgecolors="k", linewidths=0.3)
    lims = [min(y_true.min(), y_pred.min()) - 1, max(y_true.max(), y_pred.max()) + 1]
    ax.plot(lims, lims, "--", color="red", linewidth=1.5, label="Perfect prediction")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Actual G3")
    ax.set_ylabel("Predicted G3")
    ax.set_title(f"Actual vs Predicted — {model_name}\n({scenario})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"eval_actual_vs_pred_{scenario}.png", dpi=150)
    plt.close(fig)


def plot_residual_distribution(scenario: str, y_true, y_pred, model_name: str):
    residuals = y_true - y_pred
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(residuals, bins=25, edgecolor="black", alpha=0.7)
    ax.axvline(0, color="red", linestyle="--")
    ax.set_xlabel("Residual (Actual − Predicted)")
    ax.set_ylabel("Count")
    ax.set_title(f"Residual Distribution — {model_name} ({scenario})")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"eval_residual_dist_{scenario}.png", dpi=150)
    plt.close(fig)


def plot_residual_vs_predicted(scenario: str, y_true, y_pred, model_name: str):
    residuals = y_true - y_pred
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(y_pred, residuals, alpha=0.6, edgecolors="k", linewidths=0.3)
    ax.axhline(0, color="red", linestyle="--")
    ax.set_xlabel("Predicted G3")
    ax.set_ylabel("Residual")
    ax.set_title(f"Residuals vs Predicted — {model_name} ({scenario})")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"eval_residual_vs_pred_{scenario}.png", dpi=150)
    plt.close(fig)


def plot_error_by_range(scenario: str, error_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(error_df["grade_range"].astype(str), error_df["mean_abs_error"],
           yerr=error_df["std_abs_error"], capsize=4, color="coral", alpha=0.8)
    ax.set_xlabel("Grade Range")
    ax.set_ylabel("Mean Absolute Error")
    ax.set_title(f"MAE by Grade Range — {scenario}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / f"eval_error_by_range_{scenario}.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("GradeSense — Model Evaluation & Error Analysis")
    print("=" * 60)

    # Load data and prepare splits (same seed ⇒ same split)
    download_dataset()
    df = load_data()
    data = prepare_data(df)

    all_eval = {}

    for scenario in ["early_performance", "grade_assisted"]:
        model_path = MODELS_DIR / f"best_model_{scenario}.joblib"
        if not model_path.exists():
            print(f"[WARN] Model not found: {model_path}. Skipping.")
            continue

        pipe = joblib.load(model_path)
        sd = data[scenario]
        X_test = sd["X_test"]
        y_test = sd["y_test"]

        y_pred = pipe.predict(X_test)
        metrics = compute_metrics(y_test, y_pred)

        # Error analysis
        err_range = error_by_grade_range(y_test, y_pred)
        large_err = identify_large_errors(y_test, y_pred, threshold=3.0)

        # Determine model name from metadata
        meta_path = MODELS_DIR / "model_metadata.json"
        model_name = scenario
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            model_name = meta.get(scenario, {}).get("best_model", scenario)

        # Generate plots
        print(f"\n--- {scenario} ({model_name}) ---")
        print(f"  Test Metrics: {metrics}")
        print(f"  Large errors (|err| > 3): {len(large_err)} cases")
        print(f"  Error by grade range:\n{err_range.to_string(index=False)}")

        plot_actual_vs_predicted(scenario, y_test, y_pred, model_name)
        plot_residual_distribution(scenario, y_test, y_pred, model_name)
        plot_residual_vs_predicted(scenario, y_test, y_pred, model_name)
        plot_error_by_range(scenario, err_range)

        # Save error analysis
        eval_result = {
            "model": model_name,
            "test_metrics": metrics,
            "error_by_range": err_range.to_dict(orient="records"),
            "large_error_count": int(len(large_err)),
            "large_error_threshold": 3.0,
        }
        all_eval[scenario] = eval_result

        # Save large errors CSV
        large_err_path = OUTPUTS_DIR / f"large_errors_{scenario}.csv"
        large_err.to_csv(large_err_path, index=False)

        # Save error by range CSV
        err_range_path = OUTPUTS_DIR / f"error_by_range_{scenario}.csv"
        err_range.to_csv(err_range_path, index=False)

    # Save combined evaluation JSON
    eval_path = OUTPUTS_DIR / "evaluation_results.json"
    with open(eval_path, "w") as f:
        json.dump(all_eval, f, indent=2, default=str)
    print(f"\n[SAVE] {eval_path}")

    print("\n" + "=" * 60)
    print("Evaluation complete - OK")
    print("=" * 60)


if __name__ == "__main__":
    main()
