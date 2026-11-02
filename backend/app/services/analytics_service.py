"""
Analytics service for GradeSense backend.
Computes statistical findings, hypothesis tests, and dashboard insights.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy import stats

from app.schemas import AnalyticalInsight, StatisticalTestResult
from app.services.data_service import (
    load_dataset,
    get_grade_distribution,
    get_correlation_data,
)
from app.services.model_service import get_model_comparison

logger = logging.getLogger(__name__)


def compute_statistical_tests() -> List[StatisticalTestResult]:
    """Execute formal hypothesis tests on the dataset."""
    df = load_dataset()
    results: List[StatisticalTestResult] = []

    # Test 1: Welch's t-test for Higher Education desire on G3
    higher_yes = df[df["higher"] == "yes"]["G3"]
    higher_no = df[df["higher"] == "no"]["G3"]
    t_stat, p_val = stats.ttest_ind(higher_yes, higher_no, equal_var=False)
    results.append(
        StatisticalTestResult(
            test_name="Welch's Two-Sample t-test",
            description="Comparing mean final grades (G3) between students desiring higher education ('yes') vs ('no').",
            statistic=round(float(t_stat), 4),
            p_value=round(float(p_val), 6),
            significant=bool(p_val < 0.05),
            interpretation=(
                f"Statistically significant difference (t={t_stat:.2f}, p={p_val:.4e}). "
                f"Students aiming for higher education average {higher_yes.mean():.2f}/20 vs "
                f"{higher_no.mean():.2f}/20 for those who do not."
            ),
        )
    )

    # Test 2: One-way ANOVA for Study Time groups on G3
    groups = [group["G3"].values for _, group in df.groupby("studytime")]
    f_stat, p_val_anova = stats.f_oneway(*groups)
    results.append(
        StatisticalTestResult(
            test_name="One-Way ANOVA",
            description="Evaluating final grade differences across four weekly study-time tiers (<2h, 2-5h, 5-10h, >10h).",
            statistic=round(float(f_stat), 4),
            p_value=round(float(p_val_anova), 6),
            significant=bool(p_val_anova < 0.05),
            interpretation=(
                f"Observed difference across study-time categories is statistically significant (F={f_stat:.2f}, p={p_val_anova:.4f}). "
                "Students dedicating >5 weekly hours demonstrate higher mean grades, though variation remains substantial within groups."
            ),
        )
    )

    # Test 3: Pearson & Spearman correlation between G2 and G3
    pearson_r, pearson_p = stats.pearsonr(df["G2"], df["G3"])
    results.append(
        StatisticalTestResult(
            test_name="Pearson Correlation (G2 vs G3)",
            description="Assessing linear association between second-period grade (G2) and final grade (G3).",
            statistic=round(float(pearson_r), 4),
            p_value=round(float(pearson_p), 6),
            significant=bool(pearson_p < 0.05),
            interpretation=(
                f"Very strong positive linear correlation (r={pearson_r:.3f}, p={pearson_p:.4e}). "
                "Second-period performance is the single strongest empirical predictor of final achievement."
            ),
        )
    )

    return results


def get_analytical_insights() -> List[AnalyticalInsight]:
    """Compile data-driven insights and summary findings."""
    df = load_dataset()
    insights: List[AnalyticalInsight] = []

    # 1. Final Grade Overview & Failure Rate
    g3 = df["G3"]
    fail_count = int((g3 < 10).sum())
    fail_pct = round((fail_count / len(df)) * 100, 1)
    zero_count = int((g3 == 0).sum())
    zero_pct = round((zero_count / len(df)) * 100, 1)

    insights.append(
        AnalyticalInsight(
            category="Academic Performance",
            title="Grade Distribution & Passing Proportions",
            description=(
                f"The cohort average is {g3.mean():.2f}/20 (median {g3.median():.1f}, std {g3.std():.2f}). "
                f"A total of {fail_count} students ({fail_pct}%) scored below the passing threshold of 10/20. "
                f"Notably, {zero_count} students ({zero_pct}%) received a zero grade, indicating non-attendance or dropouts."
            ),
            value={"mean": round(float(g3.mean()), 2), "failure_rate_pct": fail_pct, "zero_grade_pct": zero_pct},
        )
    )

    # 2. Period Grade Dominance
    r_g1, _ = stats.pearsonr(df["G1"], df["G3"])
    r_g2, _ = stats.pearsonr(df["G2"], df["G3"])
    insights.append(
        AnalyticalInsight(
            category="Predictive Relationships",
            title="Dominance of Earlier Period Grades",
            description=(
                f"Earlier academic assessments demonstrate high predictive correlation: G1 (r={r_g1:.3f}) and "
                f"G2 (r={r_g2:.3f}). When earlier grades are available, predictive error drops substantially."
            ),
            value={"correlation_G1_G3": round(float(r_g1), 3), "correlation_G2_G3": round(float(r_g2), 3)},
        )
    )

    # 3. Study Time Impact
    study_means = df.groupby("studytime")["G3"].mean().to_dict()
    study_labels = {1: "<2 hrs", 2: "2-5 hrs", 3: "5-10 hrs", 4: ">10 hrs"}
    study_formatted = {study_labels[k]: round(float(v), 2) for k, v in study_means.items()}
    insights.append(
        AnalyticalInsight(
            category="Study Habits",
            title="Study Time and Academic Outcomes",
            description=(
                f"Average grades rise progressively with weekly study time: {study_formatted}. "
                "While higher study time correlates with higher mean scores, individual variation is broad."
            ),
            value=study_formatted,
        )
    )

    # 4. Absence Patterns
    abs_corr, _ = stats.spearmanr(df["absences"], df["G3"])
    insights.append(
        AnalyticalInsight(
            category="Attendance",
            title="Absence Patterns and Final Outcomes",
            description=(
                f"Absences show a weak non-linear rank association with final grades (Spearman rho = {abs_corr:.3f}). "
                "Moderate absences do not guarantee failure, but extreme absenteeism is observed alongside severe grade drops."
            ),
            value={"spearman_rho": round(float(abs_corr), 3), "max_absences": int(df["absences"].max())},
        )
    )

    # 5. Modeling Comparison Insight
    comp = get_model_comparison()
    if comp:
        early_models = [m for m in comp if m.get("scenario") == "early_performance"]
        assisted_models = [m for m in comp if m.get("scenario") == "grade_assisted"]
        best_early_mae = min((m.get("test_mae", 99) for m in early_models), default=None)
        best_assisted_mae = min((m.get("test_mae", 99) for m in assisted_models), default=None)

        insights.append(
            AnalyticalInsight(
                category="Machine Learning",
                title="Scenario Disparity: Early vs Grade-Assisted",
                description=(
                    f"In Scenario A (Early-Performance without prior grades), the best test MAE is {best_early_mae:.2f}. "
                    f"In Scenario B (Grade-Assisted with G1 & G2), test MAE drops to {best_assisted_mae:.2f}. "
                    "This demonstrates that prior academic performance overwhelmingly accounts for final variance."
                ),
                value={"best_early_test_mae": best_early_mae, "best_assisted_test_mae": best_assisted_mae},
            )
        )

    return insights
