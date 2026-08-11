# Security policy

This repository is a portfolio demonstration built with public synthetic data. It must not be connected directly to industrial control systems or used to trigger automatic shutdowns.

## Reporting

Please report suspected vulnerabilities privately through GitHub Security Advisories. Do not include credentials, production data or exploit details in a public issue.

## Operational boundaries

- The API has no authentication and is suitable only for an isolated demo environment.
- Alerts are advisory and require human confirmation; the platform does not implement automatic machine control.
- Docker Compose credentials are local-development defaults. Replace them through environment variables before any shared deployment.
- Render injects `DATABASE_URL`; no cloud database credential is stored in this repository.
- A production design requires identity and access management, rate limiting, audit logs, database migrations, encrypted backups, observability and a formal industrial-safety review.
