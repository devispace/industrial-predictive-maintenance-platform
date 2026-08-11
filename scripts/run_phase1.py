from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from urllib.request import urlopen

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "work" / "data" / "raw"
OUT_DIR = ROOT / "outputs" / "phase1"
DATA_URL = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
RANDOM_STATE = 42


def download_dataset() -> tuple[Path, str]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    archive = RAW_DIR / "ai4i2020.zip"
    if not archive.exists():
        with urlopen(DATA_URL, timeout=60) as response:
            archive.write_bytes(response.read())
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as zf:
        csv_name = next(name for name in zf.namelist() if name.lower().endswith(".csv"))
        csv_path = RAW_DIR / Path(csv_name).name
        if not csv_path.exists():
            zf.extract(csv_name, RAW_DIR)
            (RAW_DIR / csv_name).replace(csv_path)
    return csv_path, sha


def audit(df: pd.DataFrame) -> dict:
    target = "Machine failure"
    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "dtypes": {k: str(v) for k, v in df.dtypes.items()},
        "missing_values": {k: int(v) for k, v in df.isna().sum().items()},
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_uid": int(df["UDI"].duplicated().sum()),
        "target_counts": {str(k): int(v) for k, v in df[target].value_counts().sort_index().items()},
        "target_rate": float(df[target].mean()),
        "leakage_columns_excluded": ["UDI", "Product ID", "Failure Type", "TWF", "HDF", "PWF", "OSF", "RNF"],
    }


def metrics(y_true: pd.Series, probabilities: np.ndarray, threshold: float) -> dict:
    pred = (probabilities >= threshold).astype(int)
    return {
        "threshold": float(threshold),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "pr_auc": float(average_precision_score(y_true, probabilities)),
        "predicted_positive_rate": float(pred.mean()),
    }


def main() -> None:
    csv_path, sha256 = download_dataset()
    df = pd.read_csv(csv_path)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"source_url": DATA_URL, "archive_sha256": sha256, "dataset_audit": audit(df)}

    target = "Machine failure"
    requested_drop = [target, "UDI", "Product ID", "Failure Type", "TWF", "HDF", "PWF", "OSF", "RNF"]
    drop = [column for column in requested_drop if column in df.columns]
    X = df.drop(columns=drop)
    y = df[target].astype(int)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, stratify=y, random_state=RANDOM_STATE)
    X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=RANDOM_STATE)
    report["split"] = {"random_state": RANDOM_STATE, "train": len(X_train), "validation": len(X_valid), "test": len(X_test)}

    categorical = ["Type"]
    numeric = [c for c in X.columns if c not in categorical]
    def pipeline(class_weight):
        pre = ColumnTransformer([("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric), ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)])
        return Pipeline([("preprocess", pre), ("model", LogisticRegression(max_iter=2000, class_weight=class_weight, random_state=RANDOM_STATE))])

    tree_pre = ColumnTransformer([("num", SimpleImputer(strategy="median"), numeric), ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore"))]), categorical)])
    models = {
        "logistic_regression_baseline": pipeline(None),
        "logistic_regression_balanced": pipeline("balanced"),
        "random_forest_balanced": Pipeline([("preprocess", tree_pre), ("model", RandomForestClassifier(n_estimators=400, class_weight="balanced_subsample", min_samples_leaf=2, n_jobs=-1, random_state=RANDOM_STATE))]),
    }
    model_results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        valid_prob = model.predict_proba(X_valid)[:, 1]
        thresholds = np.linspace(0.05, 0.95, 181)
        best_threshold = max(thresholds, key=lambda t: f1_score(y_valid, (valid_prob >= t).astype(int), zero_division=0))
        test_prob = model.predict_proba(X_test)[:, 1]
        model_results[name] = {"validation": metrics(y_valid, valid_prob, best_threshold), "test": metrics(y_test, test_prob, best_threshold)}
        joblib.dump(model, OUT_DIR / f"{name}.joblib")
    report["models"] = model_results
    report["notes"] = ["Metrics are generated by this run; no manually entered values.", "TWF/HDF/PWF/OSF/RNF are excluded because they are post-hoc failure-mode labels and would leak the target."]
    (OUT_DIR / "audit_and_metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
