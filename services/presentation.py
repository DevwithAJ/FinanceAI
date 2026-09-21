from __future__ import annotations

from datetime import datetime
from typing import Any

from .loan_feature_builder import US_STATE_NAMES

MODULE_META = {
    "personal_finance": {
        "title": "Financial Health Analysis",
        "description": "A 100-point snapshot of income, spending, debt, savings, investments and emergency preparedness.",
    },
    "credit_card": {
        "title": "Credit Stress Analysis",
        "description": "A simple view of an experimental financial-stress research signal. It is not a credit approval or default decision.",
    },
    "loan_risk": {
        "title": "Loan Risk Research Analysis",
        "description": "A simple view of an experimental model trained on historical 2018 U.S. loan data. It is not a lending decision.",
    },
    "cashflow_forecast": {
        "title": "Cash-flow Forecast",
        "description": "An estimate of future income, expenses and savings from the transaction history recorded in FinanceAI.",
    },
}

FIELD_LABELS = {
    "monthly_income": "Monthly Income", "monthly_expense_total": "Monthly Expenses",
    "debt_to_income_ratio": "Debt-to-Income Ratio", "loan_payment": "Monthly Loan Payment",
    "investment_amount": "Monthly Investment", "emergency_fund": "Emergency Fund",
    "credit_score": "Credit Score", "budget_goal": "Monthly Savings Goal",
    "actual_savings": "Actual Monthly Savings", "subscription_services": "Subscription Services",
    "financial_stress_level": "Financial Stress Level", "Age": "Age", "Dependents": "Dependents",
    "Occupation": "Occupation", "City_Tier": "City Tier", "Desired_Savings_Percentage": "Desired Savings",
    "emp_length": "Employment Length", "state": "State", "homeownership": "Home Ownership",
    "annual_income": "Annual Income", "verified_income": "Income Verification",
    "annual_income_joint": "Joint Annual Income", "verification_income_joint": "Joint Income Verification",
    "application_type": "Application Type", "debt_to_income": "Debt-to-Income (DTI)",
    "debt_to_income_joint": "Joint Debt-to-Income (DTI)", "loan_amount": "Loan Amount",
    "term": "Loan Term", "loan_purpose": "Loan Purpose", "delinq_2y": "Delinquencies in Last 2 Years",
    "months_since_last_delinq": "Months Since Last Delinquency", "earliest_credit_line": "Earliest Credit Line Year",
    "inquiries_last_12m": "Credit Inquiries in Last 12 Months", "total_credit_lines": "Total Credit Lines",
    "open_credit_lines": "Open Credit Lines", "total_credit_limit": "Total Credit Limit",
    "total_credit_utilized": "Total Credit Used", "num_collections_last_12m": "Collections in Last 12 Months",
    "num_historical_failed_to_pay": "Historical Failed Payments", "months_since_90d_late": "Months Since 90+ Day Late Payment",
    "current_accounts_delinq": "Currently Delinquent Accounts", "total_collection_amount_ever": "Total Collection Amount",
    "current_installment_accounts": "Current Installment Accounts", "accounts_opened_24m": "Accounts Opened in Last 24 Months",
    "months_since_last_credit_inquiry": "Months Since Last Credit Inquiry", "num_satisfactory_accounts": "Satisfactory Accounts",
    "num_accounts_120d_past_due": "Accounts 120+ Days Past Due", "num_accounts_30d_past_due": "Accounts 30+ Days Past Due",
    "num_active_debit_accounts": "Active Debit Accounts", "total_debit_limit": "Total Debit Limit",
    "num_total_cc_accounts": "Total Credit Card Accounts", "num_open_cc_accounts": "Open Credit Card Accounts",
    "num_cc_carrying_balance": "Credit Cards Carrying Balance", "num_mort_accounts": "Mortgage Accounts",
    "account_never_delinq_percent": "Accounts Never Delinquent", "tax_liens": "Tax Liens",
    "public_record_bankrupt": "Public Bankruptcy Records", "emp_length_missing": "Employment Length Missing",
    "financial_health_score": "Financial Health Score", "financial_health_level": "Financial Health Level",
    "expense_to_income_ratio": "Expense-to-Income Ratio", "loan_to_income_ratio": "Loan-to-Income Ratio",
    "investment_to_income_ratio": "Investment-to-Income Ratio", "goal_progress_ratio": "Savings Goal Progress",
    "emergency_fund_months": "Emergency Fund Coverage", "risk_score": "Experimental Risk Score",
    "threshold": "Model Threshold", "predicted_class": "Model Class", "warning": "Responsible-use Notice",
    "reference_year": "Model Reference Year", "transaction_count": "Transactions Used",
    "months_of_history": "Months of History", "method": "Forecast Method", "days": "Forecast Horizon",
    "income": "Projected Income", "expense": "Projected Expenses", "savings": "Projected Savings",
    "savings_rate": "Projected Savings Rate", "note": "Important Note",
}

