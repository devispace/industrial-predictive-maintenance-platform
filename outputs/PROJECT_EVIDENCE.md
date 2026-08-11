# Project evidence

## Verified facts

- Dataset: UCI AI4I 2020, public synthetic industrial data, 10,000 rows.
- Data quality: 0 missing values, 0 duplicate UDI, 3.39% positive rate.
- Leakage prevention: UDI, Product ID, TWF, HDF, PWF, OSF and RNF excluded.
- Split: stratified 70/15/15, random state 42.
- Main model: class-balanced Random Forest, threshold selected on validation set.
- Test metrics: Recall 0.7451, Precision 0.6032, F1 0.6667, PR-AUC 0.7476, ROC-AUC 0.9705.
- Test confusion matrix: TN 1,424; FP 25; FN 13; TP 38.
- Explainability: SHAP run on 1,000 samples; top drivers were torque, rotational speed and tool wear.
- Tests: 7 passed.
- Deployment: Docker Compose started PostgreSQL, FastAPI and React/Nginx; API and database health checks passed.
- Persistence: a container API prediction produced a PostgreSQL prediction record.
- Browser demo: API ONLINE, interactive prediction, metrics refresh and 0.23% sample probability verified.

## Resume-ready Chinese bullet

独立实现工业设备预测性维护平台：基于 UCI AI4I 2020 公开合成数据完成数据审计、目标泄漏治理和可复现分层切分，构建 Logistic Regression 基线与类别平衡 Random Forest；主模型测试集 PR-AUC 0.7476、Recall 0.7451，并完成阈值选择、SHAP 与误差分析。使用 FastAPI、PostgreSQL、React/Vite 和 Docker Compose 实现单条/批量预测、告警记录、健康检查、监控看板及 GitHub Actions，pytest 7 项测试通过；高风险操作仅提示告警并要求人工确认。

## Resume-ready English bullet

Built an end-to-end industrial predictive-maintenance platform on the public synthetic UCI AI4I 2020 dataset, including leakage-safe reproducible splits, logistic baseline, class-balanced Random Forest (test PR-AUC 0.7476, recall 0.7451), threshold tuning, SHAP and error analysis; shipped FastAPI batch inference, PostgreSQL prediction records, a React/Vite dashboard, Docker Compose, GitHub Actions and seven passing regression/API tests, with human confirmation required for every alert.

## Honest interview caveat

The dataset is synthetic and static, so the project demonstrates engineering and evaluation discipline rather than proven real-factory generalization. A production rollout would require site-specific data, time-aware validation, drift monitoring, calibrated operational costs, security controls and a formal safety review.
