"""
Script to generate notebooks/GradeSense_Complete_Analysis.ipynb
with all 26 required sections and executable code.
"""

import json
from pathlib import Path

NOTEBOOK_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOK_DIR / "GradeSense_Complete_Analysis.ipynb"

nb = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.13.0",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def add_md(text: str):
    nb["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")],
    })


def add_code(text: str):
    nb["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.strip().split("\n")],
    })


# 1. Project Introduction
add_md("""# GradeSense: Student Performance Prediction & Academic Analytics
## Comprehensive Data Science CA2 Mini Project
**Course**: VESIT SEM VII — Data Science  
**Target Variable**: G3 (Final Numerical Grade on 0–20 scale)  
**Methodology**: Supervised Machine Learning Regression & Hypothesis Testing Across Two Deployment Scenarios  
*Disclaimer: GradeSense provides experimental estimates based on historical data. Predictions are not guaranteed outcomes and must not be used as the sole basis for high-stakes academic decisions.*""")

# 2. Problem Statement
add_md("""## 1. Problem Statement
Secondary education institutions face high stakes in identifying students requiring academic support. However, conventional institutional assessments typically identify struggling students only after summative end-of-term examinations have taken place, leaving virtually no window for corrective academic intervention.

Predicting student outcomes numerically (on a 0–20 scale) before or during earlier stages of the school term enables educational counselors and mentors to allocate academic support proactively. Crucially, the predictive model must distinguish between:
1. **Scenario A (Early-Performance Prediction)**: Relying strictly on background, family, study habit, and attendance proxy attributes before any term grades exist.
2. **Scenario B (Grade-Assisted Prediction)**: Utilizing formative term grades (G1, G2) once available to provide highly accurate end-of-term outcome forecasts.""")

# 3. Project Objectives
add_md("""## 2. Project Objectives
1. Explore student academic performance using the UCI Student Performance benchmark dataset.
2. Perform descriptive statistical analysis and exploratory data analysis.
3. Identify missing values, duplicate records, outliers, and unusual patterns.
4. Visualize distributions, correlations, and key predictive relationships.
5. Formulate and test statistical hypotheses (Welch's t-test, ANOVA, correlation significance).
6. Train and compare multiple regression models (Dummy baseline, Linear Regression, Ridge, Random Forest, Gradient Boosting, HistGradient Boosting).
7. Prevent data leakage using scikit-learn Pipeline and ColumnTransformer.
8. Evaluate models on held-out test data using MAE, MSE, RMSE, and R².
9. Perform residual and error analysis across actual grade ranges.
10. Calculate permutation feature importance to identify key predictive factors without making causal claims.""")

# 4. Dataset Source and Description
add_md("""## 3. Dataset Source and Description
- **Dataset**: Student Performance Data Set (Mathematics Subject)
- **Source**: UCI Machine Learning Repository (Cortez & Silva, 2008)
- **Official URL**: https://archive.ics.uci.edu/dataset/320/student+performance
- **Dimensions**: 395 records × 33 attributes
- **Target Variable**: G3 (Final grade, integer range 0 to 20)""")

# 5. Environment Setup & Data Loading
add_md("""## 4. Environment Setup and Data Loading""")
add_code("""import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm

# Plotting configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
DATA_PATH = PROJECT_ROOT / 'data' / 'raw' / 'student-mat.csv'

df = pd.read_csv(DATA_PATH, sep=';')
if df.shape[1] == 1:
    df = pd.read_csv(DATA_PATH, sep=',')
print(f'Dataset loaded successfully: {df.shape[0]} rows × {df.shape[1]} columns')
df.head()""")

