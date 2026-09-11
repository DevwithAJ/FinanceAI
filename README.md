# FinanceAI — Final Integrated Project

FinanceAI is a **Flask-based personal finance and risk-analysis portfolio project** developed as a four-member B.Tech CSE team project. It combines authentication, database persistence, explainable financial-health scoring, machine-learning experiments, APIs, analysis history, and an offline educational assistant in one integrated application.

The project is designed as an educational and portfolio-grade financial analytics system. It provides a transparent Personal Finance module and two carefully labeled experimental ML modules: Credit Stress and Loan Risk.

---

## Project Team

| Member | Role | Primary Responsibility |
|---|---|---|
| **Ajit Kumar** | **Team Leader · Full-Stack & Integration Lead** | Overall architecture, Flask backend, authentication, database integration, APIs, module integration, validation, deployment flow and project coordination |
| **Ajeet Kumar** | **Personal Finance & Data Analytics Lead** | Personal Finance analytics, health-score logic, recommendations, result interpretation and module testing |
| **Sonu Kumar** | **Credit Stress ML & Explainability Lead** | Credit Stress preprocessing, leakage-safe features, Logistic Regression, threshold tuning, metrics and explainability |
| **Pranav Kr Mishra** | **Loan Risk ML, Testing & Documentation Lead** | Loan Risk preprocessing, Extra Trees workflow, diagnostics, testing, input schema and documentation support |

> This responsibility split is the recommended project allocation for documentation, demonstration and presentation. All four members may jointly contribute to testing, review, documentation and presentation preparation.

---

## Problem Statement

Personal-finance users often have financial data but do not have one simple system that explains:

- their current financial health,
- which areas require improvement,
- how risk signals can be analyzed,
- how past analyses can be stored and compared,
- and how finance-related ML systems should communicate their limitations.

FinanceAI addresses this by combining explainable finance rules, machine-learning experiments, a secure Flask application, database persistence and APIs.

---

## Project Objective

The main objective of FinanceAI is to create a unified financial analytics platform that can:

1. Help users understand their financial condition through an explainable **0–100 Financial Health Score**.
2. Generate prioritized educational recommendations from current financial indicators.
3. Demonstrate an experimental **Credit Stress** classification workflow using leakage-safe predictors.
4. Demonstrate an experimental **Loan Risk** ranking workflow using application-time borrower features.
5. Store user accounts and analysis history using SQLite or MySQL.
6. Provide both a professional browser UI and JSON API endpoints.
7. Provide an offline educational FinanceAI Assistant.
8. Clearly separate educational analytics from real credit or lending decisions.

---

## Final Features

- User registration
- User login / logout
- Password change
- Secure password hashing
- CSRF protection for browser forms
- Basic login rate limiting
- Session-based authentication
- Personal Finance Health Score (0–100)
- Explainable component-wise scoring
- Personalized prioritized recommendations
- Credit Stress experimental Logistic Regression module
- Loan Risk experimental Extra Trees module
- STEP 7 tuned thresholds
- Analysis history per user
- CSV history export
- Offline FinanceAI Assistant using latest saved Personal Finance result
- JSON API endpoints
- SQLite out-of-the-box
- Optional MySQL / XAMPP backend
- Professional responsive UI
- Windows setup scripts
- Sample inputs
- Smoke tests
- Exact scikit-learn version pinned to 1.8.0
- Responsible-use warnings for experimental ML modules

---

## Technologies Used

### Backend

- Python
- Flask
- Session-based authentication
- SQLite / MySQL
- JSON APIs

### Machine Learning / Data Science

- pandas
- NumPy
- scikit-learn
- Logistic Regression
- Extra Trees
- StandardScaler
- OneHotEncoder
- ColumnTransformer
- Stratified validation
- PR-AUC / ROC-AUC / Precision / Recall / F1 / MCC

### Frontend

- HTML
- CSS
- Jinja2
- Responsive custom UI

### Development / Testing

- Python virtual environment
- Smoke tests
- Sample JSON inputs
- PowerShell setup
- XAMPP / MySQL optional configuration

---

## System Architecture

```text
User / Browser / API Client
            │
            ▼
        Flask App
            │
    ┌───────┼─────────────┐
    │       │             │
    ▼       ▼             ▼
Auth    Validation     API Routes
    │       │             │
    └───────┼─────────────┘
            ▼
        Service Layer
            │
 ┌──────────┼───────────────┐
 │          │               │
 ▼          ▼               ▼
Personal   Credit Stress   Loan Risk
Finance    Logistic Reg.   Extra Trees
Engine
 │          │               │
 └──────────┼───────────────┘
            ▼
      SQLite / MySQL
            │
            ▼
 History · Dashboard · Assistant
```

---

# Module 1 — Personal Finance

This is the **primary user-facing module**.

## Purpose

The module converts current financial information into a transparent Financial Health Score and recommendations.

## Main Inputs

- Monthly income
- Monthly expenses
- Debt-to-income ratio
- Loan payment
- Investment amount
- Emergency fund
- Credit score
- Budget goal
- Actual savings
- Subscription count
- Financial stress level

