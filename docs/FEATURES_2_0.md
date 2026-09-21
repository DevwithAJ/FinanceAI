# FinanceAI 2.0 Feature Manifest

## Account & Security
- User registration and login
- PBKDF2 password hashing
- Login attempt rate limiting
- CSRF protection for browser forms
- Session-based user isolation
- Password change page

## Money Management
- Income and expense transaction ledger
- Recurring transaction flag
- Payment-method tracking
- CSV import/export
- Synthetic six-month demo-data loader
- Monthly income, expense, balance and savings-rate KPIs

## Budgeting & Goals
- Per-category monthly budget limits
- Actual vs budget usage state
- 50/30/20 baseline planner
- Savings goal creation and progress updates
- Remaining amount, months left and required monthly contribution

## AI / ML Analytics
- Financial Health score with recommendation engine
- Expense/income/savings cash-flow forecast for 30/60/90 days
- Linear Regression forecast when sufficient history exists
- Moving-average fallback for short histories
- Isolation Forest unusual-spending detection
- K-Means spending-category clustering
- Trained Credit Stress proxy model
- Trained Loan Risk experimental ranking model
- Model Lab with methods, thresholds and feature counts

## Wealth & Discovery
- Assets tracker
- Investments tracker
- Liabilities tracker
- Net-worth calculation
- Government-linked scheme discovery page

## Assistant
- Local TF-IDF retrieval-augmented generation (RAG)
- Grounding on local finance knowledge
- Personalized account snapshot context
- Local TF-IDF RAG finance assistant with account-aware context
- Automatic local fallback if external LLM is not configured or fails

## History, Reports & APIs
- Saved analysis history
- CSV history export
- PDF analysis reports
- JSON status/personal-finance/credit-stress/loan-risk APIs
- JSON transaction/forecast/spending-insight/net-worth APIs

## Storage & Deployment
- SQLite by default
- Optional MySQL/XAMPP schema
- Windows setup/run scripts
- Linux setup/run scripts
- Responsive interface