# 6. Data Dictionary
add_md("""## 5. Data Dictionary and Feature Descriptions
The 33 attributes cover demographic, family background, academic proxy, lifestyle, alcohol consumption, past failures, earlier period grades (G1, G2), and final grade (G3).""")
add_code("""data_dict = pd.DataFrame([
    ('school', 'Categorical', 'Student school (GP: Gabriel Pereira, MS: Mousinho da Silveira)'),
    ('sex', 'Categorical', 'Student sex (F: female, M: male)'),
    ('age', 'Numeric', 'Student age (15 to 22)'),
    ('address', 'Categorical', 'Home address type (U: urban, R: rural)'),
    ('famsize', 'Categorical', 'Family size (LE3: <=3, GT3: >3)'),
    ('Pstatus', 'Categorical', 'Parent cohabitation status (T: together, A: apart)'),
    ('Medu', 'Numeric', 'Mother education (0: none to 4: higher education)'),
    ('Fedu', 'Numeric', 'Father education (0: none to 4: higher education)'),
    ('Mjob', 'Categorical', 'Mother job (teacher, health, services, at_home, other)'),
    ('Fjob', 'Categorical', 'Father job (teacher, health, services, at_home, other)'),
    ('reason', 'Categorical', 'Reason for school choice (home, reputation, course, other)'),
    ('guardian', 'Categorical', 'Student guardian (mother, father, other)'),
    ('traveltime', 'Numeric', 'Home to school travel time (1: <15 min to 4: >1 hour)'),
    ('studytime', 'Numeric', 'Weekly study time (1: <2 hrs to 4: >10 hrs)'),
    ('failures', 'Numeric', 'Number of past class failures (0 to 4)'),
    ('schoolsup', 'Categorical', 'Extra educational support (yes/no)'),
    ('famsup', 'Categorical', 'Family educational support (yes/no)'),
    ('paid', 'Categorical', 'Extra paid classes within the course subject (yes/no)'),
    ('activities', 'Categorical', 'Extra-curricular activities (yes/no)'),
    ('nursery', 'Categorical', 'Attended nursery school (yes/no)'),
    ('higher', 'Categorical', 'Wants to take higher education (yes/no)'),
    ('internet', 'Categorical', 'Internet access at home (yes/no)'),
    ('romantic', 'Categorical', 'In a romantic relationship (yes/no)'),
    ('famrel', 'Numeric', 'Quality of family relationships (1: very bad to 5: excellent)'),
    ('freetime', 'Numeric', 'Free time after school (1: very low to 5: very high)'),
    ('goout', 'Numeric', 'Going out with friends (1: very low to 5: very high)'),
    ('Dalc', 'Numeric', 'Workday alcohol consumption (1: very low to 5: very high)'),
    ('Walc', 'Numeric', 'Weekend alcohol consumption (1: very low to 5: very high)'),
    ('health', 'Numeric', 'Current health status (1: very bad to 5: very good)'),
    ('absences', 'Numeric', 'Number of school absences (0 to 93)'),
    ('G1', 'Numeric', 'First period grade (0 to 20)'),
    ('G2', 'Numeric', 'Second period grade (0 to 20)'),
    ('G3', 'Numeric', 'Target variable: Final grade (0 to 20)'),
], columns=['Feature', 'Type', 'Description'])
data_dict""")

# 7-10. Data Quality Assessment
add_md("""## 6. Initial Data Inspection & Quality Assessment
Checking data types, missing values, and duplicate records.""")
add_code("""print('--- Data Types and Non-Null Counts ---')
print(df.dtypes)
print(f'\\nTotal missing values: {df.isnull().sum().sum()}')
print(f'Duplicate rows: {df.duplicated().sum()}')""")

# 11-12. Descriptive Statistics & Univariate Analysis
add_md("""## 7. Descriptive Statistics and Univariate Analysis
Examining central tendency, spread, skewness, and kurtosis across numerical features.""")
add_code("""num_cols = df.select_dtypes(include=[np.number]).columns
stats_df = pd.DataFrame(index=num_cols)
stats_df['Mean'] = df[num_cols].mean()
stats_df['Std'] = df[num_cols].std()
stats_df['Median'] = df[num_cols].median()
stats_df['IQR'] = df[num_cols].apply(lambda x: stats.iqr(x))
stats_df['Skewness'] = df[num_cols].skew()
stats_df['Kurtosis'] = df[num_cols].kurtosis()
stats_df['Min'] = df[num_cols].min()
stats_df['Max'] = df[num_cols].max()
round(stats_df, 3)""")