## Financial Health Score

The score is transparent and totals **100 points**:

| Component | Maximum Points |
|---|---:|
| Cash Flow | 25 |
| Debt Health | 20 |
| Emergency Fund | 20 |
| Savings Progress | 15 |
| Investment | 10 |
| Credit | 10 |
| **Total** | **100** |

## Health Bands

- **Excellent:** 85–100
- **Good:** 70–84
- **Moderate:** 55–69
- **Weak:** 40–54
- **Critical:** 0–39

## Output

- Financial Health Score
- Health category
- Component breakdown
- Expense-to-income ratio
- Loan-to-income ratio
- Investment ratio
- Emergency-fund months
- Savings goal progress
- Prioritized recommendations
- Saved analysis history

## Personal Finance Limitation

The module is designed for educational financial-health guidance. It is not professional investment, banking, tax or financial-planning advice.

---

# Module 2 — Credit Stress

## Model

**Logistic Regression**

## Target

```text
financial_stress_flag
```

The target is a **rule-based financial-stress proxy**.

The proxy is constructed using conditions such as:

- Negative disposable income
- Expense-to-income ratio above 90%
- Loan-to-income ratio above 20%

## Strict Leakage-Safe Predictors

To avoid directly reconstructing the target, the benchmark uses only:

- Age
- Dependents
- Occupation
- City_Tier
- Desired_Savings_Percentage

## STEP 6 / 7 Results

- Champion: **Logistic Regression**
- CV PR-AUC: approximately **0.2275**
- Test PR-AUC: approximately **0.2334**
- Test ROC-AUC: approximately **0.8539**
- Default Recall: approximately **0.8727**
- STEP 7 tuned threshold: **0.68**
- Tuned Recall: approximately **0.8218**
- Tuned Precision: approximately **0.2514**
- Tuned F1: approximately **0.3850**
- Tuned MCC: approximately **0.3886**
- Top-decile lift: approximately **3.82×**

## Credit Stress Limitation

The target is **not observed credit default, delinquency, charge-off or missed payment**.

Therefore this module is an experimental classification demonstration and must not be presented as a real credit-approval or rejection engine.

---

# Module 3 — Loan Risk

## Model

**Extra Trees**

## Purpose

The model ranks historical borrower/application records by experimental risk using application-time features.

## Main Modeling Characteristics

- Application-time features
- Leakage review
- Rare-event target
- Severe class imbalance
- Temporal holdout
- PR-AUC-focused evaluation
- Threshold tuning
- Error diagnostics
- Feature importance
- Input schema validation

## Important Results

- Champion: **Extra Trees**
- Test ROC-AUC: approximately **0.6487**
- Test PR-AUC: approximately **0.0326**
- STEP 7 tuned threshold: approximately **0.2320**
- Rare positive class
- Limited historical observation window

## Integration Safety

The Loan Risk API requires the complete expected application-time feature schema.

Incomplete records are rejected rather than silently filled and presented as reliable decisions.

## Loan Risk Limitation

The model is an **experimental historical risk-ranking model**.

It is not approved for automated lending, sanctioning, pricing or approval/rejection decisions.

---

# Authentication & Security

FinanceAI includes:

- Registration
- Login
- Logout
- Password hashing
- Password change
- Session-based authentication
- CSRF protection on browser forms
- Basic login throttling
- User-specific analysis history
- Input validation

For a real financial production environment, additional requirements would include:

- HTTPS everywhere
- MFA
- centralized secrets management
- full audit logs
- monitoring
- secure backups
- penetration testing
- privacy controls
- compliance review
- fairness review
- incident response

---

# Database

FinanceAI supports two database modes.

## Option A — SQLite

Recommended for instant demo.

`.env`:

```env
DB_BACKEND=sqlite
SQLITE_PATH=instance/financeai.db
```

Then:

```powershell
python init_db.py
python app.py
```

## Option B — MySQL / XAMPP

Create the database:

