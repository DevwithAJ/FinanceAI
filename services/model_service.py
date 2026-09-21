import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .loan_feature_builder import build_loan_features, loan_form_groups, US_STATE_NAMES
from .presentation import label_for


class ModelService:
    def __init__(self, project_root):
        self.root = Path(project_root)

        self.credit_pipeline = joblib.load(
            self.root / "models" / "credit_card" / "credit_card_model_candidate_pipeline.pkl"
        )
        self.loan_pipeline = joblib.load(
            self.root / "models" / "loan_risk" / "loan_risk_model_candidate_pipeline.pkl"
        )

        self.credit_threshold = self._threshold(
            self.root / "models" / "credit_card" / "credit_card_step7_threshold_config.json", .50
        )
        self.loan_threshold = self._threshold(
            self.root / "models" / "loan_risk" / "loan_risk_step7_threshold_config.json", .50
        )

        self.credit_metadata = self._json(
            self.root / "models" / "credit_card" / "credit_card_step6_model_metadata.json"
        )
        self.loan_metadata = self._json(
            self.root / "models" / "loan_risk" / "loan_risk_step6_model_metadata.json"
        )

        self.credit_features = list(self.credit_pipeline.named_steps["preprocessor"].feature_names_in_)
        self.loan_features = list(self.loan_pipeline.named_steps["preprocessor"].feature_names_in_)

    @staticmethod
    def _json(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def _threshold(self, path, default):
        return float(self._json(path).get("recommended_threshold", default))

    def credit_schema(self):
        pre = self.credit_pipeline.named_steps["preprocessor"]
        cat = pre.named_transformers_["cat"].named_steps["encoder"]
        cat_cols = pre.transformers_[1][2]
        options = {col: [str(v) for v in vals] for col, vals in zip(cat_cols, cat.categories_)}
        return {
            "features": self.credit_features,
            "options": options,
            "threshold": self.credit_threshold,
            "target": "financial_stress_flag",
            "warning": "Experimental financial-stress proxy; not default probability or a credit decision.",
        }

    def loan_schema(self):
        pre = self.loan_pipeline.named_steps["preprocessor"]
        cat = pre.named_transformers_["cat"].named_steps["encoder"]
        cat_cols = pre.transformers_[1][2]
        options = {col: [str(v) for v in vals] for col, vals in zip(cat_cols, cat.categories_)}
        return {
            "model_feature_count": len(self.loan_features),
            "model_features": self.loan_features,
            "categorical_options": options,
            "state_labels": {code: US_STATE_NAMES.get(code, code) for code in options.get("state", [])},
            "field_labels": {field: label_for(field) for _, fields in loan_form_groups() for field in fields},
            "form_groups": loan_form_groups(),
            "threshold": self.loan_threshold,
            "warning": "Experimental risk ranking only; never use as an autonomous lending decision.",
            "reference_year": 2018,
        }

    def predict_credit_stress(self, payload):
        missing = [f for f in self.credit_features if payload.get(f) in (None, "")]
        if missing:
            return {"ok": False, "error": "missing_fields", "missing_fields": missing}

        row = {}
        for f in self.credit_features:
            if f in {"Age", "Dependents", "Desired_Savings_Percentage"}:
                try:
                    row[f] = float(payload[f])
                except (TypeError, ValueError):
                    return {"ok": False, "error": "invalid_numeric", "field": f}
            else:
                row[f] = str(payload[f]).strip()

        frame = pd.DataFrame([row], columns=self.credit_features)
        p = float(self.credit_pipeline.predict_proba(frame)[:, 1][0])
        cls = int(p >= self.credit_threshold)
        return {
            "ok": True,
            "module": "credit_card",
            "score": round(p, 6),
            "threshold": round(self.credit_threshold, 6),
            "predicted_class": cls,
            "label": "Elevated Stress Proxy" if cls else "Lower Stress Proxy",
            "production_ready": False,
            "warning": "This is a financial-stress proxy, not actual credit default probability.",
        }

    def predict_loan_risk(self, payload):
        try:
            built = build_loan_features(payload)
        except ValueError as exc:
            return {"ok": False, "error": "invalid_input", "detail": str(exc)}

        # Ensure the exact model feature matrix.
        row = {}
        missing_internal = []
        for f in self.loan_features:
            if f not in built:
                missing_internal.append(f)
            else:
                row[f] = built[f]

        if missing_internal:
            return {
                "ok": False,
                "error": "feature_builder_incomplete",
                "missing_features": missing_internal,
            }

        frame = pd.DataFrame([row], columns=self.loan_features)
        p = float(self.loan_pipeline.predict_proba(frame)[:, 1][0])
        cls = int(p >= self.loan_threshold)

        return {
            "ok": True,
            "module": "loan_risk",
            "risk_score": round(p, 6),
            "threshold": round(self.loan_threshold, 6),
            "predicted_class": cls,
            "label": "Elevated Experimental Risk" if cls else "Lower Experimental Risk",
            "production_ready": False,
            "warning": "Experimental risk ranking only. Do not use for autonomous loan approval/rejection.",
            "reference_year": 2018,
        }