CURRENCY_FIELDS = {
    "monthly_income", "monthly_expense_total", "loan_payment", "investment_amount", "emergency_fund",
    "budget_goal", "actual_savings", "annual_income", "annual_income_joint", "loan_amount",
    "total_credit_limit", "total_credit_utilized", "total_collection_amount_ever", "total_debit_limit",
    "income", "expense", "savings", "spent", "remaining", "target_amount", "current_amount",
    "monthly_required", "net_worth", "assets", "investments", "liabilities",
}
RATIO_FIELDS = {"debt_to_income_ratio", "expense_to_income_ratio", "loan_to_income_ratio", "investment_to_income_ratio", "goal_progress_ratio", "credit_utilization_ratio", "open_credit_ratio", "cc_carrying_balance_ratio", "active_debit_ratio", "inquiries_per_credit_line"}
PERCENT_VALUE_FIELDS = {"Desired_Savings_Percentage", "account_never_delinq_percent", "savings_rate", "percent", "progress", "debt_to_income", "debt_to_income_joint"}
MODEL_FIELDS = {"score", "risk_score", "threshold", "predicted_class"}
INTERNAL_FIELDS = {"ok", "module", "production_ready", "error", "missing_fields", "missing_features"}


def module_title(module_name: str) -> str:
    return MODULE_META.get(module_name, {}).get("title") or str(module_name or "Analysis").replace("_", " ").title()


def module_description(module_name: str) -> str:
    return MODULE_META.get(module_name, {}).get("description", "A saved FinanceAI analysis with the inputs used and the output produced at that time.")


def friendly_date(value: Any) -> str:
    if not value:
        return "—"
    text = str(value)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text[:19] if "%S" in fmt else text[:10], fmt)
            return dt.strftime("%d %b %Y, %I:%M %p") if "%S" in fmt else dt.strftime("%d %b %Y")
        except ValueError:
            continue
    return text


def label_for(key: str) -> str:
    return FIELD_LABELS.get(key, str(key).replace("_", " ").strip().title())


def _number(value: Any):
    try:
        if isinstance(value, bool):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def format_value(key: str, value: Any) -> str:
    if value is None or value == "": return "Not provided"
    if isinstance(value, bool): return "Yes" if value else "No"
    if key == "state":
        code = str(value).strip().upper()
        return f"{US_STATE_NAMES.get(code, code)} ({code})" if code in US_STATE_NAMES else str(value)
    if key == "term":
        n = _number(value); return f"{int(n)} months" if n is not None else str(value)
    if key == "emp_length":
        n = _number(value); return f"{n:g} years" if n is not None else str(value)
    if key == "emergency_fund_months":
        n = _number(value); return f"{n:.1f} months" if n is not None else str(value)
    if key == "days":
        n = _number(value); return f"{int(n)} days" if n is not None else str(value)
    if key == "financial_health_score":
        n = _number(value); return f"{n:.0f}/100" if n is not None else str(value)
    if key in {"score", "risk_score", "threshold"}:
        n = _number(value); return f"{n * 100:.1f}/100" if n is not None else str(value)
    if key == "predicted_class":
        n = _number(value); return "Above model threshold" if n is not None and int(n) else "Below model threshold"
    if key in {"earliest_credit_line", "reference_year"}:
        n = _number(value); return str(int(n)) if n is not None else str(value)
    if key in RATIO_FIELDS:
        n = _number(value); return f"{n * 100:.1f}%" if n is not None else str(value)
    if key in PERCENT_VALUE_FIELDS:
        n = _number(value); return f"{n:.1f}%" if n is not None else str(value)
    if key in CURRENCY_FIELDS or (any(t in key.lower() for t in ("amount", "income", "expense", "saving", "fund", "payment", "limit", "utilized")) and not key.lower().endswith("_flag")):
        n = _number(value); return f"₹{n:,.2f}" if n is not None else str(value)
    if key.endswith("_flag"):
        n = _number(value); return "Yes" if n is not None and int(n) else "No"
    n = _number(value)
    if n is not None and not isinstance(value, str): return f"{n:,.2f}".rstrip("0").rstrip(".")
    text = str(value)
    if "_" in text and len(text) < 80: return text.replace("_", " ").title()
    if text.isupper() and len(text) > 2: return text.title()
    return text


