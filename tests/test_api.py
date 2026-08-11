import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

os.environ.setdefault("DATABASE_URL", f"sqlite:///{ROOT / 'work' / 'test_predictions.db'}")

from app.main import SensorInput, app, health, predict

client = TestClient(app)


def test_health_has_model():
    assert health()["status"] == "ok"
    assert health()["model_loaded"] is True


def test_prediction_contract():
    item = SensorInput(Type="M", **{"Air temperature [K]": 300.1, "Process temperature [K]": 310.2, "Rotational speed [rpm]": 1500, "Torque [Nm]": 42, "Tool wear [min]": 180})
    result = predict(item)
    assert 0 <= result.probability <= 1
    assert result.threshold == pytest.approx(0.335)
    assert result.action


def test_http_prediction_and_cors_contract():
    response = client.post(
        "/predict",
        headers={"Origin": "http://localhost:5173"},
        json={"Type": "M", "Air temperature [K]": 300.1, "Process temperature [K]": 310.2, "Rotational speed [rpm]": 1500, "Torque [Nm]": 42, "Tool wear [min]": 180},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert 0 <= response.json()["probability"] <= 1


def test_invalid_machine_type_is_rejected():
    response = client.post(
        "/predict",
        json={"Type": "X", "Air temperature [K]": 300.1, "Process temperature [K]": 310.2, "Rotational speed [rpm]": 1500, "Torque [Nm]": 42, "Tool wear [min]": 180},
    )
    assert response.status_code == 422


def test_empty_batch_is_rejected():
    response = client.post("/predict/batch", json=[])
    assert response.status_code == 422