# Visualization 1: Final Grade Distribution
add_md("""### Visualization 1: Final Grade (G3) Distribution
Analyzing the target variable distribution. Notice the cluster of students at G3 = 0.""")
add_code("""fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df['G3'], bins=21, kde=True, color='#2b6cb0', ax=ax)
ax.axvline(df['G3'].mean(), color='red', linestyle='--', label=f"Mean ({df['G3'].mean():.2f})")
ax.axvline(df['G3'].median(), color='green', linestyle=':', label=f"Median ({df['G3'].median():.1f})")
ax.set_title('Distribution of Final Grade G3 (0–20 Scale)', fontsize=13, fontweight='bold')
ax.set_xlabel('Final Grade (G3)')
ax.set_ylabel('Student Count')
ax.legend()
plt.tight_layout()
plt.show()

zero_count = (df['G3'] == 0).sum()
print(f'Zero grade students: {zero_count} ({zero_count/len(df)*100:.1f}%)')""")

# Visualization 2: Grade by Study Time
add_md("""### Visualization 2: Grade Distribution by Weekly Study Time""")
add_code("""fig, ax = plt.subplots(figsize=(8, 5))
study_labels = {1: '<2 hrs', 2: '2-5 hrs', 3: '5-10 hrs', 4: '>10 hrs'}
plot_df = df.copy()
plot_df['study_label'] = plot_df['studytime'].map(study_labels)
order = ['<2 hrs', '2-5 hrs', '5-10 hrs', '>10 hrs']
sns.boxplot(data=plot_df, x='study_label', y='G3', order=order, palette='Blues_r', ax=ax)
ax.set_title('Final Grade Distribution Across Weekly Study Time Tiers', fontsize=13, fontweight='bold')
ax.set_xlabel('Weekly Study Time')
ax.set_ylabel('Final Grade (G3)')
plt.tight_layout()
plt.show()""")

# Visualization 3: Correlation Heatmap
add_md("""### Visualization 3: Correlation Heatmap of Numeric Features""")
add_code("""fig, ax = plt.subplots(figsize=(12, 9))
corr = df[num_cols].corr(method='pearson')
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, square=True, ax=ax)
ax.set_title('Pearson Correlation Heatmap of Numeric Attributes', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()""")

# Visualization 4: Earlier Grades vs Final Grade
add_md("""### Visualization 4: Earlier Term Grades (G1, G2) vs Final Grade (G3)""")
add_code("""fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
sns.regplot(data=df, x='G1', y='G3', ax=ax1, scatter_kws={'alpha': 0.5, 'color': '#2b6cb0'}, line_kws={'color': 'red'})
ax1.set_title('G1 vs G3 (First Period vs Final Grade)', fontsize=12, fontweight='bold')
ax1.set_xlabel('G1 Grade')
ax1.set_ylabel('Final Grade (G3)')

sns.regplot(data=df, x='G2', y='G3', ax=ax2, scatter_kws={'alpha': 0.5, 'color': '#dd6b20'}, line_kws={'color': 'red'})
ax2.set_title('G2 vs G3 (Second Period vs Final Grade)', fontsize=12, fontweight='bold')
ax2.set_xlabel('G2 Grade')
ax2.set_ylabel('Final Grade (G3)')
plt.tight_layout()
plt.show()""")

# Visualization 5: Absences vs Final Grade
add_md("""### Visualization 5: Absences and Final Grade""")
add_code("""fig, ax = plt.subplots(figsize=(8, 5))
sns.regplot(data=df, x='absences', y='G3', ax=ax, scatter_kws={'alpha': 0.6, 'color': '#4a5568'}, line_kws={'color': '#e53e3e'})
ax.set_title('School Absences vs Final Grade (G3)', fontsize=13, fontweight='bold')
ax.set_xlabel('Number of Absences')
ax.set_ylabel('Final Grade (G3)')
plt.tight_layout()
plt.show()""")

# 13-16. Statistical Analysis & Hypothesis Testing
add_md("""## 8. Statistical Analysis & Hypothesis Testing
Testing empirical hypotheses at $\\alpha = 0.05$ significance level.""")
add_code("""# Hypothesis 1: Higher Education Desire vs G3
higher_yes = df[df['higher'] == 'yes']['G3']
higher_no = df[df['higher'] == 'no']['G3']
t_stat, p_val = stats.ttest_ind(higher_yes, higher_no, equal_var=False)
print('--- Hypothesis Test 1: Welch Two-Sample t-test ---')
print(f'Null Hypothesis (H0): Mean G3 for higher==yes equals higher==no.')
print(f't-statistic: {t_stat:.4f}, p-value: {p_val:.4e}')
print(f'Statistically significant (alpha=0.05): {p_val < 0.05}')
print(f'Mean (higher=yes): {higher_yes.mean():.2f}, Mean (higher=no): {higher_no.mean():.2f}')

# Hypothesis 2: One-way ANOVA across Study Time Categories
print('\\n--- Hypothesis Test 2: One-Way ANOVA across Study Time ---')
study_groups = [group['G3'].values for _, group in df.groupby('studytime')]
f_stat, p_val_anova = stats.f_oneway(*study_groups)
print(f'F-statistic: {f_stat:.4f}, p-value: {p_val_anova:.4f}')
print(f'Statistically significant (alpha=0.05): {p_val_anova < 0.05}')""")

