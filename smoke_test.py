"""FinanceAI 2.0 service smoke test.

This test intentionally does not require Flask so core data/ML services can be
validated independently of the web server runtime.
"""
import json
import tempfile
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from database import Database
from services.finance_features import (
    budget_snapshot, detect_anomalies, enrich_goals, forecast_finances,
    generate_demo_transactions, month_range, spending_behavior,
)
from services.model_service import ModelService
from services.rag_service import LocalRAG

ROOT = Path(__file__).resolve().parent


def main():
    models = ModelService(ROOT)
    credit = models.predict_credit_stress(json.loads((ROOT / "samples/credit_stress_sample.json").read_text()))
    loan = models.predict_loan_risk(json.loads((ROOT / "samples/loan_risk_sample.json").read_text()))
    assert credit.get("ok") and loan.get("ok")

    with tempfile.TemporaryDirectory() as td:
        cfg = SimpleNamespace(
            DB_BACKEND="sqlite", SQLITE_PATH=str(Path(td) / "smoke.db"),
            MYSQL_HOST="", MYSQL_PORT=3306, MYSQL_USER="", MYSQL_PASSWORD="", MYSQL_DATABASE="",
        )
        db = Database(cfg)
        db.init_schema(ROOT)
        uid = db.create_user("FinanceAI Smoke User", "smoke@example.com", "test-hash")

        for row in generate_demo_transactions(months=6):
            db.add_transaction(uid, **row)
        transactions = db.list_transactions(uid, limit=1000)
        assert len(transactions) >= 50

        start, end, month = month_range()
        totals = db.transaction_totals(uid, start, end)
        categories = db.expense_by_category(uid, start, end)
        db.upsert_budget(uid, "Groceries", 7000, month)
        budget = budget_snapshot(totals, categories, db.list_budgets(uid, month))
        assert budget["items"]

        goal_id = db.add_goal(uid, "Emergency Fund", 100000, 25000, None)
        db.update_goal_progress(uid, goal_id, 30000)
        assert enrich_goals(db.list_goals(uid))[0]["progress"] == 30.0

        db.add_net_worth_item(uid, "asset", "Cash", "Savings Account", 80000, date.today().isoformat())
        db.add_net_worth_item(uid, "investment", "Mutual Fund", "Index Fund", 40000, date.today().isoformat())
        db.add_net_worth_item(uid, "liability", "Loan", "Education Loan", 35000, date.today().isoformat())
        net = db.net_worth_summary(uid)
        assert net["net_worth"] == 85000.0

        forecast = forecast_finances(transactions)
        anomalies = detect_anomalies(transactions)
        behavior = spending_behavior(db.expense_by_category(uid))
        assert forecast["ok"] and len(forecast["horizons"]) == 3
        assert anomalies["method"] in {"isolation-forest", "robust-threshold"}
        assert behavior["method"] in {"k-means", "share-bands"}

        rag = LocalRAG(ROOT)
        rag_answer, hits = rag.answer("How can I build an emergency fund?", {
            "month": totals, "net_worth": net["net_worth"], "active_goals": 1,
        })
        assert hits and "emergency" in rag_answer.lower()

    print("FinanceAI 2.0 smoke tests passed.")
    print("Credit:", credit["label"], "score", credit["score"])
    print("Loan:", loan["label"], "score", loan["risk_score"])
    print("Transactions:", len(transactions), "Forecast:", forecast["method"])
    print("Anomaly:", anomalies["method"], "Behavior:", behavior["method"])
    print("Local RAG chunks:", len(rag.docs))


if __name__ == "__main__":
    main()
