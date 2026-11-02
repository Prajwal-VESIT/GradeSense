"""
GradeSense - Model Training Module
====================================
Trains multiple regression models for both prediction scenarios,
performs cross-validation, selects the best model, evaluates on the
held-out test set, and saves all artefacts (models, metrics, figures).

Models trained (per scenario):
  1. DummyRegressor  (baseline — always predicts the mean)
  2. LinearRegression
  3. Ridge  (L2 regularisation, alpha=1.0)
  4. RandomForestRegressor  (100 trees)
  5. GradientBoostingRegressor  (100 boosting rounds)
  6. HistGradientBoostingRegressor  (histogram-based gradient boosting)

Author : [Student Name]
Course : VESIT SEM VII — Data Science
"""

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for saving figures
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_validate
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.inspection import permutation_importance

# Import our preprocessing module (works when run from project root)
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
    build_preprocessor,
    PROJECT_ROOT,
    OUTPUTS_DIR,
    MODELS_DIR,
    TARGET,
    RANDOM_STATE,
)

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
FIGURES_DIR = OUTPUTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Suppress harmless convergence / deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)

# Global plot style
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------
def get_models() -> dict:
    """Return a dict of model_name → estimator (un-fitted)."""
    return {
        "DummyRegressor": DummyRegressor(strategy="mean"),
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0, random_state=RANDOM_STATE),
        "RandomForest": RandomForestRegressor(
            n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=100, random_state=RANDOM_STATE,
        ),
        "HistGradientBoosting": HistGradientBoostingRegressor(
            random_state=RANDOM_STATE,
        ),
    }


# ---------------------------------------------------------------------------
# Training & evaluation helpers
# ---------------------------------------------------------------------------
def compute_metrics(y_true, y_pred) -> dict:
    """Compute MAE, MSE, RMSE, R² and return as a dict."""
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


def train_scenario(scenario_name: str, scenario_data: dict) -> dict:
    """Train all models for one scenario, cross-validate, evaluate on test.

    Returns a dict with per-model results, best model info, and predictions.
    """
    X_train = scenario_data["X_train"]
    X_test = scenario_data["X_test"]
    y_train = scenario_data["y_train"]
    y_test = scenario_data["y_test"]
    preprocessor = scenario_data["preprocessor"]

    models = get_models()
    results = {}
    best_cv_mae = np.inf
    best_model_name = None
    best_pipeline = None

    print(f"\n{'-' * 50}")
    print(f"  Scenario: {scenario_name}")
    print(f"  Train: {X_train.shape[0]}  |  Test: {X_test.shape[0]}  |  Features: {X_train.shape[1]}")
    print(f"{'-' * 50}")

    for name, estimator in models.items():
        # Build a full pipeline: preprocessor → model
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("model", estimator),
        ])

        # 5-fold cross-validation on training set
        cv_results = cross_validate(
            pipe, X_train, y_train, cv=5,
            scoring=["neg_mean_absolute_error", "neg_mean_squared_error", "r2"],
            return_train_score=False,
            n_jobs=-1,
        )
        cv_mae = -cv_results["test_neg_mean_absolute_error"].mean()
        cv_mse = -cv_results["test_neg_mean_squared_error"].mean()
        cv_r2 = cv_results["test_r2"].mean()

        # Re-fit on full training set (cross_validate clones the estimator)
        pipe.fit(X_train, y_train)

        # Evaluate on held-out test set
        y_pred = pipe.predict(X_test)
        test_metrics = compute_metrics(y_test, y_pred)

        results[name] = {
            "cv_MAE": round(float(cv_mae), 4),
            "cv_MSE": round(float(cv_mse), 4),
            "cv_R2": round(float(cv_r2), 4),
            "test": test_metrics,
            "pipeline": pipe,
            "y_pred": y_pred,
        }

        print(
            f"  {name:<28s}  CV MAE={cv_mae:.3f}  "
            f"Test MAE={test_metrics['MAE']:.3f}  R2={test_metrics['R2']:.3f}"
        )

        # Track best model by CV MAE
        if cv_mae < best_cv_mae:
            best_cv_mae = cv_mae
            best_model_name = name
            best_pipeline = pipe

    print(f"\n  [*] Best model: {best_model_name}  (CV MAE = {best_cv_mae:.4f})")

    # Permutation importance for the best model on test set
    perm_imp = permutation_importance(
        best_pipeline, X_test, y_test,
        n_repeats=15, random_state=RANDOM_STATE, n_jobs=-1,
        scoring="neg_mean_absolute_error",
    )
    feature_names = list(X_test.columns)
    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance_mean": perm_imp.importances_mean,
        "importance_std": perm_imp.importances_std,
    }).sort_values("importance_mean", ascending=False)

    return {
        "results": results,
        "best_model_name": best_model_name,
        "best_pipeline": best_pipeline,
        "importance": importance_df,
        "y_test": y_test,
    }


# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------
def plot_grade_distribution(df: pd.DataFrame):
    """Histogram of G3 (target variable)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df[TARGET], bins=21, range=(-0.5, 20.5), edgecolor="black", alpha=0.7)
    ax.set_xlabel("Final Grade (G3)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Final Grade (G3)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "grade_distribution.png", dpi=150)
    plt.close(fig)
    print(f"  [FIG] grade_distribution.png")


def plot_correlation_heatmap(df: pd.DataFrame):
    """Correlation heatmap for numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(14, 11))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax,
                square=True, linewidths=0.5, vmin=-1, vmax=1)
    ax.set_title("Correlation Heatmap — Numeric Features")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "correlation_heatmap.png", dpi=150)
    plt.close(fig)
    print(f"  [FIG] correlation_heatmap.png")


def plot_model_comparison(all_scenario_results: dict):
    """Bar chart comparing test MAE across models for each scenario."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
    for idx, (scenario, sdata) in enumerate(all_scenario_results.items()):
        names = list(sdata["results"].keys())
        maes = [sdata["results"][n]["test"]["MAE"] for n in names]
        bars = axes[idx].barh(names, maes, color=sns.color_palette("muted", len(names)))
        axes[idx].set_xlabel("Test MAE")
        axes[idx].set_title(f"Model Comparison — {scenario}")
        # Annotate values
        for bar, val in zip(bars, maes):
            axes[idx].text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                           f"{val:.3f}", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "model_comparison.png", dpi=150)
    plt.close(fig)
    print(f"  [FIG] model_comparison.png")


def plot_actual_vs_predicted(scenario_name: str, y_true, y_pred, model_name: str):
    """Scatter plot: actual vs predicted."""
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(y_true, y_pred, alpha=0.6, edgecolors="k", linewidths=0.3)
    lims = [min(y_true.min(), y_pred.min()) - 1, max(y_true.max(), y_pred.max()) + 1]
    ax.plot(lims, lims, "--", color="red", linewidth=1.5, label="Perfect prediction")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Actual G3")
    ax.set_ylabel("Predicted G3")
    ax.set_title(f"Actual vs Predicted — {model_name}\n({scenario_name})")
    ax.legend()
    fig.tight_layout()
    fname = f"actual_vs_pred_{scenario_name}.png"
    fig.savefig(FIGURES_DIR / fname, dpi=150)
    plt.close(fig)
    print(f"  [FIG] {fname}")


def plot_residuals(scenario_name: str, y_true, y_pred, model_name: str):
    """Two-panel residual plot: residual distribution + residual vs predicted."""
    residuals = y_true - y_pred
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Residual distribution
    ax1.hist(residuals, bins=25, edgecolor="black", alpha=0.7)
    ax1.axvline(0, color="red", linestyle="--")
    ax1.set_xlabel("Residual (Actual − Predicted)")
    ax1.set_ylabel("Count")
    ax1.set_title("Residual Distribution")

    # Residual vs Predicted
    ax2.scatter(y_pred, residuals, alpha=0.6, edgecolors="k", linewidths=0.3)
    ax2.axhline(0, color="red", linestyle="--")
    ax2.set_xlabel("Predicted G3")
    ax2.set_ylabel("Residual")
    ax2.set_title("Residuals vs Predicted")

    fig.suptitle(f"{model_name} — {scenario_name}", fontsize=13)
    fig.tight_layout()
    fname = f"residuals_{scenario_name}.png"
    fig.savefig(FIGURES_DIR / fname, dpi=150)
    plt.close(fig)
    print(f"  [FIG] {fname}")


def plot_feature_importance(scenario_name: str, importance_df: pd.DataFrame, top_n: int = 15):
    """Horizontal bar chart of permutation importances."""
    df_plot = importance_df.head(top_n)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(df_plot["feature"], df_plot["importance_mean"],
            xerr=df_plot["importance_std"], color="teal", alpha=0.8)
    ax.invert_yaxis()
    ax.set_xlabel("Mean Permutation Importance (↑ = more important)")
    ax.set_title(f"Top-{top_n} Feature Importances — {scenario_name}")
    fig.tight_layout()
    fname = f"feature_importance_{scenario_name}.png"
    fig.savefig(FIGURES_DIR / fname, dpi=150)
    plt.close(fig)
    print(f"  [FIG] {fname}")


def plot_scatter_features(df: pd.DataFrame):
    """Scatter plots of G1, G2 vs G3."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    ax1.scatter(df["G1"], df[TARGET], alpha=0.5, edgecolors="k", linewidths=0.3)
    ax1.set_xlabel("G1 (Period 1 Grade)")
    ax1.set_ylabel("G3 (Final Grade)")
    ax1.set_title("G1 vs G3")

    ax2.scatter(df["G2"], df[TARGET], alpha=0.5, edgecolors="k", linewidths=0.3, color="orange")
    ax2.set_xlabel("G2 (Period 2 Grade)")
    ax2.set_ylabel("G3 (Final Grade)")
    ax2.set_title("G2 vs G3")

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "scatter_G1_G2_vs_G3.png", dpi=150)
    plt.close(fig)
    print(f"  [FIG] scatter_G1_G2_vs_G3.png")


