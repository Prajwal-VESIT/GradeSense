# GradeSense — Student Performance Prediction
## Mini Project Report

**Course**: Data Science (SEM VII)
**College**: VESIT
**Date**: November 2026
**Team Members**: [Student Name 1], [Student Name 2], [Student Name 3]

---

## Abstract

This project applies machine learning regression techniques to predict student final grades (G3) in Mathematics using the UCI Student Performance dataset. We explore two scenarios: (A) Early Performance prediction without prior exam scores, and (B) Grade-Assisted prediction leveraging first and second period grades. Multiple models are trained, cross-validated, and compared using MAE, RMSE, and R² metrics.

## 1. Introduction

### 1.1 Problem Statement
Predicting student academic performance is crucial for early intervention. This project aims to build predictive models that estimate a student's final Mathematics grade based on demographic, social, and school-related features.

### 1.2 Objectives
1. Preprocess and explore the UCI Student Performance dataset.
2. Train and compare multiple regression models.
3. Evaluate models under two scenarios (with and without prior grades).
4. Identify the most important features for performance prediction.
5. Deploy a simple prediction API.

## 2. Dataset Description

- **Name**: Student Performance Data Set
- **Source**: [UCI ML Repository](https://archive.ics.uci.edu/dataset/320/student+performance)
- **Records**: 395
- **Features**: 33 (including target G3)
- **Target**: G3 — final grade (0 to 20)

### 2.1 Feature Categories

| Category | Features |
|----------|----------|
| Demographic | age, sex, address, famsize, Pstatus |
| Family | Medu, Fedu, Mjob, Fjob, guardian, famrel |
| School | school, reason, traveltime, studytime, failures, schoolsup, paid |
| Lifestyle | activities, nursery, higher, internet, romantic, freetime, goout |
| Health | health, Dalc, Walc |
| Academic | absences, G1, G2, **G3 (target)** |

## 3. Methodology

### 3.1 Preprocessing Pipeline
- **Numeric features**: Median imputation → Standard scaling
- **Categorical features**: Most-frequent imputation → One-hot encoding
- All transformations applied via `sklearn.pipeline.Pipeline` to prevent data leakage.

### 3.2 Train/Test Split
- 80/20 split with `random_state=42`
- 5-fold cross-validation on training set for model selection

### 3.3 Models Trained
1. **DummyRegressor** (baseline — predicts mean)
2. **Linear Regression**
3. **Ridge Regression** (α = 1.0)
4. **Random Forest** (100 trees)
5. **Gradient Boosting** (100 rounds)
6. **Histogram Gradient Boosting**

## 4. Results

### 4.1 Early Performance

**Best Model**: `RandomForest`

| Model | CV MAE | Test MAE | Test RMSE | Test R² |
|-------|--------|----------|-----------|---------|
| DummyRegressor | 3.3883 | 3.6459 | 4.5502 | -0.0097 |
| LinearRegression | 3.5757 | 3.3953 | 4.1957 | 0.1415 |
| Ridge | 3.5572 | 3.3929 | 4.1934 | 0.1424 |
| RandomForest ★ | 2.9087 | 3.0022 | 3.7687 | 0.3073 |
| GradientBoosting | 3.1171 | 3.1111 | 3.9359 | 0.2445 |
| HistGradientBoosting | 3.1636 | 3.1902 | 3.9641 | 0.2336 |

**Best model test performance**: MAE = 3.0022, RMSE = 3.7687, R² = 0.3073

### 4.2 Grade Assisted

**Best Model**: `RandomForest`

| Model | CV MAE | Test MAE | Test RMSE | Test R² |
|-------|--------|----------|-----------|---------|
| DummyRegressor | 3.3883 | 3.6459 | 4.5502 | -0.0097 |
| LinearRegression | 1.3369 | 1.6467 | 2.3784 | 0.7241 |
| Ridge | 1.3298 | 1.6391 | 2.3715 | 0.7257 |
| RandomForest ★ | 0.9067 | 1.2138 | 2.0088 | 0.8032 |
| GradientBoosting | 0.975 | 1.1526 | 1.9829 | 0.8083 |
| HistGradientBoosting | 1.0609 | 1.2321 | 1.9348 | 0.8174 |

**Best model test performance**: MAE = 1.2138, RMSE = 2.0088, R² = 0.8032

## 5. Error Analysis

### Early Performance
- Large errors (|error| > 3): **31** cases

| Grade Range | Count | Mean Abs Error |
|-------------|-------|----------------|
| 0-5 (Fail) | 9 | 6.124 |
| 6-10 (Low) | 29 | 2.497 |
| 11-15 (Mid) | 31 | 1.995 |
| 16-20 (High) | 10 | 4.779 |

### Grade Assisted
- Large errors (|error| > 3): **6** cases

| Grade Range | Count | Mean Abs Error |
|-------------|-------|----------------|
| 0-5 (Fail) | 9 | 2.970 |
| 6-10 (Low) | 29 | 1.379 |
| 11-15 (Mid) | 31 | 0.705 |
| 16-20 (High) | 10 | 0.732 |

## 6. Feature Importance

### Early Performance — Top-10

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

### Grade Assisted — Top-10

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

## 7. Conclusion

- The **Grade-Assisted** scenario achieves significantly better predictions, demonstrating that G1 and G2 are the dominant predictors of G3.
- The **Early Performance** scenario, while less accurate, is valuable for proactive student support before any grades are available.
- Tree-based ensemble methods (Random Forest, Gradient Boosting) generally outperform linear models, especially in the Early Performance scenario.
- Key non-grade features include `failures`, `absences`, `higher`, `Medu`, and `studytime`.

## References

1. P. Cortez and A. Silva. *Using Data Mining to Predict Secondary School Student Performance*. EUROSIS, 2008.
2. UCI Machine Learning Repository — Student Performance Data Set. https://archive.ics.uci.edu/dataset/320/student+performance
3. scikit-learn documentation. https://scikit-learn.org/stable/

---
*GradeSense — VESIT SEM VII Data Science Mini Project*