import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_main_model_meets_recorded_quality_floor():
    report = json.loads((ROOT / "outputs" / "phase1" / "audit_and_metrics.json").read_text(encoding="utf-8"))
    metrics = report["models"]["random_forest_balanced"]["test"]
    assert metrics["pr_auc"] >= 0.70
    assert metrics["recall"] >= 0.70
    assert metrics["f1"] >= 0.60


def test_report_proves_leakage_columns_are_excluded():
    report = json.loads((ROOT / "outputs" / "phase1" / "audit_and_metrics.json").read_text(encoding="utf-8"))
    excluded = set(report["dataset_audit"]["leakage_columns_excluded"])
    assert {"TWF", "HDF", "PWF", "OSF", "RNF"} <= excluded
