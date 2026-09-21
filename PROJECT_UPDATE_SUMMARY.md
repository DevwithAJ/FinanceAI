# FinanceAI 2.0 — Final VS Code Full Working Update

This build is the consolidated FinanceAI 2.0 project for VS Code. It preserves the full finance-management, analytics, ML and reporting workflow while using a fully local TF-IDF RAG assistant with no external AI provider dependency.

## Build identity

- Project: `FinanceAI 2.0`
- Version: `2.0.0`
- Default URL: `http://127.0.0.1:5050`
- Virtual environment folder: `venv`

## Included updates

- Budget Planner Jinja `dict.items` crash fixed.
- Spending Insights hidden `.items` collision fixed.
- Stronger authentication/session routing and no-cache behavior.
- Loan Risk uses readable full U.S. state names while preserving trained-model state codes.
- Credit Stress and Loan Risk use user-friendly Low / Moderate / High presentation.
- History uses readable tables, explanations, CSV export and PDF reports.
- Transactions, budgets, 50/30/20 planning, goals, net worth and Government Schemes retained.
- 30/60/90 cash-flow forecasting retained.
- Isolation Forest anomaly detection and K-Means spending behavior retained.
- Local TF-IDF RAG FinanceAI Assistant retained and runs without an external API key.
- VS Code Run/Debug configuration and tasks included.
- Windows scripts consistently use `venv`.
- `/version`, service smoke tests and Flask web-route smoke tests included.
