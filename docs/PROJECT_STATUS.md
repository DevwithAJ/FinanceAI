# FinanceAI 2.0 Project Status

**Build:** FinanceAI 2.0 Final VS Code Full Working  
**Application version:** `2.0.0`  
**Default development URL:** `http://127.0.0.1:5050`

## Integrated modules

The project includes authentication, profile/session handling, transaction management, CSV import/export, demo data, monthly budgets, 50/30/20 planning, financial goals, net worth, 30/60/90-day cash-flow forecasting, Isolation Forest anomaly detection, K-Means spending behavior, Financial Health analysis, experimental Credit Stress and Loan Risk models, readable analysis history, PDF/CSV reporting, Local TF-IDF RAG, Government Schemes, Model Lab, JSON APIs, SQLite and optional MySQL/XAMPP support.

## Assistant mode

The FinanceAI Assistant is local. It retrieves relevant finance knowledge using TF-IDF and combines it with a limited FinanceAI account summary. No external AI service or API key is required.

## Validation coverage

- Python source compile: included in final validation
- Core model/database/forecast/anomaly/clustering/RAG smoke test: included
- Flask authentication/routes/templates/history/PDF smoke test: included
- ZIP integrity: checked during packaging

Credit Stress and Loan Risk remain educational research modules and must not be used for real lending decisions.
