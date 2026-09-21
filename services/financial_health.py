def _num(data, key, default=0.0):
    value = data.get(key, default)
    if value in (None, ""):
        return float(default)
    return float(value)


def _ratio(a, b):
    return a / b if b > 0 else 0.0


def _level(score):
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 55:
        return "Moderate"
    if score >= 40:
        return "Weak"
    return "Critical"


def validate_personal_finance(data):
    errors = []

    def value(name, minimum=None, maximum=None, required=True):
        raw = data.get(name, "")
        if raw in (None, ""):
            if required:
                errors.append(f"{name} is required.")
            return None
        try:
            n = float(raw)
        except (TypeError, ValueError):
            errors.append(f"{name} must be numeric.")
            return None
        if minimum is not None and n < minimum:
            errors.append(f"{name} must be at least {minimum}.")
        if maximum is not None and n > maximum:
            errors.append(f"{name} must be at most {maximum}.")
        return n

    value("monthly_income", 0.01)
    value("monthly_expense_total", 0)
    value("debt_to_income_ratio", 0, 1.5)
    value("loan_payment", 0, required=False)
    value("investment_amount", 0, required=False)
    value("emergency_fund", 0, required=False)
    value("credit_score", 300, 900)
    value("budget_goal", 0.01)
    value("actual_savings", 0, required=False)
    value("subscription_services", 0, 100, required=False)

    return errors


def calculate_financial_health(data):
    income = max(_num(data, "monthly_income"), 0)
    expenses = max(_num(data, "monthly_expense_total"), 0)
    dti = max(_num(data, "debt_to_income_ratio"), 0)
    loan = max(_num(data, "loan_payment"), 0)
    investment = max(_num(data, "investment_amount"), 0)
    emergency = max(_num(data, "emergency_fund"), 0)
    credit = _num(data, "credit_score")
    budget_goal = max(_num(data, "budget_goal"), 0)

    default_savings = max(income - expenses, 0)
    actual_savings = max(_num(data, "actual_savings", default_savings), 0)

    expense_ratio = _ratio(expenses, income)
    loan_ratio = _ratio(loan, income)
    investment_ratio = _ratio(investment, income)
    emergency_months = _ratio(emergency, expenses)
    goal_progress = _ratio(actual_savings, budget_goal)

    cash_flow_score = 25 if expense_ratio <= .60 else 20 if expense_ratio <= .75 else 12 if expense_ratio <= .90 else 6 if expense_ratio <= 1 else 0
    debt_score = 20 if dti <= .20 else 16 if dti <= .30 else 10 if dti <= .40 else 5 if dti <= .50 else 0
    emergency_score = 20 if emergency_months >= 6 else 17 if emergency_months >= 3 else 10 if emergency_months >= 1 else 5 if emergency_months > 0 else 0
    savings_score = 15 if goal_progress >= 1 else 12 if goal_progress >= .75 else 8 if goal_progress >= .50 else 4 if goal_progress >= .25 else 0
    investment_score = 10 if investment_ratio >= .15 else 8 if investment_ratio >= .10 else 5 if investment_ratio >= .05 else 2 if investment_ratio > 0 else 0
    credit_score = 10 if credit >= 750 else 8 if credit >= 700 else 5 if credit >= 650 else 3 if credit >= 600 else 0

    total = int(cash_flow_score + debt_score + emergency_score + savings_score + investment_score + credit_score)

    risk_flags = []
    if expense_ratio > 1:
        risk_flags.append("negative_cash_flow")
    if expense_ratio > .90:
        risk_flags.append("high_expense_burden")
    if dti > .40:
        risk_flags.append("high_dti")
    if loan_ratio > .30:
        risk_flags.append("high_loan_burden")
    if emergency_months < 1:
        risk_flags.append("low_emergency_fund")
    if goal_progress < .50:
        risk_flags.append("low_savings_progress")
    if investment_ratio < .05:
        risk_flags.append("low_investment")
    if credit < 650:
        risk_flags.append("low_credit_score")

    return {
        "financial_health_score": total,
        "financial_health_level": _level(total),
        "expense_to_income_ratio": round(expense_ratio, 4),
        "loan_to_income_ratio": round(loan_ratio, 4),
        "investment_to_income_ratio": round(investment_ratio, 4),
        "emergency_fund_months": round(emergency_months, 2),
        "goal_progress_ratio": round(goal_progress, 4),
        "risk_flags": risk_flags,
        "components": {
            "Cash Flow": cash_flow_score,
            "Debt Health": debt_score,
            "Emergency Fund": emergency_score,
            "Savings Progress": savings_score,
            "Investment": investment_score,
            "Credit": credit_score,
        },
        "disclaimer": "Educational financial-health indicator; not professional financial advice.",
    }
