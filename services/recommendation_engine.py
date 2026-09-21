def generate_recommendations(data, health):
    def num(name, default=0):
        raw = data.get(name, default)
        try:
            return float(raw or default)
        except (TypeError, ValueError):
            return float(default)

    dti = num("debt_to_income_ratio")
    credit = num("credit_score")
    subscriptions = int(num("subscription_services"))
    stress = str(data.get("financial_stress_level", "")).strip().lower()

    expense_ratio = health["expense_to_income_ratio"]
    loan_ratio = health["loan_to_income_ratio"]
    investment_ratio = health["investment_to_income_ratio"]
    emergency_months = health["emergency_fund_months"]
    goal_progress = health["goal_progress_ratio"]

    recs = []

    def add(priority, category, message):
        recs.append({"priority": priority, "category": category, "message": message})

    if expense_ratio > 1:
        add(1, "Cash Flow", "Expenses are above income. Reduce discretionary expenses and rebuild the monthly budget first.")
    elif expense_ratio > .90:
        add(2, "Spending", "More than 90% of income is being spent. Create a larger monthly cash-flow buffer.")

    if dti > .40:
        add(1, "Debt", "Debt-to-income is high. Prioritize repayment of expensive debt and avoid unnecessary new borrowing.")

    if loan_ratio > .30:
        add(1, "Loan Burden", "Monthly loan payments are high relative to income. Review repayment options before adding new debt.")

    if emergency_months < 1:
        add(1, "Emergency Fund", "Build at least one month of essential expenses first, then gradually target 3–6 months.")
    elif emergency_months < 3:
        add(2, "Emergency Fund", "Your emergency fund is below three months. Continue building it before increasing riskier investments.")

    if goal_progress < .50:
        add(2, "Savings", "Savings progress is below 50% of the goal. Use smaller milestones and automate savings where possible.")

    if investment_ratio < .05 and dti <= .40 and emergency_months >= 1:
        add(3, "Investment", "After essential obligations are covered, consider gradually increasing long-term investments.")

    if credit < 650:
        add(2, "Credit", "Focus on on-time payments, lower utilization, and avoiding unnecessary credit applications.")

    if subscriptions >= 7:
        add(3, "Subscriptions", "Review recurring subscriptions and cancel low-value services.")

    if stress == "high":
        add(2, "Financial Stress", "Simplify the budget and focus on the largest controllable expense categories.")

    if not recs:
        add(4, "Maintain", "Your current indicators are comparatively healthy. Maintain controlled spending, emergency savings, and regular investing.")

    return sorted(recs, key=lambda r: r["priority"])[:5]
