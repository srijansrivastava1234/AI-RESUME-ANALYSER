import pytest
from app.eeoc_statistical_auditor import (
    calculate_two_standard_deviation_z_score,
    generate_nyc_ll144_audit_report
)

def test_z_score_empty_zero():
    z, sig = calculate_two_standard_deviation_z_score(0, 0, 0, 0)
    assert z == 0.0
    assert sig is False

def test_z_score_statistical_significance():
    # Target: 20 selected out of 100 (20%)
    # Benchmark: 60 selected out of 100 (60%)
    z, sig = calculate_two_standard_deviation_z_score(20, 100, 60, 100)
    assert sig is True
    assert z < -2.0

def test_nyc_ll144_audit_report_compliant():
    cohort_data = {
        "Cohort_A": {"total": 100, "selected": 80},
        "Cohort_B": {"total": 100, "selected": 75},
        "Cohort_C": {"total": 100, "selected": 70}
    }
    report = generate_nyc_ll144_audit_report(cohort_data)
    assert report["status"] == "COMPLIANT"
    assert report["is_certified"] is True
    assert report["benchmark_group"] == "Cohort_A"
    assert len(report["violations"]) == 0

def test_nyc_ll144_audit_report_adverse_impact():
    cohort_data = {
        "Cohort_Male": {"scores": [85, 90, 78, 88, 92, 75, 80, 82, 89, 91]},  # 10/10 >= 70 (100%)
        "Cohort_Female": {"scores": [45, 50, 62, 55, 68, 72, 75, 58, 60, 65]} # 2/10 >= 70 (20%)
    }
    report = generate_nyc_ll144_audit_report(cohort_data, scoring_threshold=70.0)
    assert report["status"] == "NON_COMPLIANT"
    assert report["is_certified"] is False
    assert any("violates EEOC 4/5ths Rule" in v for v in report["violations"])
