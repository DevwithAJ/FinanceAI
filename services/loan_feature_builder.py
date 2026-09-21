import math
import numpy as np


NUMERIC_RAW_FIELDS = [
    "emp_length",
    "annual_income",
    "debt_to_income",
    "annual_income_joint",
    "debt_to_income_joint",
    "delinq_2y",
    "months_since_last_delinq",
    "earliest_credit_line",
    "inquiries_last_12m",
    "total_credit_lines",
    "open_credit_lines",
    "total_credit_limit",
    "total_credit_utilized",
    "num_collections_last_12m",
    "num_historical_failed_to_pay",
    "months_since_90d_late",
    "current_accounts_delinq",
    "total_collection_amount_ever",
    "current_installment_accounts",
    "accounts_opened_24m",
    "months_since_last_credit_inquiry",
    "num_satisfactory_accounts",
    "num_accounts_120d_past_due",
    "num_accounts_30d_past_due",
    "num_active_debit_accounts",
    "total_debit_limit",
    "num_total_cc_accounts",
    "num_open_cc_accounts",
    "num_cc_carrying_balance",
    "num_mort_accounts",
    "account_never_delinq_percent",
    "tax_liens",
    "public_record_bankrupt",
    "loan_amount",
    "term",
]

CATEGORICAL_RAW_FIELDS = [
    "state",
    "homeownership",
    "verified_income",
    "verification_income_joint",
    "loan_purpose",
    "application_type",
]

# Training-data cleaning thresholds from the Step 1/2 notebook.
DTI_IQR_LOWER = -9.82
DTI_IQR_UPPER = 45.87
ANNUAL_INCOME_UPPER = 170000.0
MODEL_REFERENCE_YEAR = 2018


US_STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia",
}


def _blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


def _float(payload, key, required=False):
    value = payload.get(key)
    if _blank(value):
        if required:
            raise ValueError(f"{key} is required.")
        return np.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be numeric.")


def _cat(payload, key, required=False, default="not_applicable"):
    value = payload.get(key)
    if _blank(value):
        if required:
            raise ValueError(f"{key} is required.")
        return default
    return str(value).strip()


def _ratio(a, b):
    if np.isnan(a) or np.isnan(b) or b <= 0:
        return np.nan
    return a / b


