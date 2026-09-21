"""End-to-end FinanceAI web smoke test.

Run this inside the FinanceAI virtual environment after installing requirements:
    python web_smoke_test.py

It uses a temporary SQLite database and does not touch your normal user database.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _csrf(client):
    with client.session_transaction() as sess:
        token = sess.get("_csrf_token")
    if not token:
        raise AssertionError("CSRF token was not created by the rendered page.")
    return token


def expect(response, status=200, contains=None):
    if response.status_code != status:
        raise AssertionError(f"Expected HTTP {status}, got {response.status_code} for {response.request.path}")
    if contains is not None:
        needle = contains.encode("utf-8") if isinstance(contains, str) else contains
        if needle not in response.data:
            raise AssertionError(f"Expected {contains!r} in {response.request.path}")


def main():
    with tempfile.TemporaryDirectory(prefix="financeai_webtest_") as td:
        os.environ["DB_BACKEND"] = "sqlite"
        os.environ["SQLITE_PATH"] = str(Path(td) / "web-smoke.db")
        os.environ["FLASK_DEBUG"] = "0"
        os.environ["SECRET_KEY"] = "financeai-web-smoke-test-secret"
        # Import only after the temporary environment is configured.
        from app import create_app

        app = create_app(testing=True)
        client = app.test_client()

        expect(client.get("/"), contains="FinanceAI")
        expect(client.get("/login"), contains="Login to FinanceAI")
        expect(client.get("/register"), contains="Create")

        # A guest must NEVER receive the Dashboard HTML directly.
        guest_dashboard = client.get("/dashboard", follow_redirects=False)
        if guest_dashboard.status_code not in (301, 302, 303, 307, 308):
            raise AssertionError(f"Guest /dashboard should redirect to login, got {guest_dashboard.status_code}")
        if "/login" not in (guest_dashboard.headers.get("Location") or ""):
            raise AssertionError("Guest /dashboard did not redirect to /login")

        # Public auth pages must not accidentally render protected Dashboard content.
        login_html = client.get("/login")
        if b"FINANCEAI 2.0 DASHBOARD" in login_html.data:
            raise AssertionError("Login page incorrectly contains Dashboard HTML")

        token = _csrf(client)

        response = client.post(
            "/register",
            data={
                "_csrf_token": token,
                "full_name": "FinanceAI Test User",
                "email": "web-smoke@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            },
            follow_redirects=True,
        )
        expect(response, contains="Dashboard")
        token = _csrf(client)

        # Budget page must render with an empty snapshot and with actual budget items.
        expect(client.get("/budget"), contains="Budget")
        response = client.post(
            "/budget",
            data={"_csrf_token": token, "category": "Groceries", "monthly_limit": "7000"},
            follow_redirects=True,
        )
        expect(response, contains="Groceries")

        # Spending Insights previously had the same dict.items collision as Budget.
        expect(client.get("/spending-insights"), contains="Behavior & Anomalies")

        # Loan form should display real state names while submitting model-compatible codes.
        loan_form = client.get("/loan-risk")
        expect(loan_form, contains="New Jersey (NJ)")
        expect(loan_form, contains="California (CA)")

        token = _csrf(client)
        loan_sample = json.loads((ROOT / "samples" / "loan_risk_sample.json").read_text(encoding="utf-8"))
        loan_sample["_csrf_token"] = token
        loan_result = client.post("/loan-risk", data=loan_sample)
        expect(loan_result, contains="Loan Risk Signal")

        # Readable history list and detail table.
        history = client.get("/history")
        expect(history, contains="Loan Risk Research Analysis")
        expect(history, contains="What It Means")

        detail = client.get("/history/1")
        expect(detail, contains="New Jersey (NJ)")
        expect(detail, contains="Information Used")
        expect(detail, contains="Analysis Result")

        pdf = client.get("/history/1/report.pdf")
        expect(pdf)
        if not pdf.data.startswith(b"%PDF"):
            raise AssertionError("PDF report endpoint did not return a PDF file.")

        # Version endpoint must identify the clean FinanceAI 2.0 build without exposing local paths.
        version = client.get("/version")
        expect(version)
        version_json = version.get_json()
        if version_json.get("version") != "2.0.0":
            raise AssertionError("Unexpected FinanceAI version")
        if version_json.get("assistant") != "Local TF-IDF RAG":
            raise AssertionError("Unexpected assistant mode")
        if "project_root" in version_json:
            raise AssertionError("Version endpoint must not expose the local filesystem path")

        # Core authenticated pages.
        for path in (
            "/dashboard", "/transactions", "/goals", "/forecast", "/net-worth",
            "/schemes", "/model-lab", "/assistant", "/profile",
        ):
            expect(client.get(path))

        print("FinanceAI web smoke tests passed.")
        print("Checked authentication, Budget, Spending Insights, Loan Risk full state names,")
        print("readable History tables, PDF report generation, Local RAG assistant, and core authenticated pages.")


if __name__ == "__main__":
    main()
