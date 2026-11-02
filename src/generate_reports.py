"""
GradeSense - Report Generation Module
=======================================
Generates comprehensive reports in multiple formats:
  - JSON analytical summary
  - Markdown reports  (analytical_summary.md + full project report)
  - Word document  (.docx)
  - PDF document  (.pdf)
  - PowerPoint presentation  (.pptx)

Author : [Student Name]
Course : VESIT SEM VII — Data Science
"""

import json
import datetime
from pathlib import Path

import pandas as pd

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.data_preprocessing import PROJECT_ROOT, OUTPUTS_DIR, MODELS_DIR

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR = OUTPUTS_DIR / "figures"


# ---------------------------------------------------------------------------
# Load all results
# ---------------------------------------------------------------------------
def load_results() -> dict:
    """Load model comparison, evaluation results, and metadata."""
    results = {}

    # Model comparison
    comp_path = OUTPUTS_DIR / "model_comparison.json"
    if comp_path.exists():
        with open(comp_path) as f:
            results["model_comparison"] = json.load(f)

    # Evaluation results
    eval_path = OUTPUTS_DIR / "evaluation_results.json"
    if eval_path.exists():
        with open(eval_path) as f:
            results["evaluation"] = json.load(f)

    # Model metadata
    meta_path = MODELS_DIR / "model_metadata.json"
    if meta_path.exists():
        with open(meta_path) as f:
            results["metadata"] = json.load(f)

    # Preprocessing report
    prep_path = OUTPUTS_DIR / "preprocessing_report.json"
    if prep_path.exists():
        with open(prep_path) as f:
            results["preprocessing"] = json.load(f)

    # Feature importance
    for scenario in ["early_performance", "grade_assisted"]:
        imp_path = OUTPUTS_DIR / f"feature_importance_{scenario}.csv"
        if imp_path.exists():
            results[f"importance_{scenario}"] = pd.read_csv(imp_path).to_dict(orient="records")

    return results


