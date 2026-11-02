# GradeSense: Student Performance Prediction & Academic Analytics

> **VESIT SEM VII &bull; Data Science CA2 Mini Project**  
> *Understand Performance. Discover Insights. Support Better Learning.*

---

## 1. Project Introduction
**GradeSense** is an academic analytics and machine learning decision-support platform designed to forecast secondary school student final numerical performance ($G3$ on a $0\text{--}20$ scale) using supervised regression techniques on the UCI Student Performance benchmark dataset. 

The application demonstrates the complete Data Science lifecycle: from programmatic dataset acquisition and leakage-free feature engineering, to exploratory statistical modeling, cross-validated algorithmic benchmarking, held-out residual diagnosis, and interactive full-stack dashboard reporting.

---

## 2. Problem Statement
Academic failure has severe long-term impacts on student attainment, institutional attrition rates, and public education resources. Conventional institutional assessments identify struggling students only after summative, end-of-term examinations have already concluded, eliminating opportunities for corrective intervention.

By predicting student outcomes numerically:
1. **At the start of the academic cycle** (using background and study proxies without prior grades), counselors can identify vulnerable cohorts for early academic mentorship.
2. **At mid-semester milestones** (incorporating period 1 and period 2 formative grades), academic advisors can provide high-precision grade trajectory interventions.

---