def _flatten(mapping: Any, prefix: str = "") -> list[dict[str, str]]:
    rows = []
    if not isinstance(mapping, dict): return rows
    for key, value in mapping.items():
        if key in INTERNAL_FIELDS or key in {"_csrf_token", "password", "password_hash"}: continue
        full_label = f"{prefix} · {label_for(key)}" if prefix else label_for(key)
        if isinstance(value, dict): rows.extend(_flatten(value, full_label))
        elif isinstance(value, list):
            if not value: rows.append({"label": full_label, "value": "None"})
            elif all(isinstance(item, dict) for item in value):
                for idx, item in enumerate(value, 1):
                    if "message" in item:
                        rows.append({"label": f"{full_label} {idx}", "value": str(item.get("message"))})
                    else: rows.extend(_flatten(item, f"{full_label} {idx}"))
            else: rows.append({"label": full_label, "value": ", ".join(str(v) for v in value)})
        else: rows.append({"label": full_label, "value": format_value(key, value)})
    return rows


def _raw_score(module_name: str, result: dict, fallback=None):
    key = "risk_score" if module_name == "loan_risk" else "score"
    return _number(result.get(key, fallback))


def signal_band(module_name: str, score: Any, threshold: Any) -> dict:
    s, t = _number(score), _number(threshold)
    if s is None:
        return {"level": "Not available", "tone": "neutral", "class": "neutral", "meaning": "A readable level could not be calculated for this record."}
    if t is None or t <= 0: t = 0.5
    if s >= t:
        level, tone = "High", "high"
    elif s >= t * 0.60:
        level, tone = "Moderate", "moderate"
    else:
        level, tone = "Low", "low"
    if module_name == "credit_card":
        meaning = {
            "Low": "The research model found a lower financial-stress signal for the profile you entered.",
            "Moderate": "The research model found a mid-range financial-stress signal. Review savings and household cash-flow buffers.",
            "High": "The research model found an elevated financial-stress signal. Review savings, expenses and cash-flow buffers carefully.",
        }[level]
    else:
        meaning = {
            "Low": "The historical research model produced a lower risk signal for the loan profile you entered.",
            "Moderate": "The historical research model produced a mid-range risk signal. Review debt, utilization and repayment-history inputs.",
            "High": "The historical research model produced an elevated risk signal. Review debt, utilization and repayment-history inputs carefully.",
        }[level]
    return {"level": level, "tone": tone, "class": tone, "meaning": meaning}


def _insight(title: str, value: str, meaning: str, tone="neutral"):
    return {"factor": title, "value": value, "meaning": meaning, "tone": tone}


