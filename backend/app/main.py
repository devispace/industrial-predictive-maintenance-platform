from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Float, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT / "outputs" / "phase1" / "random_forest_balanced.joblib"))


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'work' / 'predictions.db'}"))
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


class Base(DeclarativeBase):
    pass


class PredictionRecord(Base):
    __tablename__ = "prediction_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    probability: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    alert: Mapped[bool] = mapped_column(Boolean)
    machine_type: Mapped[str] = mapped_column(String(1))


Base.metadata.create_all(engine)
model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None


class SensorInput(BaseModel):
    machine_type: str = Field(alias="Type", pattern="^[LMH]$")
    air_temperature_k: float = Field(alias="Air temperature [K]")
    process_temperature_k: float = Field(alias="Process temperature [K]")
    rotational_speed_rpm: int = Field(alias="Rotational speed [rpm]", gt=0)
    torque_nm: float = Field(alias="Torque [Nm]", ge=0)
    tool_wear_min: int = Field(alias="Tool wear [min]", ge=0)

    model_config = {"populate_by_name": True}


class PredictionResponse(BaseModel):
    probability: float
    threshold: float
    alert: bool
    action: str


app = FastAPI(title="Industrial Predictive Maintenance API", version="0.2.0")
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


def load_threshold() -> float:
    configured = os.getenv("MODEL_THRESHOLD")
    if configured is not None:
        return float(configured)
    report_path = ROOT / "outputs" / "phase1" / "audit_and_metrics.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        return float(report["models"]["random_forest_balanced"]["validation"]["threshold"])
    return 0.335


DEFAULT_THRESHOLD = load_threshold()


def predict_one(item: SensorInput) -> PredictionResponse:
    if model is None:
        raise HTTPException(status_code=503, detail="Model artifact is not available")
    row = pd.DataFrame([{
        "Type": item.machine_type,
        "Air temperature [K]": item.air_temperature_k,
        "Process temperature [K]": item.process_temperature_k,
        "Rotational speed [rpm]": item.rotational_speed_rpm,
        "Torque [Nm]": item.torque_nm,
        "Tool wear [min]": item.tool_wear_min,
    }])
    probability = float(model.predict_proba(row)[:, 1][0])
    alert = probability >= DEFAULT_THRESHOLD
    return PredictionResponse(probability=probability, threshold=DEFAULT_THRESHOLD, alert=alert, action="人工确认告警；不执行自动停机" if alert else "继续监测")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model_loaded": model is not None, "model_version": MODEL_PATH.stem, "threshold": DEFAULT_THRESHOLD}


@app.get("/metrics")
def metrics() -> dict[str, int | float]:
    with Session(engine) as session:
        total = session.scalar(select(func.count()).select_from(PredictionRecord)) or 0
        alerts = session.scalar(select(func.count()).select_from(PredictionRecord).where(PredictionRecord.alert.is_(True))) or 0
    return {"predictions_total": total, "alerts_total": alerts, "alert_rate": alerts / total if total else 0.0}


@app.post("/predict", response_model=PredictionResponse)
def predict(item: SensorInput) -> PredictionResponse:
    result = predict_one(item)
    with Session(engine) as session:
        session.add(PredictionRecord(probability=result.probability, threshold=result.threshold, alert=result.alert, machine_type=item.machine_type))
        session.commit()
    return result


@app.post("/predict/batch", response_model=list[PredictionResponse])
def predict_batch(items: list[SensorInput]) -> list[PredictionResponse]:
    if not items:
        raise HTTPException(status_code=422, detail="Batch must contain at least one item")
    if len(items) > 1000:
        raise HTTPException(status_code=413, detail="Batch size must be <= 1000")
    results = [predict_one(item) for item in items]
    records = [PredictionRecord(probability=result.probability, threshold=result.threshold, alert=result.alert, machine_type=item.machine_type) for item, result in zip(items, results)]
    with Session(engine) as session:
        session.add_all(records)
        session.commit()
    return results


STATIC_DIR = ROOT / "frontend" / "dist"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="dashboard")
