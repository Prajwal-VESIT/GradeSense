# GradeSense — Complete Project Demonstration & Viva Defense Guide

> **Project Name**: GradeSense — Student Performance Prediction and Academic Analytics  
> **Course**: VESIT SEM VII — Data Science Mini Project (CA2)  
> **Tech Stack**: React 18 (Vite, Tailwind, Recharts), FastAPI (Python 3.13, Pydantic v2), Scikit-Learn, SciPy, Statsmodels  
> **Dataset**: UCI Machine Learning Repository — Student Performance (Mathematics, 395 records × 33 attributes)  

---

## Table of Contents
1. [Quick Pre-Demo Checklist (2 Minutes Before Demo)](#1-quick-pre-demo-checklist)
2. [The 30-Second Elevator Pitch (Opening Statement)](#2-the-30-second-elevator-pitch)
3. [Core Architecture & The Two-Scenario Design](#3-core-architecture--the-two-scenario-design)
4. [Step-by-Step UI Walkthrough (What to Click & What to Say)](#4-step-by-step-ui-walkthrough)
   - [Page 1: Overview Dashboard](#page-1-overview-dashboard)
   - [Page 2: Data Explorer](#page-2-data-explorer)
   - [Page 3: Exploratory Data Analysis & Hypothesis Testing](#page-3-exploratory-data-analysis--hypothesis-testing)
   - [Page 4: Interactive Student Prediction](#page-4-interactive-student-prediction)
   - [Page 5: Quantitative Model Comparison](#page-5-quantitative-model-comparison)
   - [Page 6: Insights, Recommendations & Ethics](#page-6-insights-recommendations--ethics)
5. [Code & Pipeline Proof Points (If the Professor asks to see the code)](#5-code--pipeline-proof-points)
6. [Top 15 Viva Questions & Bulletproof Answers](#6-top-15-viva-questions--bulletproof-answers)

---

## 1. Quick Pre-Demo Checklist

Before calling the professor or starting the screen share, execute these commands to verify that both the backend and frontend are live.

### Option A: Automated Launch
Double-click `start.bat` in the project root:
```cmd
start.bat
```

### Option B: Manual Launch (Two Terminals)
**Terminal 1 (Backend API):**
```powershell
cd D:\VESIT\SEM_VII\DS\GradeSense
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
- Verify: Open [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI should show 12 endpoints).

**Terminal 2 (Frontend React App):**
```powershell
cd D:\VESIT\SEM_VII\DS\GradeSense\frontend
npm run dev
```
- Verify: Open [http://localhost:5173](http://localhost:5173).

---

## 2. The 30-Second Elevator Pitch

> *"Good morning/afternoon, Professor. Today I am presenting **GradeSense**, an end-to-end Data Science application for student academic analytics and performance prediction.*  
>  
> *In traditional education, institutional interventions happen only after a student has already failed their final exam. GradeSense solves this by implementing machine learning regression across two distinct educational scenarios: an **Early-Performance scenario** that flags at-risk students at the beginning of the school year without needing prior marks, and a **Grade-Assisted scenario** that incorporates midterm scores for high-precision trajectory forecasts.*  
>  
> *The project adheres to rigorous data science standards: zero target leakage, 5-fold cross-validation, 6 benchmarked regression algorithms, formal hypothesis testing, residual diagnosis across grade tiers, an interactive React dashboard, and automated college report generation in PDF, Word, and PowerPoint."*

---

## 3. Core Architecture & The Two-Scenario Design

Explain this diagram or concept to show architectural maturity:

```
UCI Raw Data (student-mat.csv: 395 x 33)
  ├── 80% Train Set (316 records)  ──> 5-Fold Cross-Validation ──> Model Selection (Random Forest)
  └── 20% Held-Out Test Set (79)   ──> Final Unbiased Evaluation & Residual Error Analysis
```

### Why Two Scenarios?
1. **Scenario A (Early-Performance)**:
   - **Input**: 30 features (Demographics, family education, study time, travel time, failures, alcohol consumption, absences).
   - **Excludes**: $G1$ and $G2$ (earlier period grades) and target $G3$.
   - **Use Case**: Week 1 of school year. Helps counselors identify vulnerable students who need study workshops before tests even begin.
   - **Test Result**: Random Forest achieves **Test MAE = 3.00**, $R^2 = 0.307$.
2. **Scenario B (Grade-Assisted)**:
   - **Input**: 32 features (includes $G1$ and $G2$ alongside all background features).
   - **Use Case**: Mid-semester academic advising after first-term evaluations.
   - **Test Result**: Random Forest achieves **Test MAE = 1.21**, $R^2 = 0.803$ (an error reduction of nearly $60\%$).

### Target Leakage Prevention:
- Target $G3$ is strictly removed from feature matrices before any preprocessing.
- `ColumnTransformer` (`SimpleImputer` + `StandardScaler` / `OneHotEncoder`) is fitted **strictly on training folds** and only applied to test sets or user inputs during inference.

---

## 4. Step-by-Step UI Walkthrough

Follow this exact sequence while sharing your screen.

---

### Page 1: Overview Dashboard
**URL**: `http://localhost:5173/`

#### What to Show:
1. **Top KPI Cards**:
   - Total Student Cohort: **395** (UCI benchmark).
   - Average Final Grade: **10.42 / 20** (Median 11.0, Std Dev 4.58).
   - Best Early Model: **Random Forest (3.00 MAE)**.
   - Best Grade-Assisted Model: **Random Forest (1.21 MAE)**.
2. **Scenario Comparison Cards**:
   - Point out the side-by-side comparison explaining the difference between Early and Grade-Assisted predictions.
3. **Final Grade Distribution Chart (Recharts)**:
   - Point to the histogram. Notice the bell curve centered around 10–11 points, and point out the spike at $G3 = 0$.
4. **Interactive Correlation Heatmap**:
   - Hover over cells to show correlation values dynamically.

#### What to Say:
> *"Here on the Overview Dashboard, all KPI cards and charts are loaded dynamically from our FastAPI backend.*  
>  
> *Notice the G3 distribution: in Portugal's secondary education, the passing grade is 10 out of 20. Our cohort mean is 10.42. Notice the significant spike at G3 = 0, where 38 students (9.6% of the cohort) scored zero. Our error analysis proved that these are exam dropouts or non-attendees rather than gradual cognitive declines.*  
>  
> *In our Correlation Heatmap, you can see that prior grades G1 and G2 have overwhelming positive correlation (r = 0.80 and 0.91), while past failures (r = -0.36) and absences show negative associations."*

---

### Page 2: Data Explorer
**URL**: `http://localhost:5173/explorer`

#### What to Show:
1. **Interactive Filter & Search**:
   - Type `"GP"` or filter by School `"MS"` and Sex `"F"`.
   - Show instant server-side pagination and record count updating.
2. **Schema & Missing Values Tab**:
   - Click the **"Schema & Missing Values"** tab.
   - Show all 33 columns, data types, and highlight **0% missing values across all columns**.
3. **Descriptive Statistics Tab**:
   - Click **"Descriptive Statistics"** to show Mean, Std, Median, Q1, Q3, Min, Max for every feature.
4. **CSV Export**:
   - Click the **"Export CSV"** button to show that it triggers a real data export.

#### What to Say:
> *"The Data Explorer provides institutional transparency. It supports server-side pagination, free-text search, and multi-attribute filtering.*  
>  
> *In the Schema audit tab, we verify that the UCI student-mat dataset contains 395 rows and 33 attributes with zero missing cells and zero duplicate records.*  
>  
> *We can also export the sanitized dataset directly to CSV for external auditing."*

---

### Page 3: Exploratory Data Analysis & Hypothesis Testing
**URL**: `http://localhost:5173/analysis`

#### What to Show:
1. **Visualization 1 & 2**:
   - G3 Distribution + G3 by Study Time tiers (`<2h`, `2-5h`, `5-10h`, `>10h`).
2. **Visualization 4**:
   - Scatter plots of $G1$ vs $G3$ and $G2$ vs $G3$ with regression trend lines.
3. **Visualization 5**:
   - Absences vs Final Grade.
4. **Visualization 6 & 8**:
   - Model benchmark comparison bar chart and Permutation Feature Importance.
5. **Data Interpretations**:
   - Point out the data-derived statistical interpretation box beneath each visualization.

#### What to Say:
> *"In this section, we present eight meaningful statistical visualizations alongside formal hypothesis tests.*  
>  
> *In Visualization 2, you can observe that students studying more than 10 hours weekly achieve an average final grade of 11.6, compared to 10.0 for those studying less than 2 hours. We conducted a One-Way ANOVA test which proved this difference is statistically significant with F = 3.20 and p = 0.023.*  
>  
> *Similarly, for students desiring higher education, our Welch's two-sample t-test yielded t = 4.41 and p = 4.8e-5, proving a highly significant grade advantage (10.67 vs 6.84).*  
>  
> *In Visualization 8, our Permutation Feature Importance reveals that in Scenario A, weekly study time, past failures, and mother's education are the most important predictors, whereas in Scenario B, earlier term grades G1 and G2 overwhelmingly dominate."*

---

### Page 4: Interactive Student Prediction
**URL**: `http://localhost:5173/predict`

#### What to Show:
1. **Test Scenario A (Early-Performance)**:
   - Notice that the $G1$ and $G2$ inputs are **hidden** to prevent target leakage.
   - Click the **"Average Student"** quick preset.
   - Click **"Run Prediction"**.
   - Show the result card: Predicted grade (e.g., `11.13 / 20`), Category (`Sufficient (Pass)`), Model used (`RandomForest`), Pipeline Test MAE ($\pm 3.00$), and the cautious interpretation box.
2. **Test Scenario B (Grade-Assisted)**:
   - Switch to the **"Scenario B: Grade-Assisted"** tab.
   - Notice that $G1$ and $G2$ input fields now appear.
   - Click the **"High Achiever Profile"** preset ($G1=17, G2=18$).
   - Click **"Run Prediction"**.
   - Show the updated grade: e.g., `17.85 / 20` (`Excellent (Distinction)`), with a much tighter error margin of $\pm 1.21$ points.
3. **Demonstrate Input Validation**:
   - Change age to `25` or absences to `150` to show live validation error constraints.
4. **Ethical Disclaimer**:
   - Point to the ethical disclaimer stating that predictions are experimental estimates, not guaranteed outcomes.

#### What to Say:
> *"This is the core predictive engine. Let us test Scenario A first. Notice that G1 and G2 are completely absent from the form. When I click 'Run Prediction', the inputs are packaged into a Pydantic schema, passed to our backend, scaled and encoded through the trained ColumnTransformer, and fed to our Random Forest pipeline.*  
>  
> *Now, if we switch to Scenario B where midterm evaluations G1 and G2 are known, our model incorporates them. For a student with G1=17 and G2=18, the model projects 17.85 with Distinction, backed by an evaluation MAE of only 1.21 points.*  
>  
> *Notice our system never gives deterministic claims—it translates the numerical grade into official Portuguese educational categories (Distinction, Good, Satisfactory, Sufficient, and Insufficient) and provides a cautious, data-supported interpretation."*

---

### Page 5: Quantitative Model Comparison
**URL**: `http://localhost:5173/models`

#### What to Show:
1. **The 6 Benchmark Models**:
   - DummyRegressor, Linear Regression, Ridge ($\alpha=1.0$), Random Forest, Gradient Boosting, HistGradient Boosting.
2. **Metrics Table**:
   - Point out CV MAE, Test MAE, Test MSE, Test RMSE, and Test $R^2$.
3. **Scenario Switcher**:
   - Toggle between Scenario A and Scenario B to show how all table rows and charts update dynamically from `outputs/model_comparison.json`.
4. **Error Analysis across Grade Tiers**:
   - Scroll down to the **"Error Analysis Across Performance Tiers"** table.
   - Show how the model behaves across:
     - $0\text{--}5$ (Fail): Overpredicting due to zero-grade dropouts.
     - $6\text{--}10$ (Low): Moderate errors.
     - $11\text{--}15$ (Mid): Highest accuracy (MAE $\approx 0.70$ in Scenario B).
     - $16\text{--}20$ (High): High accuracy.
5. **Metrics Glossary**:
   - Point to the bottom cards explaining MAE, RMSE, MSE, and $R^2$.

#### What to Say:
> *"Here we compare six distinct regression algorithms under identical experimental conditions: an 80/20 train/test split with fixed random seed 42, and 5-fold cross-validation on the training set.*  
>  
> *Random Forest was selected as the champion model in both scenarios because it yielded the lowest 5-fold CV MAE (2.909 in Scenario A and 0.907 in Scenario B). When tested on the 79 held-out students, it confirmed its superiority with a Test MAE of 3.002 and 1.214.*  
>  
> *In our Residual Error Analysis table, notice that the model achieves its best precision on mid-to-high scoring students (MAE < 0.75 points in Scenario B). The largest errors occur in the 0–5 tier, where students who scored zero inflate the residual because standard regression models expect continuous distributions."*

---

### Page 6: Insights, Recommendations & Ethics
**URL**: `http://localhost:5173/insights`

#### What to Show:
1. **Evidence-Based Institutional Recommendations**:
   - Early Study-Skill Workshops (targeting students with $<2$ hours study time).
   - Mid-Semester Formative Milestones (using $G1$ as an early trigger for tutoring).
   - Nuanced Absenteeism Monitoring (differentiating sporadic vs chronic dropout absences).
2. **Methodological Limitations**:
   - Specificity to two Portuguese schools; non-causal nature of survey correlations; zero-grade dropout skew.
3. **Ethical Governance Banner**:
   - Non-discriminatory use clause (sensitive features like parental marital status must never be used for punitive decisions).

#### What to Say:
> *"Finally, Data Science must translate into actionable policy without causing harm. On this page, we formulate three data-driven recommendations:*  
>  
> *First, institutions should establish study-skill workshops early in the semester, since study time is one of the strongest non-grade predictors.*  
> *Second, schools must treat G1 not as a mere assessment, but as a critical counseling trigger, since earlier grades account for 80% of final variance.*  
> *Third, we include a strict ethical governance framework: GradeSense must serve purely as an auxiliary support tool to expand tutoring, never to automate adverse or discriminatory decisions against students."*

---

## 5. Code & Pipeline Proof Points

If the professor asks you: *"Show me the code, the tests, the generated reports, or the notebook"*, follow this guide:

### A. Run Automated Tests Live in Front of the Professor:
Open a terminal in the project directory and run:
```powershell
python -m pytest backend/tests/ -v -p no:typeguard
```
**Output**: `20 passed in ~7s` (covers data leakage tests, model reloads, API routes).

### B. Show the Leakage-Free Preprocessing Pipeline:
Open `src/data_preprocessing.py`:
- Point to `build_preprocessor()`:
  - `SimpleImputer(strategy="median")` + `StandardScaler()` for numeric features.
  - `SimpleImputer(strategy="most_frequent")` + `OneHotEncoder(handle_unknown="ignore")` for categorical features.
- Point to `prepare_data()`:
  - Shows `train_test_split(..., test_size=0.2, random_state=42)` and explicit separation of feature sets for Early-Performance vs Grade-Assisted scenarios.

### C. Show the Generated Reports:
Open the `reports/` folder in Windows File Explorer:
- [`GradeSense_Mini_Project_Report.pdf`](file:///d:/VESIT/SEM_VII/DS/GradeSense/reports/GradeSense_Mini_Project_Report.pdf): 10-page formatted PDF report with embedded figures and metric tables.
- [`GradeSense_Mini_Project_Report.docx`](file:///d:/VESIT/SEM_VII/DS/GradeSense/reports/GradeSense_Mini_Project_Report.docx): Professional Microsoft Word report.
- [`GradeSense_Presentation.pptx`](file:///d:/VESIT/SEM_VII/DS/GradeSense/reports/GradeSense_Presentation.pptx): 10-slide PowerPoint presentation with actual figures.

### D. Show the Jupyter Notebook:
Open `notebooks/GradeSense_Complete_Analysis.ipynb`:
- Contains all 26 required sections: problem formulation, data loading, quality inspection, univariate/bivariate analysis, hypothesis testing, pipeline construction, model comparison, residual diagnostics, and conclusions.

---

## 6. Top 15 Viva Questions & Bulletproof Answers

### Q1: Why did you frame this as a Regression problem rather than Classification?
**Answer**:  
*"Secondary school grades on the 0–20 scale represent continuous academic achievement. Framing it as regression preserves fine-grained performance data (e.g., distinguishing a grade of 11 from 18, which binary pass/fail ignores). However, for educational reporting, our system also post-processes the numerical prediction into official Portuguese academic categories (Distinction, Good, Satisfactory, Sufficient, and Insufficient)."*

---

### Q2: What is Target Leakage, and how did you prevent it?
**Answer**:  
*"Target leakage happens when information from the target variable is inadvertently used during training or feature transformation, producing artificially high performance that fails in production. We prevented it in three ways:*  
*1. Target $G3$ is strictly removed from all predictor sets before splitting.*  
*2. In Scenario A, earlier grades $G1$ and $G2$ are completely excluded.*  
*3. All imputers and scalers in our `ColumnTransformer` are fitted strictly on the 80% training set and only transformed onto the test set."*

---

### Q3: Why is MAE your primary metric instead of MSE or RMSE?
**Answer**:  
*"MAE (Mean Absolute Error) is directly interpretable in the original units—grade points on a 0–20 scale. An MAE of 1.21 means our predictions deviate by an average of 1.21 marks. While we also report RMSE and MSE to penalize extreme errors, MAE provides the most intuitive metric for educational counselors."*

---

### Q4: Why did Random Forest outperform Linear and Ridge Regression?
**Answer**:  
*"Academic performance involves non-linear interactions and threshold effects. For example, studying more than 5 hours has diminishing marginal returns, and past failures interact non-linearly with absences. Random Forest's ensemble of 100 decision trees naturally captures feature interactions and non-linear boundaries without requiring manual polynomial feature engineering."*

---

### Q5: Can $R^2$ be negative? What does it mean for your Dummy baseline?
**Answer**:  
*"Yes. In scikit-learn, $R^2$ compares the model's residual sum of squares to a horizontal line predicting the training mean. On an unseen test set, if a model performs worse than simply predicting the mean, $R^2$ becomes negative. In our evaluation, the DummyRegressor yielded $R^2 = -0.010$, proving that predicting a constant mean fails to generalize on test data, whereas our Random Forest achieved $R^2 = 0.803$ in Scenario B."*

---

### Q6: Why is there an anomalous spike at $G3 = 0$?
**Answer**:  
*"In the Portuguese education system, students who abandon a course or fail to attend the final examination receive a grade of 0. In our dataset, 38 students (9.6%) received a 0. These are administrative zeros rather than genuine academic ratings, which explains why regression models tend to overpredict this specific tier."*

---

### Q7: Why did you use 5-Fold Cross-Validation on the training set?
**Answer**:  
*"Evaluating models repeatedly against the test set causes test-set leakage, where hyperparameters overfit to the test sample. By performing 5-fold cross-validation strictly on the 316 training samples, we selected the best estimator (Random Forest) in an unbiased manner, preserving the 79 test samples as a pure, untouched benchmark."*

---

### Q8: How does your pipeline handle unseen categories in production?
**Answer**:  
*"We configured `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`. If a student record in production contains an unseen category, the encoder assigns all zero columns for that feature rather than crashing the API."*

---

### Q9: Why did you use Welch's t-test instead of Student's t-test?
**Answer**:  
*"Student's t-test assumes equal variances between groups (homoscedasticity). In our data, students desiring higher education have a different variance and sample size ($n=349$) compared to those who do not ($n=46$). Welch's t-test does not assume equal variances, making it statistically robust."*

---

### Q10: How did you compute Permutation Feature Importance?
**Answer**:  
*"Unlike built-in tree Gini importance, which can be biased toward high-cardinality numerical variables, permutation importance is evaluated on the held-out test set. We shuffle each feature 15 times and measure the drop in test MAE. The greater the error increase when a feature is scrambled, the higher its empirical predictive importance."*

---

### Q11: Does your model imply that drinking alcohol or lack of internet causes low grades?
**Answer**:  
*"No. In our project documentation, dashboard, and reports, we explicitly emphasize that correlation does not imply causation. Observable relationships represent empirical associations within this specific sample, not verified causal mechanisms."*

---

### Q12: Why did you build the backend in FastAPI instead of Flask?
**Answer**:  
*"FastAPI provides automatic interactive Swagger documentation (`/docs`), built-in asynchronous performance, and native integration with Pydantic v2 for strict type checking and range validation. This ensures invalid student feature inputs are rejected with clear 422 HTTP responses before touching the ML model."*

---

### Q13: Why did you choose React with Tailwind over Streamlit?
**Answer**:  
*"Streamlit re-runs the entire Python script on every user interaction, making it slow and non-modular. A decoupled architecture with a React frontend and FastAPI backend reflects professional software engineering: the frontend provides sub-millisecond client-side routing, responsive layouts, and interactive Recharts visualizations, while the backend operates as a scalable REST microservice."*

---

### Q14: What are the main limitations of this dataset?
**Answer**:  
*"1. Sample Size: 395 instances collected in 2008 from two secondary schools in the Alentejo region of Portugal. Findings may not generalize universally across different countries or university curricula.  
2. Zero-grade dropout skew: Administrative dropouts distort linear regression fits.  
3. Survey self-reporting: Attributes like alcohol consumption and study time are self-reported by students."*

---

### Q15: What ethical safeguards did you implement in GradeSense?
**Answer**:  
*"We implemented three safeguards:  
1. No high-stakes automation: Predictions are clearly labeled as experimental estimates for mentorship counseling, never for disciplinary actions.  
2. Demographic non-discrimination: Institutional recommendations explicitly forbid penalizing students based on family structure, parents' marital status, or gender.  
3. Transparent model interpretability: Every prediction displays the scenario used, pipeline test MAE, and qualitative category boundaries."*

---

## 7. Summary of Artifacts Created in this Project

```
GradeSense/
├── DEMO_GUIDE.md                                <== THIS DEMO & VIVA GUIDE
├── README.md                                    <== FULL PROJECT DOCUMENTATION
├── start.bat                                    <== 1-CLICK WINDOWS LAUNCHER
│
├── frontend/                                    <== REACT 18 + VITE + TAILWIND + RECHARTS
│   ├── src/pages/Overview.jsx                   <== Page 1: Dashboard
│   ├── src/pages/DataExplorer.jsx               <== Page 2: Filterable Records
│   ├── src/pages/Analysis.jsx                   <== Page 3: 8 Core Visualizations
│   ├── src/pages/Prediction.jsx                 <== Page 4: Interactive Prediction Form
│   ├── src/pages/ModelComparison.jsx            <== Page 5: 6 Algorithms Benchmark
│   └── src/pages/Insights.jsx                   <== Page 6: Findings & Recommendations
│
├── backend/                                     <== FASTAPI REST MICROSERVICE
│   ├── app/main.py                              <== FastAPI Entrypoint & CORS
│   ├── app/routes/                              <== 12 API Endpoints
│   ├── app/schemas.py                           <== Pydantic Validation Schemas
│   └── tests/                                   <== 20 Automated Tests (100% Pass)
│
├── models/                                      <== SAVED SCIKIT-LEARN PIPELINES
│   ├── early_performance_model.joblib          <== Scenario A Pipeline
│   ├── grade_assisted_model.joblib             <== Scenario B Pipeline
│   └── model_metadata.json                      <== Hyperparameters & Metrics
│
├── outputs/                                     <== EXPERIMENTAL OUTPUTS
│   ├── figures/                                 <== 13 Publication Figures (.png)
│   ├── model_comparison.json                    <== Benchmark Results
│   └── evaluation_results.json                  <== Error Analysis
│
├── reports/                                     <== AUTOMATED COLLEGE DELIVERABLES
│   ├── GradeSense_Mini_Project_Report.pdf       <== 10-Page College Report (PDF)
│   ├── GradeSense_Mini_Project_Report.docx      <== 10-Page Word Report (.docx)
│   ├── GradeSense_Presentation.pptx             <== 10-Slide PowerPoint (.pptx)
│   └── analytical_summary.md                    <== Markdown Summary
│
└── notebooks/
    └── GradeSense_Complete_Analysis.ipynb       <== 26-Section Executable Notebook
```