def profile_insights(module_name: str, data: dict) -> list[dict]:
    out = []
    if module_name == "credit_card":
        savings = _number(data.get("Desired_Savings_Percentage"))
        deps = _number(data.get("Dependents"))
        occupation = str(data.get("Occupation", "")).replace("_", " ").title()
        city = str(data.get("City_Tier", "")).replace("_", " ").title()
        if savings is not None:
            tone = "high" if savings < 10 else "moderate" if savings < 20 else "low"
            out.append(_insight("Savings Target", f"{savings:.1f}%", "A larger realistic savings target can create more room for emergencies and goals.", tone))
        if deps is not None:
            out.append(_insight("Dependents", f"{int(deps)}", "More dependents can increase household cash-flow responsibilities; plan buffers accordingly.", "moderate" if deps >= 3 else "neutral"))
        if occupation:
            out.append(_insight("Occupation", occupation, "Income stability can differ by occupation. Keep an emergency buffer suitable for your income pattern.", "neutral"))
        if city:
            out.append(_insight("City Tier", city, "Living costs can vary by city tier, so compare your fixed expenses with your actual monthly income.", "neutral"))
    elif module_name == "loan_risk":
        dti = _number(data.get("debt_to_income"))
        annual_income = _number(data.get("annual_income"))
        loan_amount = _number(data.get("loan_amount"))
        utilized = _number(data.get("total_credit_utilized"))
        limit = _number(data.get("total_credit_limit"))
        delinq = _number(data.get("delinq_2y")) or 0
        failed = _number(data.get("num_historical_failed_to_pay")) or 0
        current_delinq = _number(data.get("current_accounts_delinq")) or 0
        inquiries = _number(data.get("inquiries_last_12m"))
        if dti is not None:
            tone = "high" if dti > 35 else "moderate" if dti > 25 else "low"
            out.append(_insight("Debt-to-Income (DTI)", f"{dti:.1f}%", "A lower DTI generally means more income remains after debt obligations.", tone))
        if annual_income and loan_amount is not None:
            ratio = loan_amount / annual_income if annual_income > 0 else 0
            tone = "high" if ratio > .60 else "moderate" if ratio > .35 else "low"
            out.append(_insight("Loan vs Annual Income", f"{ratio * 100:.1f}%", "This compares the requested loan amount with annual income; it is a planning ratio, not an approval rule.", tone))
        if limit and utilized is not None and limit > 0:
            util = utilized / limit
            tone = "high" if util > .80 else "moderate" if util > .50 else "low"
            out.append(_insight("Credit Utilization", f"{util * 100:.1f}%", "Lower utilization usually leaves more available credit capacity.", tone))
        if delinq > 0 or failed > 0 or current_delinq > 0:
            out.append(_insight("Repayment History", f"{int(delinq)} recent delinquencies", "Late or failed-payment history is worth reviewing for accuracy and improving over time.", "high"))
        else:
            out.append(_insight("Repayment History", "No entered recent delinquency", "No recent delinquency was entered in the fields checked here.", "low"))
        if inquiries is not None:
            out.append(_insight("Recent Credit Inquiries", f"{int(inquiries)}", "Many recent applications can indicate active credit seeking. Avoid unnecessary applications.", "moderate" if inquiries >= 6 else "neutral"))
        if data.get("state"):
            out.append(_insight("State", format_value("state", data.get("state")), "State is shown using its full U.S. name because this model was trained on historical U.S. loan data.", "neutral"))
    return out[:7]


def recommendations(module_name: str, data: dict, level: str) -> list[str]:
    recs = []
    if module_name == "credit_card":
        savings = _number(data.get("Desired_Savings_Percentage"))
        deps = _number(data.get("Dependents")) or 0
        if savings is not None and savings < 20: recs.append("Increase your savings target gradually if your monthly cash flow allows it.")
        if deps >= 2: recs.append("Keep a larger emergency buffer because household responsibilities are higher.")
        recs.extend(["Track fixed and discretionary expenses separately each month.", "Use the Budget and Goals modules to turn this result into a monthly action plan."])
    elif module_name == "loan_risk":
        dti = _number(data.get("debt_to_income"))
        util = None
        lim, used = _number(data.get("total_credit_limit")), _number(data.get("total_credit_utilized"))
        if lim and used is not None and lim > 0: util = used / lim
        if dti is not None and dti > 30: recs.append("Consider reducing debt obligations before taking on additional borrowing where practical.")
        if util is not None and util > .50: recs.append("Reducing revolving credit utilization may improve overall credit capacity.")
        if (_number(data.get("delinq_2y")) or 0) > 0 or (_number(data.get("current_accounts_delinq")) or 0) > 0: recs.append("Prioritize on-time payments and verify that repayment-history data is accurate.")
        if (_number(data.get("inquiries_last_12m")) or 0) >= 6: recs.append("Avoid unnecessary new credit applications in a short period.")
        recs.extend(["Compare the requested loan amount with income and existing obligations.", "Use this output only as an educational research signal, not as an approval or rejection decision."])
    return recs[:5]


