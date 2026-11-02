# GradeSense — Analytical Summary

*Generated: 2026-11-02 23:36*

## 1. Dataset Overview

- **Dataset**: UCI Student Performance (Mathematics)
- **Source**: https://archive.ics.uci.edu/dataset/320/student+performance
- **Shape**: ? rows × ? columns
- **Duplicates**: ?
- **Missing values**: None
- **Target variable**: G3 (final grade, 0–20 scale)

## 2. Prediction Scenarios

| Scenario | Description |
|----------|-------------|
| Early Performance | Predict G3 **without** G1, G2 (no prior exam grades) |
| Grade Assisted | Predict G3 **with** G1, G2 (prior exam grades available) |

## 3. Results — Early Performance

**Best Model**: RandomForest

| Metric | Value |
|--------|-------|
| MAE | 3.0022 |
| MSE | 14.203 |
| RMSE | 3.7687 |
| R2 | 0.3073 |

### All Models Comparison

| Model | CV MAE | Test MAE | Test RMSE | Test R² |
|-------|--------|----------|-----------|---------|
| DummyRegressor | 3.3883 | 3.6459 | 4.5502 | -0.0097 |
| LinearRegression | 3.5757 | 3.3953 | 4.1957 | 0.1415 |
| Ridge | 3.5572 | 3.3929 | 4.1934 | 0.1424 |
| RandomForest | 2.9087 | 3.0022 | 3.7687 | 0.3073 |
| GradientBoosting | 3.1171 | 3.1111 | 3.9359 | 0.2445 |
| HistGradientBoosting | 3.1636 | 3.1902 | 3.9641 | 0.2336 |

### Error by Grade Range

| Grade Range | Count | Mean |err| | Std |err| |
|-------------|-------|-----------|----------|
| 0-5 (Fail) | 9 | 6.124 | 3.173 |
| 6-10 (Low) | 29 | 2.497 | 1.784 |
| 11-15 (Mid) | 31 | 1.995 | 1.426 |
| 16-20 (High) | 10 | 4.779 | 1.534 |

### Top-10 Important Features (Permutation Importance)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | failures | 0.4805 |
| 2 | absences | 0.3518 |
| 3 | goout | 0.1340 |
| 4 | Medu | 0.0828 |
| 5 | sex | 0.0733 |
| 6 | schoolsup | 0.0697 |
| 7 | Mjob | 0.0690 |
| 8 | Fjob | 0.0639 |
| 9 | guardian | 0.0613 |
| 10 | romantic | 0.0445 |

## 3. Results — Grade Assisted

**Best Model**: RandomForest

| Metric | Value |
|--------|-------|
| MAE | 1.2138 |
| MSE | 4.0354 |
| RMSE | 2.0088 |
| R2 | 0.8032 |

### All Models Comparison

| Model | CV MAE | Test MAE | Test RMSE | Test R² |
|-------|--------|----------|-----------|---------|
| DummyRegressor | 3.3883 | 3.6459 | 4.5502 | -0.0097 |
| LinearRegression | 1.3369 | 1.6467 | 2.3784 | 0.7241 |
| Ridge | 1.3298 | 1.6391 | 2.3715 | 0.7257 |
| RandomForest | 0.9067 | 1.2138 | 2.0088 | 0.8032 |
| GradientBoosting | 0.975 | 1.1526 | 1.9829 | 0.8083 |
| HistGradientBoosting | 1.0609 | 1.2321 | 1.9348 | 0.8174 |

### Error by Grade Range

| Grade Range | Count | Mean |err| | Std |err| |
|-------------|-------|-----------|----------|
| 0-5 (Fail) | 9 | 2.970 | 2.818 |
| 6-10 (Low) | 29 | 1.379 | 1.763 |
| 11-15 (Mid) | 31 | 0.705 | 0.630 |
| 16-20 (High) | 10 | 0.732 | 0.331 |

### Top-10 Important Features (Permutation Importance)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | G2 | 3.4609 |
| 2 | absences | 0.3215 |
| 3 | age | 0.0279 |
| 4 | studytime | 0.0232 |
| 5 | internet | 0.0097 |
| 6 | traveltime | 0.0075 |
| 7 | health | 0.0072 |
| 8 | goout | 0.0056 |
| 9 | nursery | 0.0042 |
| 10 | Fedu | 0.0041 |

## 4. Figures

All figures saved in `outputs/figures/`:

- `grade_distribution.png` — distribution of G3
- `correlation_heatmap.png` — numeric feature correlations
- `scatter_G1_G2_vs_G3.png` — G1 and G2 scatter vs G3
- `boxplots_G3_by_category.png` — G3 distributions by category
- `model_comparison.png` — bar chart comparing all models
- `actual_vs_pred_*.png` — actual vs predicted scatter
- `residuals_*.png` — residual analysis plots
- `feature_importance_*.png` — permutation importance charts

## 5. Conclusions

1. **Grade-assisted scenario** vastly outperforms early-performance, confirming 
   that G1 and G2 are the strongest predictors of G3.
2. **Early-performance** is more challenging but still useful for identifying 
   at-risk students before any exams are graded.
3. **Failure cases** (G3 = 0) are hardest to predict accurately.

---
*GradeSense — VESIT SEM VII Data Science Mini Project*