def plot_box_plots(df: pd.DataFrame):
    """Box-plots of G3 by key categorical features."""
    cats = ["sex", "school", "higher", "internet", "romantic", "address"]
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    for ax, cat in zip(axes.flat, cats):
        sns.boxplot(data=df, x=cat, y=TARGET, ax=ax)
        ax.set_title(f"G3 by {cat}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "boxplots_G3_by_category.png", dpi=150)
    plt.close(fig)
    print(f"  [FIG] boxplots_G3_by_category.png")


def plot_grade_by_studytime(df: pd.DataFrame):
    """Visualization 2: Box plot comparing final grades across study-time categories."""
    fig, ax = plt.subplots(figsize=(8, 5))
    study_map = {1: "<2 hours", 2: "2-5 hours", 3: "5-10 hours", 4: ">10 hours"}
    plot_df = df.copy()
    plot_df["studytime_label"] = plot_df["studytime"].map(study_map)
    order = ["<2 hours", "2-5 hours", "5-10 hours", ">10 hours"]
    sns.boxplot(data=plot_df, x="studytime_label", y=TARGET, order=order, ax=ax, palette="Blues_r")
    ax.set_xlabel("Weekly Study Time")
    ax.set_ylabel("Final Grade (G3)")
    ax.set_title("Final Grade Distribution by Weekly Study Time")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "grade_by_studytime.png", dpi=150)
    plt.close(fig)
    print(f"  [FIG] grade_by_studytime.png")


