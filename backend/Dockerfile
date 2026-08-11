FROM node:24-alpine AS frontend-build
WORKDIR /frontend
RUN corepack enable && corepack prepare pnpm@11.16.0 --activate
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/index.html ./
COPY frontend/src ./src
RUN pnpm run build

FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt psycopg[binary]
COPY backend /app/backend
COPY outputs/phase1/random_forest_balanced.joblib /app/outputs/phase1/random_forest_balanced.joblib
COPY outputs/phase1/audit_and_metrics.json /app/outputs/phase1/audit_and_metrics.json
COPY --from=frontend-build /frontend/dist /app/frontend/dist
ENV PYTHONPATH=/app/backend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