```sql
CREATE DATABASE financeai
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Set `.env`:

```env
DB_BACKEND=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=financeai
```

Then:

```powershell
python init_db.py
python app.py
```

---

# Quick Start on Windows PowerShell

From the project folder:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip uninstall scikit-learn -y
pip install -r requirements.txt

Copy-Item .env.example .env

python init_db.py
python smoke_test.py
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Why uninstall scikit-learn first?

The included model `.pkl` files were created with **scikit-learn 1.8.0**.

`requirements.txt` pins:

```text
scikit-learn==1.8.0
```

This prevents the version-mismatch warnings caused by loading those model files under scikit-learn 1.9.1.

---

# Web Routes

- `/` — Landing page
- `/about` — Project details, architecture, limitations and team
- `/register`
- `/login`
- `/dashboard`
- `/personal-finance`
- `/credit-stress`
- `/loan-risk`
- `/history`
- `/assistant`
- `/profile`

---

# API Routes

- `GET /api/v1/status`
- `POST /api/v1/personal-finance`
- `GET /api/v1/credit-stress/schema`
- `POST /api/v1/credit-stress`
- `GET /api/v1/loan-risk/schema`
- `POST /api/v1/loan-risk`
- `GET /api/v1/history` — login required

---

# Offline FinanceAI Assistant

The Assistant uses the user's latest saved Personal Finance result to explain concepts such as:

- What does my score mean?
- How can I improve my financial health?
- Why is my emergency fund important?
- What should I focus on first?

The Assistant is educational and does not provide professional financial advice.

---

# Analysis History

Authenticated users can save and review past analyses.

History can contain:

- Module name
- Score/result
- Timestamp
- Analysis details
- CSV export

This demonstrates database-backed persistence rather than only one-time predictions.

---

# Team Responsibilities

## Ajit Kumar — Team Leader · Full-Stack & Integration Lead

### Main Responsibilities

- Team coordination
- Project planning
- Overall architecture
- Flask backend
- Authentication system
- Database integration
- API integration
- Module integration
- Dashboard integration
- Validation
- Deployment workflow
- Final presentation coordination

### Presentation Part

- Team introduction
- Problem statement
- Objectives
- System architecture
- Flask/backend
- Authentication/database
- Unified integration
- APIs
- Final conclusion
- Future scope

---

## Ajeet Kumar — Personal Finance & Data Analytics Lead

### Main Responsibilities

- Personal Finance dataset understanding
- EDA support
- Health-score logic interpretation
- Recommendation workflow
- Personal Finance module testing
- Result interpretation
- History-flow demonstration

### Presentation Part

- Personal Finance module
- Inputs
- Health Score
- Six score components
- Recommendations
- Saved history

---

## Sonu Kumar — Credit Stress ML & Explainability Lead

### Main Responsibilities

- Credit Stress dataset preparation
- Leakage review
- Strict feature selection
- ML preprocessing
- Logistic Regression modeling
- Evaluation
- Threshold tuning
- Explainability
- Model limitation documentation

### Presentation Part

- Credit Stress workflow
- Target definition
- Logistic Regression
- PR-AUC / ROC-AUC
- Threshold 0.68
- Coefficients / explainability
- Proxy-target limitation

---

## Pranav Kr Mishra — Loan Risk ML, Testing & Documentation Lead

### Main Responsibilities

- Loan Risk data preparation
- Target and imbalance analysis
- Feature engineering
- Extra Trees model
- Threshold diagnostics
- Input validation
- Testing
- Documentation support
- Demo support

### Presentation Part

- Loan Risk workflow
- Target
- Class imbalance
- Extra Trees
- Model metrics
- Threshold
- Input schema
- Experimental limitation

---

# Shared Team Responsibilities

All four members can jointly contribute to:

- Dataset checking
- Testing
- UI review
- Bug fixing
- Documentation review
- Presentation preparation
- Viva preparation
- Final demo validation

---

# Suggested Final Demo Flow

1. **Ajit Kumar** introduces FinanceAI and the four-member team.
2. **Ajit Kumar** explains problem statement, objective and architecture.
3. Register/login a demo user.
4. **Ajeet Kumar** demonstrates Personal Finance.
5. **Ajeet Kumar** explains Health Score + recommendations + History.
6. **Sonu Kumar** demonstrates Credit Stress.
7. **Sonu Kumar** explains Logistic Regression, metrics, threshold and proxy-target limitation.
8. **Pranav Kr Mishra** demonstrates Loan Risk.
9. **Pranav Kr Mishra** explains Extra Trees, class imbalance, experimental score and input validation.
10. Show the FinanceAI Assistant.
11. **Ajit Kumar** opens `/api/v1/status` and explains the unified backend.
12. **Ajit Kumar** closes with responsible-use limitations and future scope.

---

# Future Scope

Possible improvements include:

- Real bank transaction integration
- Real credit-card repayment data
- Actual verified credit-default target
- Larger loan outcome history
- Longer temporal validation
- Better calibrated probabilities
- Bias and fairness assessment
- Admin dashboard
- Role-based access control
- Email alerts
- Budget planning
- Investment goal tracking
- Secure cloud deployment
- Mobile app / PWA
- Advanced AI assistant with user-approved financial context

---

# Responsible-Use Boundary

FinanceAI is a **portfolio, educational and research/demo system**.

The Personal Finance module provides explainable educational guidance.

The Credit Stress and Loan Risk modules are experimental ML demonstrations.

**FinanceAI must never be used to automatically approve or reject a credit card, loan or any other financial product.**

---

# Project Structure

See:

```text
PROJECT_STRUCTURE.txt
```

---

# Documentation

The `docs/` folder contains:

- `FINAL_REPORT.md`
- `FINAL_DEMO_GUIDE.md`
- `TEAM.md`
- `API.md`
- `SECURITY.md`
- `DEPLOYMENT.md`
- `MYSQL_XAMPP.md`
- `RUN_WINDOWS.md`
- `PROJECT_STATUS.md`

---

# Team

**FinanceAI — Four Member B.Tech CSE Project Team**

**Team Leader:** Ajit Kumar

**Members:** Ajeet Kumar · Sonu Kumar · Pranav Kr Mishra
