from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from math import ceil
import random

import numpy as np

try:
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest
    from sklearn.linear_model import LinearRegression
except Exception:  # graceful fallback if optional ML runtime is unavailable
    KMeans = IsolationForest = LinearRegression = None


INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment Income", "Gift", "Refund", "Other Income"]
EXPENSE_CATEGORIES = [
    "Housing", "Groceries", "Utilities", "Transport", "Healthcare", "Education",
    "EMI / Debt", "Insurance", "Dining", "Entertainment", "Shopping", "Travel",
    "Subscriptions", "Family", "Personal Care", "Other Expense",
]
PAYMENT_METHODS = ["UPI", "Cash", "Debit Card", "Credit Card", "Bank Transfer", "Auto Debit", "Other"]

NEED_CATEGORIES = {"Housing", "Groceries", "Utilities", "Transport", "Healthcare", "Education", "EMI / Debt", "Insurance", "Family"}
WANT_CATEGORIES = {"Dining", "Entertainment", "Shopping", "Travel", "Subscriptions", "Personal Care"}


def _f(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _d(value):
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except Exception:
        return date.today()


def month_range(month_text=None):
    if month_text:
        start = datetime.strptime(month_text + "-01", "%Y-%m-%d").date()
    else:
        today = date.today()
        start = today.replace(day=1)
    if start.month == 12:
        nxt = start.replace(year=start.year + 1, month=1)
    else:
        nxt = start.replace(month=start.month + 1)
    return start.isoformat(), (nxt - timedelta(days=1)).isoformat(), start.strftime("%Y-%m")


def budget_plan(monthly_income):
    income = max(0.0, _f(monthly_income))
    return {
        "income": round(income, 2),
        "needs": round(income * 0.50, 2),
        "wants": round(income * 0.30, 2),
        "savings_debt": round(income * 0.20, 2),
    }


def budget_snapshot(totals, category_rows, budgets):
    spend = {r["category"]: _f(r["total"]) for r in category_rows}
    items = []
    for b in budgets:
        used = spend.get(b["category"], 0.0)
        limit = _f(b["monthly_limit"])
        pct = (used / limit * 100) if limit > 0 else 0.0
        items.append({
            **b,
            "spent": round(used, 2),
            "remaining": round(limit - used, 2),
            "percent": round(pct, 1),
            "status": "over" if pct > 100 else ("warning" if pct >= 80 else "ok"),
        })

    needs = sum(v for k, v in spend.items() if k in NEED_CATEGORIES)
    wants = sum(v for k, v in spend.items() if k in WANT_CATEGORIES)
    uncategorized = max(0.0, _f(totals.get("expense")) - needs - wants)
    target = budget_plan(totals.get("income", 0))
    return {
        "items": items,
        "actual": {"needs": round(needs, 2), "wants": round(wants, 2), "other": round(uncategorized, 2)},
        "target": target,
    }


def _monthly_series(transactions):
    grouped = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for t in transactions:
        key = str(t.get("transaction_date"))[:7]
        typ = t.get("transaction_type")
        if typ in ("income", "expense"):
            grouped[key][typ] += _f(t.get("amount"))
    return [(m, grouped[m]["income"], grouped[m]["expense"]) for m in sorted(grouped)]


def _predict_series(values, steps):
    vals = np.asarray(values, dtype=float)
    if len(vals) == 0:
        return [0.0] * steps, "no-data"
    if len(vals) >= 3 and LinearRegression is not None:
        x = np.arange(len(vals)).reshape(-1, 1)
        model = LinearRegression().fit(x, vals)
        pred = model.predict(np.arange(len(vals), len(vals) + steps).reshape(-1, 1))
        # Blend linear trend with recent mean to avoid extreme projections on tiny histories.
        recent = float(np.mean(vals[-min(3, len(vals)):]))
        pred = np.maximum(0, pred * 0.65 + recent * 0.35)
        return pred.tolist(), "linear-regression"
    avg = float(np.mean(vals[-min(3, len(vals)):]))
    return [max(0.0, avg)] * steps, "moving-average"


def forecast_finances(transactions):
    series = _monthly_series(transactions)
    incomes = [r[1] for r in series]
    expenses = [r[2] for r in series]
    inc_pred, inc_method = _predict_series(incomes, 3)
    exp_pred, exp_method = _predict_series(expenses, 3)

    horizons = []
    for months in (1, 2, 3):
        income = sum(inc_pred[:months])
        expense = sum(exp_pred[:months])
        horizons.append({
            "days": months * 30,
            "income": round(income, 2),
            "expense": round(expense, 2),
            "savings": round(income - expense, 2),
            "savings_rate": round(((income - expense) / income * 100), 2) if income > 0 else 0.0,
        })
    history = [
        {"month": m, "income": round(i, 2), "expense": round(e, 2), "savings": round(i - e, 2)}
        for m, i, e in series[-12:]
    ]
    return {
        "ok": bool(series),
        "history": history,
        "horizons": horizons,
        "method": inc_method if inc_method == exp_method else f"{inc_method} / {exp_method}",
        "months_of_history": len(series),
        "note": "Forecasts are estimates based on your recorded transaction history, not guaranteed outcomes.",
    }


def detect_anomalies(transactions):
    expenses = [t for t in transactions if t.get("transaction_type") == "expense" and _f(t.get("amount")) > 0]
    if not expenses:
        return {"method": "no-data", "count": 0, "items": []}

    amounts = np.array([_f(t["amount"]) for t in expenses], dtype=float)
    flagged = []
    method = "robust-threshold"
    if len(expenses) >= 8 and IsolationForest is not None:
        model = IsolationForest(n_estimators=120, contamination=min(0.15, max(0.05, 2 / len(expenses))), random_state=42)
        x = amounts.reshape(-1, 1)
        labels = model.fit_predict(x)
        scores = -model.score_samples(x)
        for t, label, score in zip(expenses, labels, scores):
            if int(label) == -1:
                flagged.append({**t, "anomaly_score": round(float(score), 4), "reason": "Unusual amount compared with your expense history"})
        method = "isolation-forest"
    else:
        median = float(np.median(amounts))
        mad = float(np.median(np.abs(amounts - median))) or max(1.0, median * 0.20)
        threshold = median + 3.5 * mad
        for t in expenses:
            amount = _f(t["amount"])
            if amount > threshold:
                flagged.append({**t, "anomaly_score": round(amount / max(threshold, 1), 4), "reason": "Amount is far above your typical expense"})

    flagged.sort(key=lambda x: x.get("anomaly_score", 0), reverse=True)
    return {"method": method, "count": len(flagged), "items": flagged[:12]}


def spending_behavior(category_rows):
    if not category_rows:
        return {"profile": "No data", "top_category": None, "concentration": 0, "clusters": [], "method": "no-data"}
    totals = np.array([_f(r["total"]) for r in category_rows], dtype=float)
    overall = float(totals.sum()) or 1.0
    top_idx = int(np.argmax(totals))
    top_share = float(totals[top_idx] / overall * 100)
    need_share = sum(_f(r["total"]) for r in category_rows if r["category"] in NEED_CATEGORIES) / overall * 100
    want_share = sum(_f(r["total"]) for r in category_rows if r["category"] in WANT_CATEGORIES) / overall * 100

    if need_share >= 65:
        profile = "Essentials Heavy"
    elif want_share >= 40:
        profile = "Lifestyle Heavy"
    elif top_share >= 50:
        profile = "Concentrated Spending"
    else:
        profile = "Balanced Mix"

    clusters = []
    if len(category_rows) >= 3 and KMeans is not None:
        k = min(3, len(category_rows))
        features = np.array([[v, v / overall] for v in totals], dtype=float)
        km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(features)
        center_order = np.argsort(km.cluster_centers_[:, 0])
        names = {int(cluster): ["Low", "Medium", "High"][min(rank, 2)] for rank, cluster in enumerate(center_order)}
        for row, label in zip(category_rows, km.labels_):
            clusters.append({"category": row["category"], "total": round(_f(row["total"]), 2), "cluster": names[int(label)]})
        method = "k-means"
    else:
        for row in category_rows:
            share = _f(row["total"]) / overall
            cluster = "High" if share >= .30 else ("Medium" if share >= .12 else "Low")
            clusters.append({"category": row["category"], "total": round(_f(row["total"]), 2), "cluster": cluster})
        method = "share-bands"

    return {
        "profile": profile,
        "top_category": category_rows[top_idx]["category"],
        "concentration": round(top_share, 1),
        "needs_share": round(need_share, 1),
        "wants_share": round(want_share, 1),
        "clusters": clusters,
        "method": method,
    }


def enrich_goals(goals):
    today = date.today()
    out = []
    for g in goals:
        target = max(0.0, _f(g.get("target_amount")))
        current = max(0.0, _f(g.get("current_amount")))
        remaining = max(0.0, target - current)
        target_date = _d(g.get("target_date")) if g.get("target_date") else None
        months_left = None
        monthly_required = None
        if target_date:
            days = (target_date - today).days
            months_left = max(0, ceil(days / 30))
            monthly_required = remaining / max(1, months_left) if remaining else 0
        progress = min(100.0, (current / target * 100) if target else 0.0)
        out.append({
            **g,
            "progress": round(progress, 1),
            "remaining": round(remaining, 2),
            "months_left": months_left,
            "monthly_required": round(monthly_required, 2) if monthly_required is not None else None,
        })
    return out


def government_schemes():
    # Educational discovery data; deliberately avoids time-sensitive interest rates/limits.
    return [
        {"name": "Public Provident Fund (PPF)", "type": "Long-term savings", "fit": "People seeking a government-backed long-term savings option", "note": "Check current rules, rates and tax treatment on official government/bank sources."},
        {"name": "National Pension System (NPS)", "type": "Retirement", "fit": "People building long-term retirement savings", "note": "Market-linked retirement product; allocation and withdrawal rules apply."},
        {"name": "Atal Pension Yojana (APY)", "type": "Pension", "fit": "Eligible subscribers seeking a defined pension-oriented scheme", "note": "Eligibility and contribution rules should be verified on the official portal."},
        {"name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)", "type": "Life insurance", "fit": "Eligible bank-account holders looking for basic life cover", "note": "Premium and eligibility can change; verify before enrollment."},
        {"name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)", "type": "Accident insurance", "fit": "Eligible bank-account holders looking for basic accident cover", "note": "Verify current premium, age and renewal conditions."},
        {"name": "Sukanya Samriddhi Yojana", "type": "Child savings", "fit": "Eligible guardians saving for a girl child", "note": "Account eligibility and deposit rules apply; verify current official terms."},
    ]


def generate_demo_transactions(months=6, seed=42):
    rng = random.Random(seed)
    today = date.today()
    rows = []
    for offset in range(months - 1, -1, -1):
        year = today.year
        month = today.month - offset
        while month <= 0:
            month += 12; year -= 1
        base_date = date(year, month, min(5, 28))
        salary = 52000 + rng.randint(-2500, 3500)
        rows.append({"transaction_type": "income", "amount": salary, "category": "Salary", "description": "Monthly salary", "transaction_date": base_date.isoformat(), "payment_method": "Bank Transfer", "is_recurring": True})
        expense_map = {
            "Housing": 12000, "Groceries": 6500, "Utilities": 2800, "Transport": 3500,
            "Dining": 2400, "Entertainment": 1600, "Subscriptions": 700, "Healthcare": 1200,
        }
        for idx, (cat, base) in enumerate(expense_map.items(), start=1):
            amount = max(100, base + rng.randint(-int(base*.18), int(base*.18)))
            day = min(7 + idx * 2, 26)
            rows.append({"transaction_type": "expense", "amount": amount, "category": cat, "description": f"Demo {cat.lower()} expense", "transaction_date": date(year, month, day).isoformat(), "payment_method": "UPI" if cat not in {"Housing", "Utilities"} else "Bank Transfer", "is_recurring": cat in {"Housing", "Utilities", "Subscriptions"}})
    return rows
