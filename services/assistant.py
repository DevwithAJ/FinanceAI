from __future__ import annotations


def _contains(text: str, *phrases: str) -> bool:
    return any(p in text for p in phrases)


def respond(message, latest_personal=None):
    """Deterministic local helper used with the Local RAG assistant.

    The local assistant intentionally stays conservative. It can answer common
    English/Hinglish/Hindi-transliteration finance questions and uses the latest
    Personal Finance result when available.
    """
    text = (message or "").strip().lower()
    if not text:
        return (
            "Ask me about your score, savings/bachat, expenses/kharcha, debt/karz, "
            "emergency fund, credit habits, investments, goals, or FinanceAI model results."
        )

    health = None
    if latest_personal:
        health = latest_personal.get("health", latest_personal)

    if _contains(text, "my score", "health score", "score mean", "mera score", "score kya", "financial health"):
        if health:
            score = health.get("financial_health_score")
            level = health.get("financial_health_level")
            return (
                f"Your latest FinanceAI health score is {score}/100 ({level}). "
                "Start with the lowest component scores and the priority recommendations shown in your saved result."
            )
        return "No saved Personal Finance analysis is available yet. Run Financial Health once so FinanceAI can use your score."

    if _contains(text, "emergency", "emergency fund", "backup fund", "emergency paisa"):
        if health:
            months = health.get("emergency_fund_months", 0)
            return (
                f"Your latest emergency-fund coverage is about {months} months. "
                "A practical sequence is: build a small buffer, then about one month of essentials, then gradually work toward several months based on your situation."
            )
        return "A practical emergency-fund approach is to build a small buffer first, then about one month of essential expenses, and increase it gradually."

    if _contains(text, "debt", "dti", "loan burden", "karz", "udhar", "emi pressure"):
        if health:
            dti = health.get("loan_to_income_ratio", 0)
            return (
                f"Your latest monthly loan-to-income ratio is about {float(dti or 0) * 100:.1f}%. "
                "Keep required payments current, avoid unnecessary high-cost borrowing, and direct extra cash toward expensive debt when practical."
            )
        return "For debt management, keep all required payments current, avoid unnecessary high-cost borrowing, and prioritize expensive debt with extra available cash."

    if _contains(text, "saving", "savings", "save more", "bachat", "paisa bach", "बचत"):
        if health:
            progress = health.get("goal_progress_ratio", 0)
            return (
                f"Your latest savings-goal progress is about {float(progress or 0) * 100:.1f}%. "
                "Try a realistic monthly target, automate it soon after income arrives, and review your largest flexible expense categories."
            )
        return "To improve savings, set a realistic monthly target, automate it after income arrives, and review the largest flexible spending categories."

    if _contains(text, "expense", "spending", "kharcha", "kharche", "खर्च"):
        return "Use Transactions and Spending Insights to identify your largest categories, compare them with your budget, and review unusually large transactions before cutting essential expenses."

    if _contains(text, "credit score", "cibil", "credit", "सिबिल"):
        return "Healthy credit habits include paying on time, keeping revolving utilization manageable, avoiding unnecessary applications, and checking official credit reports for errors. FinanceAI does not provide an official bureau score."

    if _contains(text, "invest", "investment", "nivesh", "sip", "mutual fund", "निवेश"):
        return "Before taking more investment risk, consider near-term expenses, expensive debt, emergency savings, time horizon, and liquidity needs. FinanceAI provides educational guidance, not investment advice."

    if _contains(text, "goal", "lakshya", "target", "लक्ष्य"):
        return "For a goal, enter the target amount, current amount, and target date. FinanceAI estimates progress and a monthly contribution target so the goal becomes easier to track."

    if _contains(text, "loan risk", "loan model", "loan ka risk", "loan risk kya"):
        return "Loan Risk is an experimental research signal trained on historical 2018 U.S. loan data. It helps demonstrate risk ranking, but it is not a bank approval/rejection decision or a guaranteed default probability."

    if _contains(text, "credit card model", "stress model", "credit stress", "stress kya"):
        return "Credit Stress is an experimental financial-stress proxy. It is useful for education and model demonstration, but it is not an official credit score or a calibrated default probability."

    return (
        "I can explain your FinanceAI results in simple language. Try: "
        "'Mera score samjhao', 'Savings kaise improve karu?', 'Kharcha kaise control karu?', "
        "'Loan Risk kya hai?', or 'Credit Stress samjhao'."
    )
