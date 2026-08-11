# 公开仓库安全与发布审计

审计日期：2026-08-11

## 结论

仓库可作为公开作品集发布，未发现已提交凭证或当前已知的 Python/前端生产依赖漏洞。它仍是无认证的演示系统，不适合直接连接生产网络、真实设备或工业控制系统。

## 已执行检查

| 项目 | 实际检查 | 结果 |
|---|---|---|
| 密钥与凭证 | 使用 `rg` 扫描 API key、token、password、private key、带密码 PostgreSQL URL 等模式 | 未发现 API Key、Token 或私钥；只命中 Docker Compose 本地默认密码与测试样例 URL |
| Python 依赖 | `pip-audit 2.10.1 -r requirements.txt` | `No known vulnerabilities found` |
| 前端生产依赖 | `pnpm --dir frontend audit --prod --audit-level moderate` | `No known vulnerabilities found` |
| 数据许可证 | 检查 UCI 数据页归属、DOI、README 署名和数据边界 | AI4I 2020 标注 CC BY 4.0；README 提供来源、DOI 与许可证链接 |
| 代码许可证 | 检查根目录 `LICENSE` | MIT License 存在 |
| 数据泄漏 | 检查审计报告和模型输入 | UDI、Product ID、TWF/HDF/PWF/OSF/RNF 已排除 |
| 部署凭证 | 检查 `render.yaml` 与应用配置 | `DATABASE_URL` 由 Render Blueprint 注入，仓库不存云数据库凭证 |
| 高风险动作 | 检查 API 返回和 README | 只输出告警与人工确认；不实现自动停机 |

## 已加入的防护

- `.env`、本地数据、SQLite、虚拟环境和前端依赖目录均在 `.gitignore`。
- Dependabot 每周检查 pip/npm、每月检查 Docker/GitHub Actions。
- `SECURITY.md` 声明漏洞报告方式和演示系统边界。
- CI 执行数据/模型回归、API 测试、前端构建和 Compose 配置验证。

## 已知风险与处置

1. **API 无认证和速率限制**：仅用于隔离的公开演示；不得传入真实工业数据。生产化前需 IAM、RBAC、限流和审计日志。
2. **Compose 使用本地默认账号密码**：便于本机一键启动，不是秘密。共享环境必须用环境变量或 Secret Manager 替换，并限制数据库网络暴露。
3. **依赖采用兼容范围而非完整哈希锁定**：前端有 pnpm lockfile；Python CI 会解析区间版本。后续可增加 `pip-compile --generate-hashes` 和 SBOM。
4. **容器基础镜像使用标签而非 digest**：便于自动接收补丁，但构建并非逐字节可复现。正式发布可锁定 digest 并配合自动更新。
5. **Render 免费 Web Service 冷启动**：闲置后首次请求可能等待约 50 秒或更久，README 已显著提示。
6. **Render 免费 PostgreSQL 有效期**：创建于 2026-08-11，按 30 天限制预计约 2026-09-10 到期；每次投递简历或面试前需验证并在必要时迁移/重建。
7. **合成数据与静态二分类**：不能证明真实工厂泛化，也不能解释为 RUL 或提前若干天预警。

## 面试前发布清单

- 打开在线演示并等待冷启动，运行一次预测。
- 确认 GitHub Actions 最近一次 main 构建通过。
- 确认 Render PostgreSQL 未过期，预测计数能持久化。
- 检查 Dependabot 告警并处理高危项。
- 不在演示中输入公司、客户或真实设备数据。