def build_loan_features(payload):
    # Important required raw inputs for a meaningful demo.
    annual_income = _float(payload, "annual_income", required=True)
    earliest_credit_line = _float(payload, "earliest_credit_line", required=True)
    loan_amount = _float(payload, "loan_amount", required=True)
    total_credit_limit = _float(payload, "total_credit_limit", required=True)

    raw = {}
    for field in NUMERIC_RAW_FIELDS:
        raw[field] = _float(payload, field, required=field in {
            "annual_income", "earliest_credit_line", "loan_amount", "total_credit_limit"
        })

    for field in CATEGORICAL_RAW_FIELDS:
        raw[field] = _cat(
            payload, field,
            required=field in {"state", "homeownership", "verified_income", "loan_purpose", "application_type"},
            default="not_applicable",
        )

    # Missing flags follow training cleaning logic.
    raw["is_joint_application"] = 1 if raw["application_type"].lower() == "joint" else 0
    raw["emp_length_missing"] = int(np.isnan(raw["emp_length"]))
    raw["dti_missing"] = int(np.isnan(raw["debt_to_income"]))
    raw["num_accounts_120d_missing"] = int(np.isnan(raw["num_accounts_120d_past_due"]))
    raw["months_since_last_delinq_missing"] = int(np.isnan(raw["months_since_last_delinq"]))
    raw["months_since_90d_late_missing"] = int(np.isnan(raw["months_since_90d_late"]))
    raw["months_since_last_credit_inquiry_missing"] = int(np.isnan(raw["months_since_last_credit_inquiry"]))

    # Training used -1 sentinel for missing recency values.
    for field in ["months_since_last_delinq", "months_since_90d_late", "months_since_last_credit_inquiry"]:
        if np.isnan(raw[field]):
            raw[field] = -1.0

    dti = raw["debt_to_income"]
    raw["annual_income_zero_flag"] = int(annual_income == 0)
    raw["dti_outlier_flag"] = int(
        (not np.isnan(dti)) and (dti < DTI_IQR_LOWER or dti > DTI_IQR_UPPER)
    )
    raw["annual_income_outlier_flag"] = int(annual_income > ANNUAL_INCOME_UPPER)
    raw["zero_credit_limit_flag"] = int(total_credit_limit == 0)

    # Engineered Step 4 predictors.
    raw["credit_utilization_ratio"] = _ratio(raw["total_credit_utilized"], total_credit_limit)
    raw["loan_to_income_ratio"] = _ratio(loan_amount, annual_income)
    raw["open_credit_ratio"] = _ratio(raw["open_credit_lines"], raw["total_credit_lines"])
    raw["cc_carrying_balance_ratio"] = _ratio(raw["num_cc_carrying_balance"], raw["num_open_cc_accounts"])
    raw["active_debit_ratio"] = _ratio(raw["num_active_debit_accounts"], raw["open_credit_lines"])
    raw["inquiries_per_credit_line"] = _ratio(raw["inquiries_last_12m"], raw["total_credit_lines"])
    raw["credit_age_years"] = max(MODEL_REFERENCE_YEAR - earliest_credit_line, 0)

    raw["delinquency_history_flag"] = int((raw["delinq_2y"] if not np.isnan(raw["delinq_2y"]) else 0) > 0)
    raw["collection_history_flag"] = int(
        (raw["num_collections_last_12m"] if not np.isnan(raw["num_collections_last_12m"]) else 0) > 0
        or (raw["total_collection_amount_ever"] if not np.isnan(raw["total_collection_amount_ever"]) else 0) > 0
    )
    raw["bankruptcy_or_lien_flag"] = int(
        (raw["public_record_bankrupt"] if not np.isnan(raw["public_record_bankrupt"]) else 0) > 0
        or (raw["tax_liens"] if not np.isnan(raw["tax_liens"]) else 0) > 0
    )
    raw["failed_payment_history_flag"] = int(
        (raw["num_historical_failed_to_pay"] if not np.isnan(raw["num_historical_failed_to_pay"]) else 0) > 0
    )
    raw["high_utilization_flag"] = int(
        (not np.isnan(raw["credit_utilization_ratio"])) and raw["credit_utilization_ratio"] > .80
    )
    raw["high_dti_flag"] = int((not np.isnan(dti)) and dti > 35)
    recency = raw["months_since_last_credit_inquiry"]
    raw["recent_credit_inquiry_flag"] = int(0 <= recency <= 3)

    # Raw num_accounts_120d_past_due is excluded from the model; keep only its missing flag.
    raw.pop("num_accounts_120d_past_due", None)

    return raw


def loan_form_groups():
    return [
        ("Applicant", [
            "emp_length", "state", "homeownership", "annual_income", "verified_income",
            "annual_income_joint", "verification_income_joint", "application_type"
        ]),
        ("Debt & Loan", [
            "debt_to_income", "debt_to_income_joint", "loan_amount", "term", "loan_purpose"
        ]),
        ("Credit History", [
            "delinq_2y", "months_since_last_delinq", "earliest_credit_line",
            "inquiries_last_12m", "months_since_90d_late", "months_since_last_credit_inquiry",
            "num_historical_failed_to_pay", "num_collections_last_12m",
            "total_collection_amount_ever", "tax_liens", "public_record_bankrupt"
        ]),
        ("Credit Accounts", [
            "total_credit_lines", "open_credit_lines", "total_credit_limit",
            "total_credit_utilized", "current_accounts_delinq", "current_installment_accounts",
            "accounts_opened_24m", "num_satisfactory_accounts",
            "num_accounts_120d_past_due", "num_accounts_30d_past_due",
            "num_active_debit_accounts", "total_debit_limit", "num_total_cc_accounts",
            "num_open_cc_accounts", "num_cc_carrying_balance", "num_mort_accounts",
            "account_never_delinq_percent"
        ]),
    ]
