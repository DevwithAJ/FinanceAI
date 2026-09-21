def build_status(model_service):
    return {
        "project": "FinanceAI",
        "version": "2.0.0",
        "modules": {
            "personal_finance": {
                "ready": True,
                "mode": "transparent health score + recommendations",
                "decision_use": "educational",
            },
            "credit_card": {
                "ready": True,
                "mode": "experimental stress-proxy classifier",
                "model": model_service.credit_metadata.get("champion_model", "Logistic Regression"),
                "threshold": model_service.credit_threshold,
                "decision_use": "not for credit approval/rejection",
            },
            "loan_risk": {
                "ready": True,
                "mode": "experimental risk-ranking classifier",
                "model": model_service.loan_metadata.get("champion_model", "Extra Trees"),
                "threshold": model_service.loan_threshold,
                "decision_use": "not for automated lending decisions",
            },
        },
    }
