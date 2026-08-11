# 简历项目表述

## 项目名称

工业设备预测性维护与异常诊断平台｜个人项目｜Python / FastAPI / PostgreSQL / React / Docker

## 中文简历版（推荐）

- 基于 UCI AI4I 2020 **公开合成工业数据**独立构建设备故障风险诊断流程，完成 10,000 条样本的数据审计、身份字段与后验故障标签泄漏治理，以及固定随机种子的 70%/15%/15% 分层切分。
- 建立 Logistic Regression 基线并使用类别平衡 Random Forest 作为主模型，在独立测试集取得 **PR-AUC 0.7476、Recall 0.7451、Precision 0.6032、F1 0.6667**；在验证集选择 `0.335` 阈值，并结合混淆矩阵、181 个候选阈值、SHAP 和假阳性/假阴性样本分析评估漏报与误报。
- 使用 **FastAPI + PostgreSQL + React/Vite** 实现单条/最多 1,000 条批量预测、健康检查、运行指标、预测与告警记录和工业监控看板；通过 **Docker Compose、8 项 pytest/模型回归测试和 GitHub Actions** 完成工程化交付，并部署至 Render 公网环境。
- 将高风险工业动作限定为“告警 + 人工确认”，明确不实现自动停机；在 README 中披露合成数据边界、模型局限、冷启动与免费数据库有效期，避免将演示系统包装为真实工厂生产系统。

## 一行精简版

独立实现工业设备预测性维护平台，基于 UCI AI4I 2020 公开合成数据完成泄漏安全建模、类别不平衡处理与阈值/SHAP 分析（测试集 PR-AUC 0.7476、Recall 0.7451），并以 FastAPI、PostgreSQL、React、Docker Compose、pytest、GitHub Actions 和 Render 完成端到端部署。

## English version

- Built an end-to-end industrial equipment failure-risk platform on the public synthetic UCI AI4I 2020 dataset, with leakage-safe feature selection and a reproducible stratified 70/15/15 split across 10,000 samples.
- Benchmarked Logistic Regression and trained a class-balanced Random Forest achieving **0.7476 test PR-AUC, 0.7451 recall, 0.6032 precision and 0.6667 F1**; selected a 0.335 validation threshold and conducted confusion-matrix, threshold, SHAP and false-positive/false-negative analysis.
- Shipped single and batch inference, health/metrics endpoints, PostgreSQL prediction records and a React/Vite dashboard with FastAPI; verified the system through Docker Compose, eight pytest/model-regression tests, GitHub Actions and a public Render deployment.
- Kept all alerts human-in-the-loop and intentionally excluded automatic shutdown controls; documented the synthetic-data boundary and production-readiness gaps.

## 真实性检查

- 不写“中铝项目”“真实工厂落地”或“降低停机率 X%”。
- 不把静态二分类描述成 RUL、提前 N 天预警或实时流式预测。
- 指标只引用 `outputs/phase1/audit_and_metrics.json` 的独立测试集结果。
- 项目链接使用公开仓库与 Render 在线演示；面试前先确认免费实例仍可访问。
