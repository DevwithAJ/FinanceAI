# 💰 Finance AI

An AI-powered Personal Finance Management System built using **Python, Streamlit, Machine Learning, and MySQL**. The system helps users track income, expenses, and savings while providing intelligent financial insights, budgeting recommendations, expense predictions, and financial health analysis.

---

## 📌 Abstract

Finance AI is an AI-powered finance management system that helps users track income, expenses, and savings. The system analyzes spending patterns, provides smart budgeting recommendations, predicts future expenses, and generates financial insights.

It is designed to improve financial planning, promote better saving habits, and support informed financial decision-making for students, professionals, families, freelancers, and small business owners.

---

## 🎯 Problem Statement

Managing personal finances effectively can be challenging due to:

- Lack of proper expense tracking
- Poor budgeting habits
- Difficulty in predicting future expenses
- Limited financial insights
- Inability to assess financial health

Finance AI solves these problems using Artificial Intelligence and Machine Learning.

---

## 👥 Target Users

- Students
- Working Professionals
- Families
- Freelancers
- Small Business Owners

---

# 🚀 Features

## 🔐 User Authentication

- User Registration
- Secure Login
- User Profile Management

---

## 💵 Income Management

- Add Income
- View Income History
- Update Income Records
- Income Analytics

---

## 💸 Expense Management

- Add Expenses
- Categorize Expenses
- Expense History
- Expense Analysis

Categories include:

- Food
- Travel
- Shopping
- Bills
- Healthcare
- Education
- Entertainment

---

## 🏦 Savings Tracking

- Calculate Monthly Savings
- Track Savings Growth
- Savings Reports
- Goal Monitoring

Formula:

```text
Savings = Income - Expenses
```

---

## 📊 Dashboard Analytics

Interactive Dashboard showing:

- Total Income
- Total Expenses
- Total Savings
- Financial Health Score
- Expense Distribution

Charts:

- Pie Charts
- Line Charts
- Bar Charts

---

## 🤖 AI Budget Recommendation

Provides intelligent recommendations such as:

- Reduce unnecessary expenses
- Increase savings rate
- Improve budget planning
- Optimize spending patterns

---

## 🔮 Expense Prediction

Machine Learning model predicts future expenses using:

- Monthly Income
- Savings Rate
- Budget Goal
- Credit Score
- Debt-to-Income Ratio
- Essential Spending
- Discretionary Spending

Algorithm:

```text
Random Forest Regressor
```

Output:

```text
Predicted Monthly Expense
```

---

## 😟 Financial Stress Prediction

Predicts financial stress level:

- Low
- Medium
- High

Algorithm:

```text
Random Forest Classifier
```

---

## 🎯 Savings Goal Prediction

Predicts whether a user can achieve their savings goal.

Output:

```text
Goal Achieved
Goal Not Achieved
```

Algorithm:

```text
Random Forest Classifier
```

---

## 📈 Spending Pattern Analysis

Analyzes:

- Spending Categories
- Monthly Trends
- Essential vs Discretionary Spending
- Cash Flow Status

---

## 🧠 Financial Insights

Examples:

- High Spending Alerts
- Budget Warnings
- Savings Suggestions
- Financial Improvement Tips

---

## 📑 Reports

Generate:

- Monthly Financial Report
- Expense Report
- Savings Report

Export Formats:

- CSV
- PDF

---

# 🏗️ System Architecture

```text
User
  │
  ▼
Streamlit Frontend
  │
  ▼
Python Backend
  │
  ├── Income Module
  ├── Expense Module
  ├── Savings Module
  ├── AI Recommendation Module
  │
  ▼
Machine Learning Models
  │
  ├── Expense Prediction
  ├── Stress Prediction
  └── Savings Goal Prediction
  │
  ▼
MySQL Database
```

---

# 🗄️ Database Tables

## Users

```sql
user_id
name
email
password
```

## Income

```sql
income_id
user_id
amount
source
date
```

## Expenses

```sql
expense_id
user_id
category
amount
date
description
```

## Budget

```sql
budget_id
user_id
budget_amount
month
```

---

# 🤖 Machine Learning Models

## Expense Prediction Model

Target:

```text
monthly_expense_total
```

Algorithm:

```text
Random Forest Regressor
```

Saved File:

```text
expense_model.pkl
```

---

## Financial Stress Model

Target:

```text
financial_stress_level
```

Algorithm:

```text
Random Forest Classifier
```

Saved File:

```text
stress_model.pkl
```

---

## Savings Goal Model

Target:

```text
savings_goal_met
```

Algorithm:

```text
Random Forest Classifier
```

Saved File:

```text
savings_goal_model.pkl
```

---

# 🛠️ Technologies Used

## Frontend

- Streamlit

## Backend

- Python

## Database

- MySQL

## Machine Learning

- Scikit-Learn
- Random Forest

## Data Processing

- Pandas
- NumPy

## Visualization

- Plotly
- Matplotlib

---

# 📂 Project Structure

```text
FinanceAI/
│
├── app.py
├── model.py
├── finance_dataset.csv
│
├── expense_model.pkl
├── stress_model.pkl
├── savings_goal_model.pkl
│
├── pages/
│   ├── Dashboard.py
│   ├── Income.py
│   ├── Expense.py
│   ├── Budget.py
│   └── Reports.py
│
├── database/
│   └── db.py
│
├── assets/
│
└── README.md
```

---

# ⚙️ Installation

Clone Repository:

```bash
git clone https://github.com/yourusername/FinanceAI.git
```

Move into project folder:

```bash
cd FinanceAI
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Train Models

```bash
python model.py
```

Generated Files:

```text
expense_model.pkl
stress_model.pkl
savings_goal_model.pkl
```

---

# ▶️ Run Application

```bash
streamlit run app.py
```

Open Browser:

```text
http://localhost:8501
```

---

# 📊 Expected Outcomes

- Better Financial Planning
- Improved Savings Habits
- Smart Budget Recommendations
- Future Expense Prediction
- Financial Health Assessment
- AI-powered Financial Insights

---

# 🔮 Future Enhancements

- AI Chatbot Assistant
- Voice-based Finance Assistant
- Investment Recommendations
- Mobile Application
- Real-Time Bank Integration
- OCR Receipt Scanner

---

# 👨‍💻 Team

**Finance Squad**

Members:

- Ajit Kumar
- Ajeet Kumar
- Sonu Kumar

---

# 📜 License

This project is developed for academic and educational purposes.

---

## ⭐ Finance AI

**Intelligent Personal Finance Management and Prediction System using Artificial Intelligence and Machine Learning**