def plot_absences_vs_g3(df: pd.DataFrame):
    """Visualization 5: Absences versus final grades."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.regplot(data=df, x="absences", y=TARGET, ax=ax, scatter_kws={"alpha": 0.5}, line_kws={"color": "red"})
    ax.set_xlabel("Number of School Absences")
    ax.set_ylabel("Final Grade (G3)")
    ax.set_title("Relationship Between School Absences and Final Grade")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "absences_vs_g3.png", dpi=150)
    plt.close(fig)
    print(f"  [FIG] absences_vs_g3.png")


# ---------------------------------------------------------------------------
# Save results helpers
# ---------------------------------------------------------------------------
def save_model_artifacts(all_scenario_results: dict):
    """Save best model pipelines and metadata JSON files."""
    metadata = {}
    comparison_rows = []

    for scenario, sdata in all_scenario_results.items():
        best_name = sdata["best_model_name"]
        best_pipe = sdata["best_pipeline"]

        # Save best pipeline as .joblib (support multiple standard aliases)
        model_path = MODELS_DIR / f"{scenario}_model.joblib"
        joblib.dump(best_pipe, model_path)
        joblib.dump(best_pipe, MODELS_DIR / f"best_model_{scenario}.joblib")
        joblib.dump(best_pipe, MODELS_DIR / f"{scenario}_pipeline.joblib")
        print(f"[SAVE] {model_path} (and aliases)")

        # Save feature importance CSV
        imp_path = OUTPUTS_DIR / f"feature_importance_{scenario}.csv"
        sdata["importance"].to_csv(imp_path, index=False)

        # Collect metadata
        scenario_meta = {
            "best_model": best_name,
            "model_path": str(model_path),
            "models": {},
        }
        for name, res in sdata["results"].items():
            entry = {
                "cv_MAE": res["cv_MAE"],
                "cv_MSE": res["cv_MSE"],
                "cv_R2": res["cv_R2"],
                "test_MAE": res["test"]["MAE"],
                "test_MSE": res["test"]["MSE"],
                "test_RMSE": res["test"]["RMSE"],
                "test_R2": res["test"]["R2"],
            }
            scenario_meta["models"][name] = entry

            comparison_rows.append({
                "scenario": scenario,
                "model": name,
                **entry,
            })

        metadata[scenario] = scenario_meta

    # Save model_metadata.json
    meta_path = MODELS_DIR / "model_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"[SAVE] {meta_path}")

    # Save model_comparison.json and .csv
    comp_json_path = OUTPUTS_DIR / "model_comparison.json"
    with open(comp_json_path, "w") as f:
        json.dump(comparison_rows, f, indent=2)
    print(f"[SAVE] {comp_json_path}")

    comp_csv_path = OUTPUTS_DIR / "model_comparison.csv"
    pd.DataFrame(comparison_rows).to_csv(comp_csv_path, index=False)
    print(f"[SAVE] {comp_csv_path}")

    # Save predictions / residuals for error analysis
    for scenario, sdata in all_scenario_results.items():
        best_name = sdata["best_model_name"]
        y_test = sdata["y_test"]
        y_pred = sdata["results"][best_name]["y_pred"]
        pred_df = pd.DataFrame({
            "actual": y_test,
            "predicted": y_pred,
            "residual": y_test - y_pred,
        })
        pred_path = OUTPUTS_DIR / f"predictions_{scenario}.csv"
        pred_df.to_csv(pred_path, index=False)
        print(f"[SAVE] {pred_path}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    """Run the full model training pipeline."""
    print("=" * 60)
    print("GradeSense — Model Training Pipeline")
    print("=" * 60)

    # 1. Load data
    download_dataset()
    df = load_data()

    # 2. Prepare train/test splits for both scenarios
    data = prepare_data(df)

    # 3. Generate dataset-level plots
    print("\n[INFO] Generating dataset-level figures ...")
    plot_grade_distribution(df)
    plot_grade_by_studytime(df)
    plot_correlation_heatmap(df)
    plot_scatter_features(df)
    plot_absences_vs_g3(df)
    plot_box_plots(df)

    # 4. Train models for each scenario
    all_results = {}
    for scenario_name, scenario_data in data.items():
        all_results[scenario_name] = train_scenario(scenario_name, scenario_data)

    # 5. Generate per-scenario plots
    print("\n[INFO] Generating model-level figures ...")
    for scenario_name, sdata in all_results.items():
        best_name = sdata["best_model_name"]
        y_test = sdata["y_test"]
        y_pred = sdata["results"][best_name]["y_pred"]
        plot_actual_vs_predicted(scenario_name, y_test, y_pred, best_name)
        plot_residuals(scenario_name, y_test, y_pred, best_name)
        plot_feature_importance(scenario_name, sdata["importance"])

    plot_model_comparison(all_results)

    # 6. Save all artefacts
    print("\n[INFO] Saving models and results ...")
    save_model_artifacts(all_results)

    # 7. Print summary
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    for scenario_name, sdata in all_results.items():
        best = sdata["best_model_name"]
        metrics = sdata["results"][best]["test"]
        print(
            f"  {scenario_name:<24s} -> Best: {best:<28s} "
            f"MAE={metrics['MAE']:.3f}  RMSE={metrics['RMSE']:.3f}  R2={metrics['R2']:.3f}"
        )
    print("=" * 60)
    print("Training complete - OK")

    return all_results


if __name__ == "__main__":
    main()
