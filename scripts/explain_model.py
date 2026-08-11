from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import shap

ROOT = Path(__file__).resolve().parents[1]
MODEL = joblib.load(ROOT / "outputs" / "phase1" / "random_forest_balanced.joblib")
df = pd.read_csv(ROOT / "work" / "data" / "raw" / "ai4i2020.csv")
drop = ["Machine failure", "UDI", "Product ID", "Failure Type", "TWF", "HDF", "PWF", "OSF", "RNF"]
X = df.drop(columns=[c for c in drop if c in df.columns]).sample(n=min(1000, len(df)), random_state=42)
pre = MODEL.named_steps["preprocess"]
transformed = pre.transform(X)
feature_names = pre.get_feature_names_out().tolist()
explainer = shap.TreeExplainer(MODEL.named_steps["model"])
values = explainer.shap_values(transformed)
if isinstance(values, list):
    values = values[1]
elif getattr(values, "ndim", 0) == 3:
    values = values[:, :, 1]
importance = pd.DataFrame({"feature": feature_names, "mean_abs_shap": abs(values).mean(axis=0)}).sort_values("mean_abs_shap", ascending=False)
out = ROOT / "outputs" / "phase1"
importance.to_csv(out / "shap_feature_importance.csv", index=False)
(out / "shap_summary.json").write_text(json.dumps({"sample_size": len(X), "top_features": importance.head(10).to_dict("records")}, ensure_ascii=False, indent=2), encoding="utf-8")
print(importance.head(10).to_string(index=False))
