# FinanceAI Final Project Report

## Project Team

| Member | Role |
|---|---|
| **Ajit Kumar** | **Team Leader · Full-Stack & Integration Lead** |
| **Ajeet Kumar** | **Personal Finance & Data Analytics Lead** |
| **Sonu Kumar** | **Credit Stress ML & Explainability Lead** |
| **Pranav Kr Mishra** | **Loan Risk ML, Testing & Documentation Lead** |

### Team Responsibility Summary

**Ajit Kumar** coordinates the complete FinanceAI architecture, Flask backend, authentication, database, APIs, final integration, validation and presentation flow.

**Ajeet Kumar** focuses on Personal Finance analytics, health-score interpretation, recommendations, analysis history and user-facing module validation.

**Sonu Kumar** focuses on Credit Stress preprocessing, leakage-safe feature selection, Logistic Regression modeling, threshold tuning, evaluation and explainability.

**Pranav Kr Mishra** focuses on Loan Risk preprocessing, Extra Trees risk ranking, diagnostics, input validation, testing and documentation.

All four members share final testing, documentation review, presentation preparation and viva preparation.

---

## Project Objective

FinanceAI is a unified financial analytics system designed to convert personal-finance inputs and historical credit/loan data into understandable scores, recommendations, experimental risk signals, and saved user history.

The final system demonstrates full-stack development, machine learning, data analytics, authentication, persistent storage, APIs and responsible model communication.

---

## Final Architecture

```text
Browser / JSON Client
        ↓
Flask Application
        ↓
Authentication + Validation
        ↓
Service Layer
        ↓
Rule Engine / ML Pipelines
        ↓
SQLite or MySQL
        ↓
History / Dashboard / Assistant
```

---

## Personal Finance Module

- Transparent 100-point health score
- Components:
  - Cash Flow 25
  - Debt 20
  - Emergency Fund 20
  - Savings 15
  - Investment 10
  - Credit 10
- Personalized prioritized recommendations
- Primary user-facing module
- Results saved to user history
- Educational guidance, not professional financial advice

---

## Credit Stress Model

- Champion: Logistic Regression
- Target: `financial_stress_flag`
- Strict predictors:
  - Age
  - Dependents
  - Occupation
  - City_Tier
  - Desired_Savings_Percentage
- CV PR-AUC: ~0.2275
- Test PR-AUC: ~0.2334
- Test ROC-AUC: ~0.8539
- STEP 7 tuned threshold: 0.68
- Tuned Recall: ~0.8218
- Tuned Precision: ~0.2514
- Tuned F1: ~0.3850
- Tuned MCC: ~0.3886
- Top-decile lift: ~3.82×

### Limitation

The target is a rule-based financial-stress proxy, not real credit default.

---

## Loan Risk Model

- Champion: Extra Trees
- Historical application-time features only
- Test ROC-AUC: ~0.6487
- Test PR-AUC: ~0.0326
- STEP 7 tuned threshold: ~0.2320
- Model remains experimental because rare-event performance is weak and the historical window is limited.
- API requires complete application-time features.

---

## Final Application Features

- Register / login / logout
- Password hashing
- Password change
- CSRF protection
- Basic login throttling
- Personal Finance analyzer
- Credit Stress analyzer
- Loan Risk analyzer
- User analysis history
- CSV history export
- Offline FinanceAI Assistant
- REST-style JSON APIs
- SQLite default database
- Optional MySQL/XAMPP
- Responsive professional UI
- Sample inputs
- Smoke tests
- Windows setup documentation
- Deployment notes
- Responsible-use warnings

---

## Team-Wise Module Presentation

### Ajit Kumar — Team Leader

- Introduction
- Problem statement
- Objective
- Architecture
- Flask backend
- Authentication
- Database
- Integration
- APIs
- Conclusion
- Future scope

### Ajeet Kumar

- Personal Finance
- Financial Health Score
- Components
- Recommendations
- History

### Sonu Kumar

- Credit Stress target
- Logistic Regression
- Metrics
- Threshold tuning
- Explainability
- Proxy-label limitation

### Pranav Kr Mishra

- Loan Risk target
- Class imbalance
- Extra Trees
- Threshold
- Input schema
- Testing
- Limitations

---

## Responsible-Use Boundary

The final application is a portfolio/demo and educational analytics system.

The Credit Stress and Loan Risk outputs must never be used as automatic approval/rejection decisions.

---

## Future Scope

- Real transaction integration
- Real repayment outcomes
- Larger temporal datasets
- Better-calibrated risk scores
- Fairness testing
- Cloud deployment
- Role-based administration
- Mobile / PWA version
- Advanced user-approved AI assistant