## 3. Project Objectives
1. **Exploratory Data Analysis**: Formulate comprehensive univariate, bivariate, and correlation analyses across demographic, social, and academic variables.
2. **Quality & Anomaly Assessment**: Detect duplicate instances, analyze zero-grade clumping, and evaluate skewness and kurtosis.
3. **Hypothesis Testing**: Conduct formal statistical tests (Welch's two-sample t-test, One-Way ANOVA, Pearson and Spearman correlation analysis) at $\alpha = 0.05$.
4. **Target Leakage Prevention**: Fit all imputation and scaling transformations strictly on training folds via scikit-learn `Pipeline` and `ColumnTransformer`.
5. **Algorithmic Benchmarking**: Compare 6 regression models (Dummy baseline, Linear Regression, Ridge, Random Forest, Gradient Boosting, HistGradient Boosting) across two distinct prediction scenarios.
6. **Error & Residual Analysis**: Evaluate absolute residuals across performance tiers ($0\text{--}5$, $6\text{--}10$, $11\text{--}15$, $16\text{--}20$) on held-out test data.
7. **Feature Interpretability**: Compute permutation feature importance scores without presenting empirical correlations as proof of causality.
8. **Interactive Reporting**: Provide an interactive React/Tailwind/Recharts dashboard and an automated multi-format report generator (PDF, DOCX, PPTX).

---

## 4. Key Features
- **Two Distinct Prediction Scenarios**:
  - **Scenario A (Early-Performance)**: Predicts final grade $G3$ strictly without $G1$ or $G2$ (30 features).
  - **Scenario B (Grade-Assisted)**: Predicts final grade $G3$ using period grades $G1$ and $G2$ alongside background factors (32 features).
- **Interactive Single & Batch Prediction**: Validates input ranges, clamps predictions to $[0, 20]$, and maps scores to official Portuguese academic categories.
- **Dynamic Data Explorer**: Search, filter by school or gender, paginate records, and download CSV exports.
- **Formal Hypothesis Testing Engine**: Automated execution of Welch's t-tests and ANOVA with p-values and plain-English interpretations.
- **Automated College Reports**: Programmatic generation of 10-page mini-project reports in PDF and DOCX, plus an 8-slide PowerPoint presentation.

---

## 5. Technology Stack

### Frontend
- **React.js 18** (Vite build system)
- **Tailwind CSS** (Restrained academic theme)
- **Recharts** (Declarative charts: histograms, bar charts, scatter plots)
- **Lucide React** (Modern feather icons)
- **React Router v6** & **Axios**

### Backend API
- **Python 3.10+ / 3.13**
- **FastAPI** (REST API with automatic Swagger docs)
- **Uvicorn** (ASGI server)
- **Pydantic v2** (Strict schema validation)

### Data Science & Machine Learning
- **Pandas** & **NumPy** (Data manipulation and linear algebra)
- **Scikit-learn** (Pipelines, ColumnTransformer, regression algorithms, permutation importance)
- **SciPy** & **Statsmodels** (Hypothesis testing, descriptive statistics)
- **Matplotlib** & **Seaborn** (Static publication figures)
- **Joblib** (Artifact persistence)

### Document & Presentation Generation
- **ReportLab** (PDF generation)
- **python-docx** (Word documentation)
- **python-pptx** (Presentation slides)

---

## 6. Dataset Source & Attribution
- **Dataset**: Student Performance Data Set (Mathematics Subject, `student-mat.csv`)
- **Source**: [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/320/student+performance)
- **Citation**: P. Cortez and A. Silva. *Using Data Mining to Predict Secondary School Student Performance*. In A. Brito and J. Teixeira Eds., Proceedings of 5th FUture BUsiness TEChnology Conference (FUBUTEC 2008) pp. 5-12, Porto, Portugal, April, 2008, EUROSIS, ISBN 978-9077381-39-7.
- **Dimensions**: 395 student records, 33 attributes (including target $G3$).

Detailed feature descriptions and preprocessing rules are documented in [`data/README.md`](data/README.md).

---

## 7. Project Directory Structure
```
GradeSense/
|-- backend/
|   |-- app/
|   |   |-- routes/
|   |   |   |-- analytics.py       # Grade dist, correlations, statistical tests
|   |   |   |-- data.py            # Summary, records pagination, CSV export
|   |   |   |-- health.py          # API health check
|   |   |   |-- models.py          # Model comparison & error analysis endpoints
|   |   |   `-- predictions.py     # Single & batch prediction endpoints
|   |   |-- services/
|   |   |   |-- analytics_service.py
|   |   |   |-- data_service.py
|   |   |   |-- model_service.py
|   |   |   `-- prediction_service.py
|   |   |-- config.py              # Paths, CORS, API metadata
|   |   |-- main.py                # FastAPI app initialization
|   |   `-- schemas.py             # Pydantic request/response schemas
|   |-- tests/
|   |   |-- test_api.py            # API endpoint integration tests
|   |   |-- test_data.py           # Preprocessing & leakage verification
|   |   `-- test_models.py         # Model training & reload verification
|   `-- requirements.txt
|-- data/
|   |-- raw/
|   |   `-- student-mat.csv        # Primary dataset (395 x 33)
|   |-- processed/
|   |   `-- student_mat_clean.csv
|   `-- README.md                  # Comprehensive dataset documentation
|-- frontend/
|   |-- src/
|   |   |-- components/            # StatCard, ChartCard, CorrelationHeatmap
|   |   |-- layouts/               # Responsive DashboardLayout
|   |   |-- pages/
|   |   |   |-- Overview.jsx       # Page 1: Academic analytics dashboard
|   |   |   |-- DataExplorer.jsx   # Page 2: Filterable records & schema
|   |   |   |-- Analysis.jsx       # Page 3: 8 core visualizations & tests
|   |   |   |-- Prediction.jsx     # Page 4: Interactive prediction form
|   |   |   |-- ModelComparison.jsx# Page 5: Benchmarks across 6 algorithms
|   |   |   `-- Insights.jsx       # Page 6: Findings & policy recommendations
|   |   |-- services/api.js        # Axios API client
|   |   |-- App.jsx
|   |   `-- main.jsx
|   |-- package.json
|   `-- vite.config.js
|-- models/
|   |-- early_performance_model.joblib
|   |-- grade_assisted_model.joblib
|   `-- model_metadata.json
|-- notebooks/
|   `-- GradeSense_Complete_Analysis.ipynb # 26-section executable analysis
|-- outputs/
|   |-- figures/                   # 13 generated figures
|   |-- model_comparison.csv
|   |-- model_comparison.json
|   `-- analytical_summary.json
|-- reports/
|   |-- GradeSense_Mini_Project_Report.pdf
|   |-- GradeSense_Mini_Project_Report.docx
|   |-- GradeSense_Presentation.pptx
|   `-- analytical_summary.md
|-- scripts/
|   `-- make_notebook.py
|-- src/
|   |-- data_preprocessing.py      # ColumnTransformer pipelines
|   |-- train_models.py            # 5-fold CV & model fitting
|   |-- evaluate_models.py         # Residual & error diagnostics
|   `-- generate_reports.py        # PDF, DOCX, PPTX generator
|-- requirements.txt
|-- start.bat                      # Windows launcher script
`-- README.md
```

---

## 8. Windows Installation & Environment Setup

### Prerequisites
- **Python 3.10+** (verified on Python 3.13)
- **Node.js 18+** & **npm** (verified on Node v22.14.0)

### 1. Clone or Extract Project
```powershell
cd D:\VESIT\SEM_VII\DS\GradeSense
```

### 2. Install Python Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

## 9. Model Training & Pipeline Execution

To train all 6 regression models, perform 5-fold cross-validation, save model pipelines, and generate all static figures:

```powershell
# 1. Train models and generate figures
python src/train_models.py

# 2. Run error diagnostics and residual analysis
python src/evaluate_models.py

# 3. Generate college reports (PDF, Word, PowerPoint, Markdown)
python src/generate_reports.py

# 4. Generate Jupyter Notebook
python scripts/make_notebook.py
```

---

## 10. Actual Measured Model Results

Evaluated on 79 held-out test students ($20\%$ test split, fixed `random_state=42`):

| Scenario | Algorithm | CV MAE (5-Fold) | Test MAE | Test RMSE | Test $R^2$ | Status |
|---|---|---|---|---|---|---|
| **Scenario A** (Early) | DummyRegressor (Baseline) | 3.388 | 3.646 | 4.545 | -0.010 | Baseline |
| **Scenario A** (Early) | Linear Regression | 3.576 | 3.395 | 4.198 | 0.141 | Evaluated |
| **Scenario A** (Early) | Ridge Regression ($\alpha=1.0$) | 3.557 | 3.393 | 4.195 | 0.142 | Evaluated |
| **Scenario A** (Early) | **Random Forest** | **2.909** | **3.002** | **3.769** | **0.307** | **Selected Model** |
| **Scenario A** (Early) | Gradient Boosting | 3.117 | 3.111 | 3.937 | 0.244 | Evaluated |
| **Scenario A** (Early) | HistGradient Boosting | 3.164 | 3.190 | 3.963 | 0.234 | Evaluated |
| | | | | | | |
| **Scenario B** (Assisted) | DummyRegressor (Baseline) | 3.388 | 3.646 | 4.545 | -0.010 | Baseline |
| **Scenario B** (Assisted) | Linear Regression | 1.337 | 1.647 | 2.385 | 0.724 | Evaluated |
| **Scenario B** (Assisted) | Ridge Regression ($\alpha=1.0$) | 1.330 | 1.639 | 2.378 | 0.726 | Evaluated |
| **Scenario B** (Assisted) | **Random Forest** | **0.907** | **1.214** | **2.009** | **0.803** | **Selected Model** |
| **Scenario B** (Assisted) | Gradient Boosting | 0.975 | 1.153 | 1.986 | 0.808 | Evaluated |
| **Scenario B** (Assisted) | HistGradient Boosting | 1.061 | 1.232 | 1.936 | 0.817 | Evaluated |

---

## 11. Automated Testing

Execute the automated test suite verifying data integrity, model pipelines, and API routes:

```powershell
python -m pytest backend/tests/ -v -p no:typeguard
```

All 20 test cases pass across:
- `backend/tests/test_data.py`: Verifies zero target leakage, 80/20 partition non-overlap, and ColumnTransformer transformations.
- `backend/tests/test_models.py`: Verifies all 6 estimators, metric calculations, and artifact re-loading.
- `backend/tests/test_api.py`: Tests health checks, dataset summary, pagination, batch prediction, and missing grade validation.

---

## 12. Application Startup (Windows)

### Option 1: Automated Script
Double-click `start.bat` or run:
```cmd
start.bat
```

### Option 2: Manual Terminal Startup
**Terminal 1 (Backend API):**
```powershell
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Swagger Documentation: `http://localhost:8000/docs`

**Terminal 2 (Frontend Dashboard):**
```powershell
cd frontend
npm run dev
```
- Dashboard URL: `http://localhost:5173`

---

## 13. API Documentation Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and model availability |
| `GET` | `/api/dataset/summary` | Records count, columns metadata, and summary stats |
| `GET` | `/api/dataset/records` | Paginated and filtered student records |
| `GET` | `/api/dataset/export/csv` | Download raw dataset CSV file |
| `GET` | `/api/analytics/grades` | $G3$ distribution statistics, histogram bins, and quartiles |
| `GET` | `/api/analytics/correlations` | Pearson, Spearman, or Kendall correlation matrix |
| `GET` | `/api/analytics/insights` | Data-derived analytical findings |
| `GET` | `/api/analytics/statistical-tests` | Formal hypothesis test results (t-test, ANOVA) |
| `GET` | `/api/models/comparison` | Quantitative benchmark metrics across all models |
| `GET` | `/api/models/metadata` | Selected model hyperparameters and feature orders |
| `GET` | `/api/models/error-analysis` | Residual diagnostics and errors across grade ranges |
| `POST` | `/api/predict` | Single student grade prediction (Scenario A or B) |
| `POST` | `/api/predict/batch` | Batch student grade prediction (1 to 500 records) |

---

## 14. Key Analytical Insights & Recommendations
1. **Dominance of Prior Academic Marks**: Period grades $G1$ and $G2$ account for $>80\%$ of variance in final grades ($R^2 = 0.803$). When period grades are known, background attributes provide minor marginal predictive benefit.
2. **Early Prediction Value**: Before any exam grades exist, Random Forest predicts final grades with a Mean Absolute Error of $3.00$ points ($R^2 = 0.307$). This enables counselors to flag at-risk students before the first test is administered.
3. **Study Time Matters**: Students studying $>5$ hours weekly average $11.6/20$ points vs $10.0/20$ for students studying $<2$ hours ($p = 0.023$, One-Way ANOVA).
4. **Higher Education Aspiration**: Students intending to pursue university education achieve significantly higher grades ($10.67$ vs $6.84$, $p < 0.0001$, Welch's t-test).

---

## 15. Limitations & Ethical Guidelines
- **Educational Prototype**: GradeSense is developed as a decision-support prototype and must **never** be used as the sole basis for high-stakes academic determinations.
- **Historical Bias & Generalizability**: The dataset reflects 395 students in Portugal (2008). Patterns should not be assumed to hold unconditionally across institutions with different grading norms.
- **Zero-Grade Dropout Clumping**: Approximately $9.6\%$ of students received score 0 (indicating course abandonment rather than gradual grade degradation).
- **Non-Causal Interpretations**: Correlation does not prove causation; observed factors reflect empirical associations.

---

## 16. Authors & Course Information
- **Course**: VESIT SEM VII — Data Science Mini Project (CA2)
- **Year**: 2026
