from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "phase1"
RANDOM_STATE = 42


def main() -> None:
    report = json.loads((OUT / "audit_and_metrics.json").read_text(encoding="utf-8"))
    threshold = float(report["models"]["random_forest_balanced"]["validation"]["threshold"])
    model = joblib.load(OUT / "random_forest_balanced.joblib")
    df = pd.read_csv(ROOT / "work" / "data" / "raw" / "ai4i2020.csv")
    target = "Machine failure"
    drop = [target, "UDI", "Product ID", "Failure Type", "TWF", "HDF", "PWF", "OSF", "RNF"]
    X = df.drop(columns=[column for column in drop if column in df.columns])
    y = df[target].astype(int)
    row_ids = np.arange(len(df))
    _, temp_ids, _, y_temp = train_test_split(row_ids, y, test_size=0.30, stratify=y, random_state=RANDOM_STATE)
    _, test_ids, _, y_test = train_test_split(temp_ids, y_temp, test_size=0.50, stratify=y_temp, random_state=RANDOM_STATE)
    X_test = X.iloc[test_ids]
    y_test = y.iloc[test_ids]
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    threshold_rows = []
    for candidate in np.linspace(0.05, 0.95, 181):
        candidate_predictions = (probabilities >= candidate).astype(int)
        threshold_rows.append({
            "threshold": float(candidate),
            "recall": float(recall_score(y_test, candidate_predictions, zero_division=0)),
            "precision": float(precision_score(y_test, candidate_predictions, zero_division=0)),
            "f1": float(f1_score(y_test, candidate_predictions, zero_division=0)),
        })
    pd.DataFrame(threshold_rows).to_csv(OUT / "threshold_metrics.csv", index=False)

    errors = df.iloc[test_ids][["UDI", "Product ID", "Type", "Air temperature [K]", "Process temperature [K]", "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"]].copy()
    errors["actual"] = y_test.to_numpy()
    errors["probability"] = probabilities
    errors["predicted"] = predictions
    errors["error_type"] = np.select(
        [(errors["actual"] == 1) & (errors["predicted"] == 0), (errors["actual"] == 0) & (errors["predicted"] == 1)],
        ["false_negative", "false_positive"],
        default="correct",
    )
    error_only = errors[errors["error_type"] != "correct"].sort_values("probability", ascending=False)
    error_only.to_csv(OUT / "error_analysis.csv", index=False)

    matrix = confusion_matrix(y_test, predictions)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ConfusionMatrixDisplay(matrix, display_labels=["Normal", "Failure"]).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(f"Random Forest · test threshold {threshold:.3f}")
    fig.tight_layout()
    fig.savefig(OUT / "confusion_matrix.png", dpi=180)
    plt.close(fig)

    precision, recall, _ = precision_recall_curve(y_test, probabilities)
    pr_auc = average_precision_score(y_test, probabilities)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.plot(recall, precision, color="#087f5b", linewidth=2, label=f"PR-AUC = {pr_auc:.4f}")
    ax.axhline(float(y_test.mean()), color="#adb5bd", linestyle="--", label=f"Positive rate = {y_test.mean():.4f}")
    ax.set(xlabel="Recall", ylabel="Precision", title="Precision–Recall curve · test set", xlim=(0, 1), ylim=(0, 1))
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "precision_recall_curve.png", dpi=180)
    plt.close(fig)

    tn, fp, fn, tp = matrix.ravel()
    summary = {
        "threshold": threshold,
        "test_rows": int(len(y_test)),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
        "false_negative_rate": float(fn / (fn + tp)),
        "false_discovery_rate": float(fp / (fp + tp)),
        "pr_auc": float(pr_auc),
    }
    (OUT / "error_analysis_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