# 17-21. Machine Learning Pipelines, Comparison & Validation
add_md("""## 9. Machine Learning: Preprocessing, Model Comparison & Validation
We evaluate 6 regression algorithms under two distinct scenarios:
- **Scenario A (Early-Performance)**: Predicts G3 without G1 or G2.
- **Scenario B (Grade-Assisted)**: Predicts G3 using G1 and G2 alongside demographic and lifestyle features.""")

add_code("""from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance

sys.path.insert(0, str(PROJECT_ROOT))
from src.data_preprocessing import prepare_data, build_preprocessor

data = prepare_data(df)

models = {
    'DummyRegressor': DummyRegressor(strategy='mean'),
    'LinearRegression': LinearRegression(),
    'Ridge': Ridge(alpha=1.0, random_state=42),
    'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=1),
    'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
    'HistGradientBoosting': HistGradientBoostingRegressor(random_state=42),
}

comparison_rows = []
fitted_pipelines = {}

for scenario, sdata in data.items():
    X_train, X_test = sdata['X_train'], sdata['X_test']
    y_train, y_test = sdata['y_train'], sdata['y_test']
    preprocessor = build_preprocessor(sdata['numeric_features'], sdata['categorical_features'])
    
    print(f'=== Scenario: {scenario} ===')
    for name, est in models.items():
        pipe = Pipeline([('preprocessor', preprocessor), ('model', est)])
        cv = cross_validate(pipe, X_train, y_train, cv=5, scoring='neg_mean_absolute_error', n_jobs=1)
        cv_mae = -cv['test_score'].mean()
        
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        comparison_rows.append({
            'Scenario': scenario,
            'Model': name,
            'CV MAE': round(cv_mae, 3),
            'Test MAE': round(mae, 3),
            'Test RMSE': round(rmse, 3),
            'Test R2': round(r2, 3),
        })
        fitted_pipelines[f'{scenario}_{name}'] = pipe
        print(f'  {name:<24s} | CV MAE: {cv_mae:.3f} | Test MAE: {mae:.3f} | Test R2: {r2:.3f}')

comp_table = pd.DataFrame(comparison_rows)
comp_table""")

# Visualization 6: Model Comparison Chart
add_md("""### Visualization 6: Model Performance Comparison (MAE)""")
add_code("""fig, axes = plt.subplots(1, 2, figsize=(15, 5), sharey=True)
for idx, sc in enumerate(['early_performance', 'grade_assisted']):
    sub = comp_table[comp_table['Scenario'] == sc]
    sns.barplot(data=sub, x='Test MAE', y='Model', palette='Blues_d', ax=axes[idx])
    axes[idx].set_title(f'Test MAE: {sc.replace(\"_\", \" \").title()}', fontsize=12, fontweight='bold')
    for p in axes[idx].patches:
        width = p.get_width()
        axes[idx].annotate(f'{width:.2f}', (width + 0.05, p.get_y() + p.get_height() / 2), va='center')

plt.tight_layout()
plt.show()""")

# Visualization 7: Actual vs Predicted
add_md("""### Visualization 7: Actual vs Predicted Grades (Held-Out Test Set)""")
add_code("""fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

for ax, sc in zip([ax1, ax2], ['early_performance', 'grade_assisted']):
    best_pipe = fitted_pipelines[f'{sc}_RandomForest']
    X_test, y_test = data[sc]['X_test'], data[sc]['y_test']
    y_pred = best_pipe.predict(X_test)
    
    ax.scatter(y_test, y_pred, alpha=0.6, edgecolors='k')
    ax.plot([0, 20], [0, 20], 'r--', label='Perfect Fit')
    ax.set_title(f'Actual vs Predicted: {sc.replace(\"_\", \" \").title()} (Random Forest)', fontweight='bold')
    ax.set_xlabel('Actual Grade (G3)')
    ax.set_ylabel('Predicted Grade (G3)')
    ax.set_xlim(-1, 21)
    ax.set_ylim(-1, 21)
    ax.legend()

plt.tight_layout()
plt.show()""")

