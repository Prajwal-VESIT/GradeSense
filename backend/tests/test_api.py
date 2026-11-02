"""
Integration and functional tests for GradeSense API endpoints.
Tests endpoints directly against schemas and logic.
"""

import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.routes.health import get_health
from app.routes.data import get_summary, get_records, export_csv
from app.routes.analytics import get_grades, get_correlations, get_insights, get_statistical_tests
from app.routes.models import get_comparison, get_metadata
from app.routes.predictions import predict, batch_predict
from app.schemas import (
    PredictionRequest,
    StudentFeatures,
    ScenarioEnum,
    BatchPredictionRequest,
)
from fastapi import HTTPException


def get_sample_features(with_grades: bool = False) -> dict:
    feat = {
        "school": "GP",
        "sex": "F",
        "age": 17,
        "address": "U",
        "famsize": "GT3",
        "Pstatus": "T",
        "Medu": 3,
        "Fedu": 3,
        "Mjob": "other",
        "Fjob": "services",
        "reason": "course",
        "guardian": "mother",
        "traveltime": 1,
        "studytime": 2,
        "failures": 0,
        "schoolsup": "no",
        "famsup": "yes",
        "paid": "no",
        "activities": "yes",
        "nursery": "yes",
        "higher": "yes",
        "internet": "yes",
        "romantic": "no",
        "famrel": 4,
        "freetime": 3,
        "goout": 2,
        "Dalc": 1,
        "Walc": 1,
        "health": 4,
        "absences": 4,
    }
    if with_grades:
        feat["G1"] = 14
        feat["G2"] = 15
    return feat


def test_health_route():
    h = get_health()
    assert h.status == "ok"
    assert h.dataset_available is True
    assert h.models_available["early_performance"] is True
    assert h.models_available["grade_assisted"] is True


def test_dataset_summary_route():
    s = get_summary()
    assert s["n_rows"] == 395
    assert s["n_cols"] == 33
    assert len(s["columns"]) == 33


def test_dataset_records_pagination_and_search():
    records = get_records(page=1, page_size=10, search=None, school="GP", sex="F")
    assert records["page"] == 1
    assert records["page_size"] == 10
    assert records["total_records"] > 0
    assert len(records["records"]) == 10
    assert all(r["school"] == "GP" and r["sex"] == "F" for r in records["records"])


def test_csv_export():
    csv_resp = export_csv()
    assert csv_resp.status_code == 200
    assert "school;sex" in csv_resp.body.decode() or "school,sex" in csv_resp.body.decode()


def test_analytics_grades():
    grades = get_grades()
    assert grades["mean"] == pytest.approx(10.415, 0.01)
    assert grades["median"] == 11.0
    assert len(grades["grades"]) == 395


def test_analytics_correlations():
    corr = get_correlations(method="pearson")
    assert "G3" in corr["features"]
    assert len(corr["correlation_matrix"]) == len(corr["features"])


def test_analytics_insights_and_tests():
    insights = get_insights()
    assert len(insights) >= 4

    tests = get_statistical_tests()
    assert len(tests) >= 3
    t_names = [t.test_name for t in tests]
    assert any("Welch" in name for name in t_names)


def test_models_comparison_and_metadata():
    comp = get_comparison()
    assert len(comp) == 12  # 6 models x 2 scenarios

    meta = get_metadata()
    assert "early_performance" in meta
    assert "grade_assisted" in meta


def test_predict_early_performance():
    req = PredictionRequest(
        scenario=ScenarioEnum.early_performance,
        features=StudentFeatures(**get_sample_features(with_grades=False)),
    )
    res = predict(req)
    assert 0.0 <= res.predicted_grade <= 20.0
    assert res.scenario == "early_performance"
    assert "RandomForest" in res.model_used


def test_predict_grade_assisted():
    req = PredictionRequest(
        scenario=ScenarioEnum.grade_assisted,
        features=StudentFeatures(**get_sample_features(with_grades=True)),
    )
    res = predict(req)
    assert 0.0 <= res.predicted_grade <= 20.0
    assert res.scenario == "grade_assisted"
    assert res.predicted_grade > 12.0  # Given G1=14, G2=15, predicted grade should be strong


def test_predict_grade_assisted_missing_grades():
    req = PredictionRequest(
        scenario=ScenarioEnum.grade_assisted,
        features=StudentFeatures(**get_sample_features(with_grades=False)),
    )
    with pytest.raises(HTTPException) as exc_info:
        predict(req)
    assert exc_info.value.status_code == 422


def test_batch_prediction():
    records = [
        StudentFeatures(**get_sample_features(with_grades=False)),
        StudentFeatures(**get_sample_features(with_grades=False)),
    ]
    req = BatchPredictionRequest(
        scenario=ScenarioEnum.early_performance,
        records=records,
    )
    res = batch_predict(req)
    assert res.total == 2
    assert res.successful == 2
    assert res.failed == 0
    assert len(res.predictions) == 2
