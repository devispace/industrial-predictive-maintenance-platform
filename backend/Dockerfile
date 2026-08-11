FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt psycopg[binary]
COPY backend /app/backend
COPY outputs/phase1/random_forest_balanced.joblib /app/outputs/phase1/random_forest_balanced.joblib
ENV PYTHONPATH=/app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