# ---------------------------------------------------------------------------
# JSON analytical summary
# ---------------------------------------------------------------------------
def generate_json_summary(results: dict):
    """Save outputs/analytical_summary.json."""
    summary = {
        "project": "GradeSense — Student Performance Prediction",
        "generated_at": datetime.datetime.now().isoformat(),
        "dataset": {
            "name": "UCI Student Performance (Mathematics)",
            "source": "https://archive.ics.uci.edu/dataset/320/student+performance",
            "target": "G3 (final grade, 0–20)",
        },
        "scenarios": {},
    }

    meta = results.get("metadata", {})
    eval_data = results.get("evaluation", {})

    for scenario in ["early_performance", "grade_assisted"]:
        s_meta = meta.get(scenario, {})
        s_eval = eval_data.get(scenario, {})
        summary["scenarios"][scenario] = {
            "best_model": s_meta.get("best_model", "N/A"),
            "test_metrics": s_eval.get("test_metrics", {}),
            "all_models": s_meta.get("models", {}),
            "error_analysis": {
                "large_error_count": s_eval.get("large_error_count", "N/A"),
                "error_by_range": s_eval.get("error_by_range", []),
            },
        }

    path = OUTPUTS_DIR / "analytical_summary.json"
    with open(path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[SAVE] {path}")
    return summary


# ---------------------------------------------------------------------------
# Markdown analytical summary
# ---------------------------------------------------------------------------
def generate_markdown_summary(results: dict):
    """Generate reports/analytical_summary.md."""
    meta = results.get("metadata", {})
    eval_data = results.get("evaluation", {})
    prep = results.get("preprocessing", {})

    lines = [
        "# GradeSense — Analytical Summary",
        "",
        f"*Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "## 1. Dataset Overview",
        "",
        "- **Dataset**: UCI Student Performance (Mathematics)",
        "- **Source**: https://archive.ics.uci.edu/dataset/320/student+performance",
        f"- **Shape**: {prep.get('shape', {}).get('rows', '?')} rows × {prep.get('shape', {}).get('columns', '?')} columns",
        f"- **Duplicates**: {prep.get('duplicates', '?')}",
        f"- **Missing values**: {'None' if not prep.get('missing_values') else json.dumps(prep.get('missing_values'))}",
        "- **Target variable**: G3 (final grade, 0–20 scale)",
        "",
        "## 2. Prediction Scenarios",
        "",
        "| Scenario | Description |",
        "|----------|-------------|",
        "| Early Performance | Predict G3 **without** G1, G2 (no prior exam grades) |",
        "| Grade Assisted | Predict G3 **with** G1, G2 (prior exam grades available) |",
        "",
    ]

    # Per-scenario results
    for scenario in ["early_performance", "grade_assisted"]:
        s_meta = meta.get(scenario, {})
        s_eval = eval_data.get(scenario, {})
        best = s_meta.get("best_model", "N/A")
        tm = s_eval.get("test_metrics", {})

        lines.append(f"## 3. Results — {scenario.replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"**Best Model**: {best}")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        for k, v in tm.items():
            lines.append(f"| {k} | {v} |")
        lines.append("")

        # All models comparison table
        models = s_meta.get("models", {})
        if models:
            lines.append("### All Models Comparison")
            lines.append("")
            lines.append("| Model | CV MAE | Test MAE | Test RMSE | Test R² |")
            lines.append("|-------|--------|----------|-----------|---------|")
            for mname, mvals in models.items():
                lines.append(
                    f"| {mname} | {mvals.get('cv_MAE', '')} | "
                    f"{mvals.get('test_MAE', '')} | {mvals.get('test_RMSE', '')} | "
                    f"{mvals.get('test_R2', '')} |"
                )
            lines.append("")

        # Error analysis
        err_range = s_eval.get("error_by_range", [])
        if err_range:
            lines.append("### Error by Grade Range")
            lines.append("")
            lines.append("| Grade Range | Count | Mean |err| | Std |err| |")
            lines.append("|-------------|-------|-----------|----------|")
            for row in err_range:
                lines.append(
                    f"| {row.get('grade_range', '')} | {row.get('count', '')} | "
                    f"{row.get('mean_abs_error', ''):.3f} | {row.get('std_abs_error', ''):.3f} |"
                    if isinstance(row.get('mean_abs_error'), (int, float)) else
                    f"| {row.get('grade_range', '')} | {row.get('count', '')} | "
                    f"{row.get('mean_abs_error', '')} | {row.get('std_abs_error', '')} |"
                )
            lines.append("")

        # Top features
        imp_key = f"importance_{scenario}"
        if imp_key in results:
            imp = results[imp_key][:10]
            lines.append("### Top-10 Important Features (Permutation Importance)")
            lines.append("")
            lines.append("| Rank | Feature | Importance |")
            lines.append("|------|---------|------------|")
            for i, row in enumerate(imp, 1):
                lines.append(f"| {i} | {row['feature']} | {row['importance_mean']:.4f} |")
            lines.append("")

    lines.extend([
        "## 4. Figures",
        "",
        "All figures saved in `outputs/figures/`:",
        "",
        "- `grade_distribution.png` — distribution of G3",
        "- `correlation_heatmap.png` — numeric feature correlations",
        "- `scatter_G1_G2_vs_G3.png` — G1 and G2 scatter vs G3",
        "- `boxplots_G3_by_category.png` — G3 distributions by category",
        "- `model_comparison.png` — bar chart comparing all models",
        "- `actual_vs_pred_*.png` — actual vs predicted scatter",
        "- `residuals_*.png` — residual analysis plots",
        "- `feature_importance_*.png` — permutation importance charts",
        "",
        "## 5. Conclusions",
        "",
        "1. **Grade-assisted scenario** vastly outperforms early-performance, confirming ",
        "   that G1 and G2 are the strongest predictors of G3.",
        "2. **Early-performance** is more challenging but still useful for identifying ",
        "   at-risk students before any exams are graded.",
        "3. **Failure cases** (G3 = 0) are hardest to predict accurately.",
        "",
        "---",
        "*GradeSense — VESIT SEM VII Data Science Mini Project*",
    ])

    md_text = "\n".join(lines)
    path = REPORTS_DIR / "analytical_summary.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(md_text)
    print(f"[SAVE] {path}")
    return md_text


# ---------------------------------------------------------------------------
# Full project report (Markdown)
# ---------------------------------------------------------------------------
def generate_project_report_md(results: dict):
    """Generate reports/GradeSense_Mini_Project_Report.md."""
    meta = results.get("metadata", {})
    eval_data = results.get("evaluation", {})
    prep = results.get("preprocessing", {})

    sections = []
    sections.append("# GradeSense — Student Performance Prediction")
    sections.append("## Mini Project Report")
    sections.append("")
    sections.append("**Course**: Data Science (SEM VII)")
    sections.append("**College**: VESIT")
    sections.append(f"**Date**: {datetime.datetime.now().strftime('%B %Y')}")
    sections.append("**Team Members**: [Student Name 1], [Student Name 2], [Student Name 3]")
    sections.append("")
    sections.append("---")
    sections.append("")

    # Abstract
    sections.append("## Abstract")
    sections.append("")
    sections.append(
        "This project applies machine learning regression techniques to predict "
        "student final grades (G3) in Mathematics using the UCI Student Performance "
        "dataset. We explore two scenarios: (A) Early Performance prediction without "
        "prior exam scores, and (B) Grade-Assisted prediction leveraging first and "
        "second period grades. Multiple models are trained, cross-validated, and "
        "compared using MAE, RMSE, and R² metrics."
    )
    sections.append("")

    # Chapter 1: Introduction
    sections.append("## 1. Introduction")
    sections.append("")
    sections.append("### 1.1 Problem Statement")
    sections.append(
        "Predicting student academic performance is crucial for early intervention. "
        "This project aims to build predictive models that estimate a student's final "
        "Mathematics grade based on demographic, social, and school-related features."
    )
    sections.append("")
    sections.append("### 1.2 Objectives")
    sections.append("1. Preprocess and explore the UCI Student Performance dataset.")
    sections.append("2. Train and compare multiple regression models.")
    sections.append("3. Evaluate models under two scenarios (with and without prior grades).")
    sections.append("4. Identify the most important features for performance prediction.")
    sections.append("5. Deploy a simple prediction API.")
    sections.append("")

    # Chapter 2: Dataset
    sections.append("## 2. Dataset Description")
    sections.append("")
    sections.append("- **Name**: Student Performance Data Set")
    sections.append("- **Source**: [UCI ML Repository](https://archive.ics.uci.edu/dataset/320/student+performance)")
    sections.append(f"- **Records**: {prep.get('shape', {}).get('rows', '395')}")
    sections.append(f"- **Features**: {prep.get('shape', {}).get('columns', '33')} (including target G3)")
    sections.append("- **Target**: G3 — final grade (0 to 20)")
    sections.append("")
    sections.append("### 2.1 Feature Categories")
    sections.append("")
    sections.append("| Category | Features |")
    sections.append("|----------|----------|")
    sections.append("| Demographic | age, sex, address, famsize, Pstatus |")
    sections.append("| Family | Medu, Fedu, Mjob, Fjob, guardian, famrel |")
    sections.append("| School | school, reason, traveltime, studytime, failures, schoolsup, paid |")
    sections.append("| Lifestyle | activities, nursery, higher, internet, romantic, freetime, goout |")
    sections.append("| Health | health, Dalc, Walc |")
    sections.append("| Academic | absences, G1, G2, **G3 (target)** |")
    sections.append("")

    # Chapter 3: Methodology
    sections.append("## 3. Methodology")
    sections.append("")
    sections.append("### 3.1 Preprocessing Pipeline")
    sections.append("- **Numeric features**: Median imputation → Standard scaling")
    sections.append("- **Categorical features**: Most-frequent imputation → One-hot encoding")
    sections.append("- All transformations applied via `sklearn.pipeline.Pipeline` to prevent data leakage.")
    sections.append("")
    sections.append("### 3.2 Train/Test Split")
    sections.append("- 80/20 split with `random_state=42`")
    sections.append("- 5-fold cross-validation on training set for model selection")
    sections.append("")
    sections.append("### 3.3 Models Trained")
    sections.append("1. **DummyRegressor** (baseline — predicts mean)")
    sections.append("2. **Linear Regression**")
    sections.append("3. **Ridge Regression** (α = 1.0)")
    sections.append("4. **Random Forest** (100 trees)")
    sections.append("5. **Gradient Boosting** (100 rounds)")
    sections.append("6. **Histogram Gradient Boosting**")
    sections.append("")

    # Chapter 4: Results
    sections.append("## 4. Results")
    sections.append("")

    for scenario in ["early_performance", "grade_assisted"]:
        s_meta = meta.get(scenario, {})
        s_eval = eval_data.get(scenario, {})
        best = s_meta.get("best_model", "N/A")
        tm = s_eval.get("test_metrics", {})

        scenario_title = scenario.replace("_", " ").title()
        sections.append(f"### 4.{'1' if scenario == 'early_performance' else '2'} {scenario_title}")
        sections.append("")
        sections.append(f"**Best Model**: `{best}`")
        sections.append("")

        models = s_meta.get("models", {})
        if models:
            sections.append("| Model | CV MAE | Test MAE | Test RMSE | Test R² |")
            sections.append("|-------|--------|----------|-----------|---------|")
            for mname, mv in models.items():
                marker = " ★" if mname == best else ""
                sections.append(
                    f"| {mname}{marker} | {mv.get('cv_MAE','')} | "
                    f"{mv.get('test_MAE','')} | {mv.get('test_RMSE','')} | "
                    f"{mv.get('test_R2','')} |"
                )
            sections.append("")

        if tm:
            sections.append(f"**Best model test performance**: MAE = {tm.get('MAE','?')}, "
                            f"RMSE = {tm.get('RMSE','?')}, R² = {tm.get('R2','?')}")
            sections.append("")

    # Chapter 5: Error Analysis
    sections.append("## 5. Error Analysis")
    sections.append("")
    for scenario in ["early_performance", "grade_assisted"]:
        s_eval = eval_data.get(scenario, {})
        sections.append(f"### {scenario.replace('_',' ').title()}")
        sections.append(f"- Large errors (|error| > 3): **{s_eval.get('large_error_count', '?')}** cases")
        err_range = s_eval.get("error_by_range", [])
        if err_range:
            sections.append("")
            sections.append("| Grade Range | Count | Mean Abs Error |")
            sections.append("|-------------|-------|----------------|")
            for row in err_range:
                mae_val = row.get("mean_abs_error", "")
                mae_str = f"{mae_val:.3f}" if isinstance(mae_val, (int, float)) else str(mae_val)
                sections.append(f"| {row.get('grade_range','')} | {row.get('count','')} | {mae_str} |")
        sections.append("")

    # Chapter 6: Feature Importance
    sections.append("## 6. Feature Importance")
    sections.append("")
    for scenario in ["early_performance", "grade_assisted"]:
        imp_key = f"importance_{scenario}"
        if imp_key in results:
            imp = results[imp_key][:10]
            sections.append(f"### {scenario.replace('_',' ').title()} — Top-10")
            sections.append("")
            sections.append("| Rank | Feature | Importance |")
            sections.append("|------|---------|------------|")
            for i, row in enumerate(imp, 1):
                sections.append(f"| {i} | {row['feature']} | {row['importance_mean']:.4f} |")
            sections.append("")

    # Chapter 7: Conclusion
    sections.append("## 7. Conclusion")
    sections.append("")
    sections.append(
        "- The **Grade-Assisted** scenario achieves significantly better predictions, "
        "demonstrating that G1 and G2 are the dominant predictors of G3."
    )
    sections.append(
        "- The **Early Performance** scenario, while less accurate, is valuable for "
        "proactive student support before any grades are available."
    )
    sections.append(
        "- Tree-based ensemble methods (Random Forest, Gradient Boosting) generally "
        "outperform linear models, especially in the Early Performance scenario."
    )
    sections.append(
        "- Key non-grade features include `failures`, `absences`, `higher`, `Medu`, "
        "and `studytime`."
    )
    sections.append("")

    # References
    sections.append("## References")
    sections.append("")
    sections.append("1. P. Cortez and A. Silva. *Using Data Mining to Predict Secondary School Student Performance*. EUROSIS, 2008.")
    sections.append("2. UCI Machine Learning Repository — Student Performance Data Set. https://archive.ics.uci.edu/dataset/320/student+performance")
    sections.append("3. scikit-learn documentation. https://scikit-learn.org/stable/")
    sections.append("")
    sections.append("---")
    sections.append("*GradeSense — VESIT SEM VII Data Science Mini Project*")

    report_text = "\n".join(sections)
    path = REPORTS_DIR / "GradeSense_Mini_Project_Report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"[SAVE] {path}")
    return report_text


# ---------------------------------------------------------------------------
# DOCX report
# ---------------------------------------------------------------------------
def generate_docx(results: dict):
    """Try to generate a .docx report using python-docx."""
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        print("[WARN] python-docx not available. Skipping .docx generation.")
        return

    meta = results.get("metadata", {})
    eval_data = results.get("evaluation", {})

    doc = Document()

    # Title
    title = doc.add_heading("GradeSense — Student Performance Prediction", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Mini Project Report — VESIT SEM VII Data Science", style="Subtitle")
    doc.add_paragraph(f"Generated: {datetime.datetime.now().strftime('%B %d, %Y')}")
    doc.add_paragraph("Team: [Student Name 1], [Student Name 2], [Student Name 3]")
    doc.add_page_break()

    # Abstract
    doc.add_heading("Abstract", level=1)
    doc.add_paragraph(
        "This project uses machine learning to predict student final grades (G3) in "
        "Mathematics. We compare six regression models across two prediction scenarios "
        "using the UCI Student Performance dataset."
    )

    # Results per scenario
    for scenario in ["early_performance", "grade_assisted"]:
        s_meta = meta.get(scenario, {})
        s_eval = eval_data.get(scenario, {})
        best = s_meta.get("best_model", "N/A")
        tm = s_eval.get("test_metrics", {})

        doc.add_heading(f"Results — {scenario.replace('_', ' ').title()}", level=1)
        doc.add_paragraph(f"Best Model: {best}")

        # Metrics table
        models = s_meta.get("models", {})
        if models:
            table = doc.add_table(rows=1, cols=5, style="Light Grid Accent 1")
            hdr = table.rows[0].cells
            for i, h in enumerate(["Model", "CV MAE", "Test MAE", "Test RMSE", "Test R²"]):
                hdr[i].text = h
            for mname, mv in models.items():
                row = table.add_row().cells
                row[0].text = mname
                row[1].text = str(mv.get("cv_MAE", ""))
                row[2].text = str(mv.get("test_MAE", ""))
                row[3].text = str(mv.get("test_RMSE", ""))
                row[4].text = str(mv.get("test_R2", ""))

        # Try to insert figures
        for fig_name in [f"actual_vs_pred_{scenario}.png",
                         f"residuals_{scenario}.png",
                         f"feature_importance_{scenario}.png"]:
            fig_path = FIGURES_DIR / fig_name
            if fig_path.exists():
                doc.add_paragraph()
                doc.add_picture(str(fig_path), width=Inches(5.5))

    # Save
    path = REPORTS_DIR / "GradeSense_Mini_Project_Report.docx"
    doc.save(str(path))
    print(f"[SAVE] {path}")


# ---------------------------------------------------------------------------
# PDF report
# ---------------------------------------------------------------------------
def generate_pdf(results: dict):
    """Try to generate a PDF report using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
            PageBreak,
        )
        from reportlab.lib import colors
    except ImportError:
        print("[WARN] reportlab not available. Skipping PDF generation.")
        return

    meta = results.get("metadata", {})
    eval_data = results.get("evaluation", {})
    path = REPORTS_DIR / "GradeSense_Mini_Project_Report.pdf"

    doc = SimpleDocTemplate(str(path), pagesize=A4,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=22,
                                  spaceAfter=12, alignment=1)
    heading_style = ParagraphStyle("CustomH1", parent=styles["Heading1"], fontSize=16,
                                    spaceAfter=8, spaceBefore=14)
    body_style = styles["BodyText"]

    story = []

    # Title page
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("GradeSense", title_style))
    story.append(Paragraph("Student Performance Prediction", styles["Heading2"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Mini Project Report — VESIT SEM VII Data Science", body_style))
    story.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Paragraph("Team: [Student Name 1], [Student Name 2], [Student Name 3]", body_style))
    story.append(PageBreak())

    # Abstract
    story.append(Paragraph("Abstract", heading_style))
    story.append(Paragraph(
        "This project applies machine learning regression techniques to predict "
        "student final grades (G3) in Mathematics using the UCI Student Performance "
        "dataset. Six models are compared across two scenarios.",
        body_style,
    ))
    story.append(Spacer(1, 0.3 * inch))

    # Results per scenario
    for scenario in ["early_performance", "grade_assisted"]:
        s_meta = meta.get(scenario, {})
        s_eval = eval_data.get(scenario, {})
        best = s_meta.get("best_model", "N/A")

        story.append(Paragraph(f"Results — {scenario.replace('_', ' ').title()}", heading_style))
        story.append(Paragraph(f"Best Model: <b>{best}</b>", body_style))

        models = s_meta.get("models", {})
        if models:
            data = [["Model", "CV MAE", "Test MAE", "Test RMSE", "Test R²"]]
            for mname, mv in models.items():
                data.append([
                    mname,
                    str(mv.get("cv_MAE", "")),
                    str(mv.get("test_MAE", "")),
                    str(mv.get("test_RMSE", "")),
                    str(mv.get("test_R2", "")),
                ])
            t = Table(data, hAlign="LEFT")
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#D9E2F3")]),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.3 * inch))

        # Insert figures if available
        for fig_name in [f"actual_vs_pred_{scenario}.png",
                         f"feature_importance_{scenario}.png"]:
            fig_path = FIGURES_DIR / fig_name
            if fig_path.exists():
                story.append(Image(str(fig_path), width=5 * inch, height=3.5 * inch))
                story.append(Spacer(1, 0.2 * inch))

        story.append(PageBreak())

    # Build PDF
    doc.build(story)
    print(f"[SAVE] {path}")


# ---------------------------------------------------------------------------
# PPTX presentation
# ---------------------------------------------------------------------------
def generate_pptx(results: dict):
    """Try to generate a PowerPoint presentation."""
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.enum.text import PP_ALIGN
    except ImportError:
        print("[WARN] python-pptx not available. Skipping .pptx generation.")
        return

    meta = results.get("metadata", {})
    eval_data = results.get("evaluation", {})

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # --- Slide 1: Title ---
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "GradeSense"
    slide.placeholders[1].text = (
        "Student Performance Prediction\n"
        "VESIT SEM VII — Data Science Mini Project\n"
        f"{datetime.datetime.now().strftime('%B %Y')}"
    )

    # --- Slide 2: Problem Statement ---
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Problem Statement"
    body = slide.placeholders[1].text_frame
    body.text = "Predict student final Mathematics grade (G3, 0–20) using:"
    body.add_paragraph().text = "• Demographic, family, school & lifestyle features"
    body.add_paragraph().text = "• Two scenarios: with and without prior exam grades (G1, G2)"
    body.add_paragraph().text = "• Goal: early identification of at-risk students"

    # --- Slide 3: Dataset ---
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Dataset"
    body = slide.placeholders[1].text_frame
    body.text = "UCI Student Performance Dataset (Mathematics)"
    body.add_paragraph().text = "• 395 students, 33 attributes"
    body.add_paragraph().text = "• Features: school, family, social, health, academic"
    body.add_paragraph().text = "• Target: G3 (final grade, 0–20)"
    body.add_paragraph().text = "• No missing values"

    # --- Slide 4: Methodology ---
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Methodology"
    body = slide.placeholders[1].text_frame
    body.text = "Preprocessing Pipeline (scikit-learn)"
    body.add_paragraph().text = "• Numeric: Median imputation → Standard scaling"
    body.add_paragraph().text = "• Categorical: Mode imputation → One-hot encoding"
    body.add_paragraph().text = "• 80/20 train/test split, 5-fold cross-validation"
    body.add_paragraph().text = "• 6 regression models compared per scenario"

    # --- Slide 5: Models ---
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Models Trained"
    body = slide.placeholders[1].text_frame
    body.text = "1. DummyRegressor (baseline — always predicts mean)"
    body.add_paragraph().text = "2. Linear Regression"
    body.add_paragraph().text = "3. Ridge Regression (α = 1.0)"
    body.add_paragraph().text = "4. Random Forest (100 trees)"
    body.add_paragraph().text = "5. Gradient Boosting (100 rounds)"
    body.add_paragraph().text = "6. Histogram Gradient Boosting"

    # --- Slides 6-7: Results per scenario ---
    for scenario in ["early_performance", "grade_assisted"]:
        s_meta = meta.get(scenario, {})
        s_eval = eval_data.get(scenario, {})
        best = s_meta.get("best_model", "N/A")
        tm = s_eval.get("test_metrics", {})

        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = f"Results — {scenario.replace('_', ' ').title()}"
        body = slide.placeholders[1].text_frame
        body.text = f"Best Model: {best}"
        if tm:
            body.add_paragraph().text = f"• MAE  = {tm.get('MAE', '?')}"
            body.add_paragraph().text = f"• RMSE = {tm.get('RMSE', '?')}"
            body.add_paragraph().text = f"• R²   = {tm.get('R2', '?')}"
        body.add_paragraph().text = f"• Large errors (|err|>3): {s_eval.get('large_error_count', '?')}"

    # --- Slide 8: Model Comparison figure ---
    fig_path = FIGURES_DIR / "model_comparison.png"
    if fig_path.exists():
        slide = prs.slides.add_slide(prs.slide_layouts[5])  # blank
        slide.shapes.title.text = "Model Comparison"
        slide.shapes.add_picture(str(fig_path), Inches(1), Inches(1.5),
                                  width=Inches(11), height=Inches(5))

    # --- Slide 9: Feature Importance ---
    for scenario in ["early_performance", "grade_assisted"]:
        fig_path = FIGURES_DIR / f"feature_importance_{scenario}.png"
        if fig_path.exists():
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            slide.shapes.title.text = f"Feature Importance — {scenario.replace('_',' ').title()}"
            slide.shapes.add_picture(str(fig_path), Inches(1.5), Inches(1.5),
                                      width=Inches(10), height=Inches(5))

    # --- Slide 10: Conclusion ---
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Conclusions & Future Work"
    body = slide.placeholders[1].text_frame
    body.text = "Key Findings:"
    body.add_paragraph().text = "• G1 and G2 are the strongest predictors of G3"
    body.add_paragraph().text = "• Early performance prediction is harder but valuable"
    body.add_paragraph().text = "• Tree-based ensembles outperform linear models"
    body.add_paragraph().text = ""
    body.add_paragraph().text = "Future Work:"
    body.add_paragraph().text = "• Hyperparameter tuning (GridSearchCV)"
    body.add_paragraph().text = "• Feature engineering (interaction terms)"
    body.add_paragraph().text = "• Deploy prediction API for real-time use"

    # Save
    path = REPORTS_DIR / "GradeSense_Presentation.pptx"
    prs.save(str(path))
    print(f"[SAVE] {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("GradeSense — Report Generation")
    print("=" * 60)

    results = load_results()

    if not results:
        print("[ERROR] No results found. Run train_models.py and evaluate_models.py first.")
        return

    # 1. JSON summary
    generate_json_summary(results)

    # 2. Markdown analytical summary
    generate_markdown_summary(results)

    # 3. Full project report (Markdown)
    generate_project_report_md(results)

    # 4. Word document
    generate_docx(results)

    # 5. PDF
    generate_pdf(results)

    # 6. PowerPoint
    generate_pptx(results)

    print("\n" + "=" * 60)
    print("Report generation complete - OK")
    print("=" * 60)


if __name__ == "__main__":
    main()