def present_model_result(module_name: str, input_data: dict, result: dict) -> dict:
    score = _raw_score(module_name, result)
    band = signal_band(module_name, score, result.get("threshold"))
    title = "Credit Stress Result" if module_name == "credit_card" else "Loan Risk Result"
    noun = "Financial Stress" if module_name == "credit_card" else "Loan Risk"
    return {
        "title": title,
        "level": band["level"], "tone": band["tone"],
        "headline": f"{band['level']} {noun} Signal",
        "score_display": f"{score * 100:.1f} / 100" if score is not None else "—",
        "score_label": "Stress Score" if module_name == "credit_card" else "Research Risk Score",
        "meaning": band["meaning"],
        "warning": result.get("warning", "This is an educational research signal, not a financial decision."),
        "insights": profile_insights(module_name, input_data),
        "recommendations": recommendations(module_name, input_data, band["level"]),
        "technical_rows": [
            {"label": "Model threshold", "value": format_value("threshold", result.get("threshold"))},
            {"label": "Threshold status", "value": format_value("predicted_class", result.get("predicted_class"))},
            *([{"label": "Model reference year", "value": format_value("reference_year", result.get("reference_year"))}] if result.get("reference_year") else []),
        ],
    }


def score_display(module_name: str, score: Any) -> str:
    n = _number(score)
    if n is None: return "—"
    if module_name == "personal_finance": return f"{n:.0f}/100"
    if module_name in {"credit_card", "loan_risk"}: return f"{n * 100:.1f} / 100"
    if module_name == "cashflow_forecast": return f"{n:.1f}% savings rate"
    return f"{n:.2f}"


def simple_meaning(module_name: str, label: str | None, score=None, threshold=None) -> str:
    if module_name in {"credit_card", "loan_risk"}:
        return signal_band(module_name, score, threshold)["meaning"]
    label = label or "Result saved"
    if module_name == "personal_finance": return f"Your financial-health result was “{label}”. Open the record to see the ratios and recommendations behind it."
    if module_name == "cashflow_forecast": return "This record stores a projected savings-rate snapshot based on the transactions available at that time."
    return f"Saved result: {label}."


def present_history_row(row: dict) -> dict:
    module_name = row.get("module_name") or "analysis"
    result_data = row.get("result_data") or {}
    if module_name in {"credit_card", "loan_risk"}:
        band = signal_band(module_name, row.get("score"), result_data.get("threshold"))
        result_display = f"{band['level']} Signal"
        tone = band["tone"]
        meaning = band["meaning"]
    else:
        result_display = row.get("label") or "Saved result"
        tone = "neutral"
        meaning = simple_meaning(module_name, row.get("label"), row.get("score"), result_data.get("threshold"))
    return {**row, "title": module_title(module_name), "date_display": friendly_date(row.get("created_at")), "score_display": score_display(module_name, row.get("score")), "result_display": result_display, "tone": tone, "meaning": meaning}


def present_analysis_detail(row: dict) -> dict:
    module_name = row.get("module_name") or "analysis"
    result_data = row.get("result_data") or {}
    input_data = row.get("input_data") or {}
    warning = result_data.get("warning") or result_data.get("note")
    if module_name in {"credit_card", "loan_risk"}:
        view = present_model_result(module_name, input_data, result_data)
        result_rows = [
            {"label": "Level", "value": view["level"]},
            {"label": view["score_label"], "value": view["score_display"]},
            {"label": "Simple Meaning", "value": view["meaning"]},
        ]
        return {
            "title": module_title(module_name), "description": module_description(module_name),
            "date_display": friendly_date(row.get("created_at")), "result_label": row.get("label") or "Saved result",
            "result_display": f"{view['level']} Signal", "tone": view["tone"], "score_display": view["score_display"],
            "meaning": view["meaning"], "warning": warning, "input_rows": _flatten(input_data), "result_rows": result_rows,
            "insights": view["insights"], "recommendations": view["recommendations"], "technical_rows": view["technical_rows"],
        }
    return {
        "title": module_title(module_name), "description": module_description(module_name), "date_display": friendly_date(row.get("created_at")),
        "result_label": row.get("label") or "Saved result", "result_display": row.get("label") or "Saved result", "tone": "neutral",
        "score_display": score_display(module_name, row.get("score")), "meaning": simple_meaning(module_name, row.get("label"), row.get("score"), result_data.get("threshold")),
        "warning": warning, "input_rows": _flatten(input_data), "result_rows": _flatten(result_data), "insights": [], "recommendations": [], "technical_rows": [],
    }
