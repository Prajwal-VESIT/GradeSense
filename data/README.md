# UCI Student Performance Dataset Documentation

## 1. Dataset Information
- **Dataset Name**: Student Performance Data Set (Mathematics Subject)
- **Primary File**: `student-mat.csv`
- **Official Source**: [UCI Machine Learning Repository - Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance)
- **Citation**: P. Cortez and A. Silva. *Using Data Mining to Predict Secondary School Student Performance*. In A. Brito and J. Teixeira Eds., Proceedings of 5th FUture BUsiness TEChnology Conference (FUBUTEC 2008) pp. 5-12, Porto, Portugal, April, 2008, EUROSIS, ISBN 978-9077381-39-7.

## 2. Dataset Dimensions & Schema
- **Number of Records (Rows)**: 395 students
- **Number of Attributes (Columns)**: 33 features
- **Target Variable**: `G3` — Final grade (numerical score on a 0 to 20 integer scale, according to the Portuguese secondary education grading system)

## 3. Prediction Scenarios & Target Leakage Prevention
To prevent target leakage and reflect real-world educational deployment constraints, the project evaluates two distinct scenarios:
- **Scenario A: Early-Performance Prediction**: Predicts `G3` using demographic, family background, school environment, lifestyle, and proxy attendance variables, **strictly omitting** earlier period grades `G1` and `G2`.
- **Scenario B: Grade-Assisted Prediction**: Predicts `G3` incorporating period grades `G1` (first period) and `G2` (second period) alongside the base attributes.

In both scenarios, `G3` is strictly removed from input feature sets prior to any preprocessing, scaling, or model fitting.

## 4. Feature Dictionary

| # | Attribute | Type | Scale / Range | Description |
|---|-----------|------|---------------|-------------|
| 1 | `school` | Categorical (Binary) | `GP` (Gabriel Pereira), `MS` (Mousinho da Silveira) | Student's school |
| 2 | `sex` | Categorical (Binary) | `F` (female), `M` (male) | Student's sex |
| 3 | `age` | Numeric (Discrete) | 15 to 22 | Student's age in years |
| 4 | `address` | Categorical (Binary) | `U` (urban), `R` (rural) | Home address type |
| 5 | `famsize` | Categorical (Binary) | `LE3` (≤3 members), `GT3` (>3 members) | Family size |
| 6 | `Pstatus` | Categorical (Binary) | `T` (living together), `A` (apart) | Parent's cohabitation status |
| 7 | `Medu` | Numeric (Ordinal) | 0 (none), 1 (primary), 2 (5th-9th grade), 3 (secondary), 4 (higher) | Mother's education |
| 8 | `Fedu` | Numeric (Ordinal) | 0 (none), 1 (primary), 2 (5th-9th grade), 3 (secondary), 4 (higher) | Father's education |
| 9 | `Mjob` | Categorical (Nominal) | `teacher`, `health`, `services`, `at_home`, `other` | Mother's job |
| 10 | `Fjob` | Categorical (Nominal) | `teacher`, `health`, `services`, `at_home`, `other` | Father's job |
| 11 | `reason` | Categorical (Nominal) | `home`, `reputation`, `course`, `other` | Reason for choosing this school |
| 12 | `guardian` | Categorical (Nominal) | `mother`, `father`, `other` | Student's legal guardian |
| 13 | `traveltime` | Numeric (Ordinal) | 1 (<15 min), 2 (15-30 min), 3 (30 min - 1 hr), 4 (>1 hr) | Home to school travel time |
| 14 | `studytime` | Numeric (Ordinal) | 1 (<2 hrs), 2 (2-5 hrs), 3 (5-10 hrs), 4 (>10 hrs) | Weekly study time |
| 15 | `failures` | Numeric (Discrete) | 0 to 4 (number of past class failures) | Past class failures |
| 16 | `schoolsup` | Categorical (Binary) | `yes`, `no` | Extra educational support from school |
| 17 | `famsup` | Categorical (Binary) | `yes`, `no` | Family educational support |
| 18 | `paid` | Categorical (Binary) | `yes`, `no` | Extra paid classes within course subject |
| 19 | `activities` | Categorical (Binary) | `yes`, `no` | Extra-curricular activities |
| 20 | `nursery` | Categorical (Binary) | `yes`, `no` | Attended nursery school |
| 21 | `higher` | Categorical (Binary) | `yes`, `no` | Desires to take higher education |
| 22 | `internet` | Categorical (Binary) | `yes`, `no` | Internet access at home |
| 23 | `romantic` | Categorical (Binary) | `yes`, `no` | With a romantic relationship |
| 24 | `famrel` | Numeric (Ordinal) | 1 (very bad) to 5 (excellent) | Quality of family relationships |
| 25 | `freetime` | Numeric (Ordinal) | 1 (very low) to 5 (very high) | Free time after school |
| 26 | `goout` | Numeric (Ordinal) | 1 (very low) to 5 (very high) | Going out with friends |
| 27 | `Dalc` | Numeric (Ordinal) | 1 (very low) to 5 (very high) | Workday alcohol consumption |
| 28 | `Walc` | Numeric (Ordinal) | 1 (very low) to 5 (very high) | Weekend alcohol consumption |
| 29 | `health` | Numeric (Ordinal) | 1 (very bad) to 5 (very good) | Current health status |
| 30 | `absences` | Numeric (Discrete) | 0 to 93 | Number of school absences |
| 31 | `G1` | Numeric (Discrete) | 0 to 20 | First period grade (Scenario B only) |
| 32 | `G2` | Numeric (Discrete) | 0 to 20 | Second period grade (Scenario B only) |
| 33 | `G3` | Numeric (Discrete) | 0 to 20 | **Target variable**: Final grade |

## 5. Preprocessing Strategy
1. **Numeric Pipeline**:
   - `SimpleImputer(strategy="median")` to handle missing numeric values robustly without outlier distortion.
   - `StandardScaler()` applied to scale features for linear and distance-sensitive models (fitted strictly on training split).
2. **Categorical Pipeline**:
   - `SimpleImputer(strategy="most_frequent")` for categorical missingness.
   - `OneHotEncoder(handle_unknown="ignore", sparse_output=False)` to prevent unseen category failures at inference time.
3. **Data Partitioning**:
   - 80% Train, 20% Test split using fixed `random_state=42`.
   - 5-fold Cross-Validation strictly inside the training set for unbiased model selection.

## 6. Known Dataset Limitations
1. **Sample Size**: 395 records from two secondary schools in the Alentejo region of Portugal. Findings do not generalize universally across disparate educational systems.
2. **Zero-Grade Clumping**: A cluster of students (around 9.6%) scored `G3 = 0`, typically representing non-attendance or dropouts rather than gradual academic regression.
3. **Correlation vs Causality**: Survey self-reports (such as alcohol consumption or study habits) reflect observed associations, not demonstrated causal mechanisms.