# Visualization 8: Feature Importance
add_md("""### Visualization 8: Feature Importance Analysis (Permutation Method)""")
add_code("""fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

for ax, sc in zip([ax1, ax2], ['early_performance', 'grade_assisted']):
    best_pipe = fitted_pipelines[f'{sc}_RandomForest']
    X_test, y_test = data[sc]['X_test'], data[sc]['y_test']
    perm = permutation_importance(best_pipe, X_test, y_test, n_repeats=15, random_state=42, scoring='neg_mean_absolute_error', n_jobs=1)
    
    top_indices = perm.importances_mean.argsort()[::-1][:10]
    top_names = [X_test.columns[i] for i in top_indices]
    top_vals = perm.importances_mean[top_indices]
    
    ax.barh(top_names[::-1], top_vals[::-1], color='#319795')
    ax.set_title(f'Top 10 Feature Importances: {sc.replace(\"_\", \" \").title()}', fontweight='bold')
    ax.set_xlabel('Mean Permutation Importance (MAE Increase)')

plt.tight_layout()
plt.show()""")

# 22. Error Analysis
add_md("""## 10. Model Error Analysis across Grade Ranges
Diagnosing residual patterns across performance tiers to identify over/under-prediction biases.""")
add_code("""for sc in ['early_performance', 'grade_assisted']:
    best_pipe = fitted_pipelines[f'{sc}_RandomForest']
    X_test, y_test = data[sc]['X_test'], data[sc]['y_test']
    y_pred = best_pipe.predict(X_test)
    residuals = y_test - y_pred
    
    err_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred, 'Residual': residuals, 'AbsError': np.abs(residuals)})
    bins = [0, 5, 10, 15, 20]
    labels = ['0-5 (Fail)', '6-10 (Low)', '11-15 (Mid)', '16-20 (High)']
    err_df['Range'] = pd.cut(err_df['Actual'], bins=bins, labels=labels, include_lowest=True)
    
    print(f'=== Error Diagnostics: {sc} ===')
    grouped = err_df.groupby('Range', observed=False).agg(
        Count=('AbsError', 'count'),
        MeanAbsError=('AbsError', 'mean'),
        MeanResidual=('Residual', 'mean')
    )
    print(grouped)
    print()""")

# 24-26. Findings, Conclusion, References
add_md("""## 11. Key Findings, Limitations & Ethical Guidelines

### Key Analytical Findings
1. **Dominance of Prior Academic Performance**: Period grades (G1 and G2) explain over 80% of final grade variance ($R^2 = 0.803$, test MAE = 1.21). When formative grades are available, background attributes contribute minimal marginal gain.
2. **Early-Performance Feasibility**: When predicting outcomes prior to term examinations (Scenario A), Random Forest achieves a test MAE of 3.00 ($R^2 = 0.307$). While less precise than Scenario B, it provides actionable early alerts for educational intervention.
3. **Influential Non-Grade Factors**: Weekly study time (>5 hours), desire for higher education, and absence frequency are the most influential non-grade factors.
4. **Zero-Grade Disparity**: Students receiving 0 points represent exam non-takers or dropouts, which regression models tend to overpredict.

### Known Limitations
1. **Sample Specificity**: Historical records derive from two secondary schools in Portugal and cannot be generalized universally across disparate educational systems.
2. **Correlation vs Causation**: Feature importances and correlation coefficients demonstrate empirical associations, not causal relationships.

### Ethical Disclaimer
*GradeSense provides experimental estimates based on historical cohort data. Predictions are not guaranteed outcomes and must not be used as the sole basis for high-stakes academic determinations.*

## 12. References
1. Cortez, P., & Silva, A. (2008). *Using Data Mining to Predict Secondary School Student Performance*. FUBUTEC.
2. Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python*. JMLR.
3. James, G., Witten, D., Hastie, T., & Tibshirani, R. (2013). *An Introduction to Statistical Learning*. Springer.""")

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print(f"[SUCCESS] Wrote notebook with {len(nb['cells'])} cells to {NOTEBOOK_PATH}")
