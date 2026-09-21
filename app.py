import csv
import io
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

from flask import (
    Flask, Response, abort, flash, jsonify, redirect, render_template,
    request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config import Config
from database import Database
from services.assistant import respond as assistant_respond
from services.financial_health import calculate_financial_health, validate_personal_finance
from services.loan_feature_builder import loan_form_groups
from services.model_service import ModelService
from services.recommendation_engine import generate_recommendations
from services.security import (
    clear_login_failures, csrf_token, login_rate_limited, login_required,
    record_login_failure, validate_csrf, validate_registration
)
from services.system_status import build_status
from services.finance_features import (
    INCOME_CATEGORIES, EXPENSE_CATEGORIES, PAYMENT_METHODS, month_range, budget_plan,
    budget_snapshot, forecast_finances, detect_anomalies, spending_behavior, enrich_goals,
    government_schemes, generate_demo_transactions
)
from services.rag_service import LocalRAG
from services.planning_tools import smart_category, what_if, emergency_plan
from services.presentation import present_history_row, present_analysis_detail, present_model_result


ROOT = Path(__file__).resolve().parent
APP_VERSION = "2.0.0"


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["TESTING"] = testing
    app.config["APP_VERSION"] = APP_VERSION
    app.permanent_session_lifetime = timedelta(
        minutes=Config.PERMANENT_SESSION_LIFETIME_MINUTES
    )

    db = Database(Config)
    db.init_schema(ROOT)
    models = ModelService(ROOT)
    rag = LocalRAG(ROOT)

    @app.after_request
    def prevent_stale_dynamic_pages(response):
        # FinanceAI pages contain session-dependent navigation and user data.
        # Prevent the browser from reusing a stale Dashboard/Login page from cache.
        if request.path.startswith("/static/"):
            return response
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["X-FinanceAI-Version"] = APP_VERSION
        return response

    @app.context_processor
    def inject_globals():
        user = None
        if session.get("user_id"):
            user = db.get_user_by_id(session["user_id"])
        return {
            "csrf_token": csrf_token,
            "current_user": user,
            "app_status": build_status(models),
            "app_version": APP_VERSION,
        }

    @app.before_request
    def csrf_protect():
        if request.method == "POST" and not request.is_json:
            token = request.form.get("_csrf_token")
            if not validate_csrf(token):
                abort(400, description="Invalid or expired form token. Refresh the page and try again.")

    def payload():
        return (request.get_json(silent=True) or {}) if request.is_json else request.form.to_dict()

    def safe_next_url(target):
        """Allow only same-site relative redirects after login."""
        if not target or not isinstance(target, str):
            return None
        try:
            parts = urlsplit(target)
        except ValueError:
            return None
        if parts.scheme or parts.netloc or not target.startswith("/") or target.startswith("//"):
            return None
        return target

    def save_if_logged_in(module, input_data, result, score=None, label=None):
        if session.get("user_id"):
            return db.save_analysis(
                session["user_id"], module, input_data, result, score=score, label=label
            )
        return None

    def build_analysis_pdf(row, user):
        """Generate a readable, generic PDF report for any saved analysis."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=f"FinanceAI Analysis #{row['id']}",
            author="FinanceAI Team",
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="FinanceTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=colors.HexColor("#0B6E75"),
            alignment=TA_CENTER,
            spaceAfter=8,
        ))
        styles.add(ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#12344D"),
            spaceBefore=10,
            spaceAfter=7,
        ))
        styles.add(ParagraphStyle(
            name="SmallMuted",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#607484"),
        ))

        detail = present_analysis_detail(row)

        def display_value(value):
            if value is None:
                return "—"
            return str(value)

        def data_table(rows):
            safe_rows = [[Paragraph(f"<b>{escape(str(k))}</b>", styles["BodyText"]), Paragraph(escape(str(v).replace("₹", "INR ")), styles["BodyText"])] for k, v in rows]
            if not safe_rows:
                safe_rows = [["—", "No data available"]]
            table = Table(safe_rows, colWidths=[58 * mm, 102 * mm], repeatRows=0)
            table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF7F6")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#203746")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D8E4E8")),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            return table

        module_name = detail["title"]
        story = [
            Paragraph("FinanceAI", styles["FinanceTitle"]),
            Paragraph("Intelligent Personal Finance & Risk Analysis System", styles["SmallMuted"]),
            Spacer(1, 8),
            Paragraph(f"{module_name} Report", styles["Heading1"]),
        ]

        summary_rows = [
            ["Report ID", row.get("id")],
            ["User", user.get("full_name") if user else "FinanceAI User"],
            ["Analysis", module_name],
            ["Result", detail["result_display"]],
            ["Score", detail["score_display"]],
            ["What it means", detail["meaning"]],
            ["Created", detail["date_display"]],
        ]
        input_rows = [[r["label"], r["value"]] for r in detail["input_rows"]]
        result_rows = [[r["label"], r["value"]] for r in detail["result_rows"]]
        insight_rows = [[i["factor"], f"{i['value']} — {i['meaning']}"] for i in detail.get("insights", [])]
        recommendation_rows = [[f"Step {idx}", text] for idx, text in enumerate(detail.get("recommendations", []), 1)]
        story.extend([
            Paragraph("Summary", styles["SectionTitle"]),
            data_table(summary_rows),
        ])
        if insight_rows:
            story.extend([Paragraph("Profile Observations", styles["SectionTitle"]), data_table(insight_rows)])
        if recommendation_rows:
            story.extend([Paragraph("Recommended Next Steps", styles["SectionTitle"]), data_table(recommendation_rows)])
        story.extend([
            Paragraph("Input Data", styles["SectionTitle"]),
            data_table(input_rows),
            Paragraph("Analysis Output", styles["SectionTitle"]),
            data_table(result_rows),
            Spacer(1, 12),
            Paragraph(
                "Responsible-use notice: FinanceAI is an educational analytics project. "
                "Personal-finance guidance is not professional financial advice. Credit Stress "
                "and Loan Risk outputs are experimental research/demo signals and must not be "
                "used to approve, reject, price, or limit financial products.",
                styles["SmallMuted"],
            ),
        ])

        doc.build(story)
        buffer.seek(0)
        return buffer

    # ---------------- Public ----------------
    @app.get("/")
    def home():
        return render_template("home.html")

    @app.get("/about")
    def about():
        return render_template("about.html")
    @app.get("/privacy")
    def privacy():
       return render_template("privacy.html")

    @app.get("/terms")
    def terms():
        return render_template("terms.html")


    @app.get("/healthz")
    def healthz():
        return jsonify({"ok": True, "service": "FinanceAI", "version": APP_VERSION})

    @app.get("/version")
    def version():
        return jsonify({
            "service": "FinanceAI",
            "version": APP_VERSION,
            "assistant": "Local TF-IDF RAG",
        })


    # ---------------- Auth ----------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if session.get("user_id"):
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")

            errors = validate_registration(full_name, email, password, confirm)
            if db.get_user_by_email(email):
                errors.append("An account with this email already exists.")

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template("auth/register.html", form=request.form), 400

            password_hash = generate_password_hash(
                password, method="pbkdf2:sha256:600000", salt_length=16
            )
            user_id = db.create_user(full_name, email, password_hash)
            session.clear()
            session["user_id"] = user_id
            session.permanent = True
            flash("Account created successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("auth/register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if session.get("user_id"):
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            if login_rate_limited():
                flash("Too many failed attempts. Try again after 15 minutes.", "danger")
                return render_template("auth/login.html"), 429

            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = db.get_user_by_email(email)

            if not user or not check_password_hash(user["password_hash"], password):
                record_login_failure()
                flash("Invalid email or password.", "danger")
                return render_template("auth/login.html"), 401

            clear_login_failures()
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = True
            db.update_last_login(user["id"])
            flash("Welcome back.", "success")
            next_url = safe_next_url(request.args.get("next"))
            return redirect(next_url or url_for("dashboard"))

        return render_template("auth/login.html")

    @app.post("/logout")
    @login_required
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("home"))

    # ---------------- User ----------------
    @app.get("/dashboard")
    @login_required
    def dashboard():
        uid = session["user_id"]
        stats = db.dashboard_stats(uid)
        recent = db.list_analyses(uid, limit=6)
        start, end, month = month_range()
        month_totals = db.transaction_totals(uid, start, end)
        category_rows = db.expense_by_category(uid, start, end)
        net_worth = db.net_worth_summary(uid)
        active_goals = enrich_goals(db.list_goals(uid, include_completed=False))
        transactions = db.list_transactions(uid, limit=400)
        forecast = forecast_finances(transactions)
        anomalies = detect_anomalies(transactions)
        return render_template(
            "dashboard.html", stats=stats, recent=recent, month=month, month_totals=month_totals,
            categories=category_rows[:5], net_worth=net_worth, active_goals=active_goals[:4],
            forecast=forecast, anomalies=anomalies,
        )

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        user = db.get_user_by_email(db.get_user_by_id(session["user_id"])["email"])
        if request.method == "POST":
            old_password = request.form.get("old_password", "")
            new_password = request.form.get("new_password", "")
            confirm = request.form.get("confirm_password", "")

            if not check_password_hash(user["password_hash"], old_password):
                flash("Current password is incorrect.", "danger")
            elif len(new_password) < 8:
                flash("New password must be at least 8 characters.", "danger")
            elif new_password != confirm:
                flash("New passwords do not match.", "danger")
            else:
                db.update_password(
                    session["user_id"],
                    generate_password_hash(new_password, method="pbkdf2:sha256:600000", salt_length=16),
                )
                flash("Password updated.", "success")
                return redirect(url_for("profile"))

        return render_template("profile.html", user=db.get_user_by_id(session["user_id"]))

    # ---------------- Personal Finance ----------------
    @app.route("/personal-finance", methods=["GET", "POST"])
    @login_required
    def personal_finance():
        if request.method == "POST":
            data = request.form.to_dict()
            data.pop("_csrf_token", None)
            errors = validate_personal_finance(data)
            if errors:
                for e in errors:
                    flash(e.replace("_", " "), "danger")
                return render_template("modules/personal_finance.html", form=request.form), 400

            health = calculate_financial_health(data)
            recommendations = generate_recommendations(data, health)
            result = {"health": health, "recommendations": recommendations}
            analysis_id = db.save_analysis(
                session["user_id"],
                "personal_finance",
                data,
                result,
                score=health["financial_health_score"],
                label=health["financial_health_level"],
            )
            return render_template(
                "modules/personal_finance_result.html",
                health=health,
                recommendations=recommendations,
                analysis_id=analysis_id,
            )

        return render_template("modules/personal_finance.html")

    # ---------------- Credit Stress ----------------
    @app.route("/credit-stress", methods=["GET", "POST"])
    @login_required
    def credit_stress():
        schema = models.credit_schema()

        if request.method == "POST":
            data = request.form.to_dict()
            data.pop("_csrf_token", None)
            result = models.predict_credit_stress(data)
            if not result.get("ok"):
                flash("Please complete all fields with valid values.", "danger")
                return render_template("modules/credit_stress.html", schema=schema, form=request.form), 400

            analysis_id = db.save_analysis(
                session["user_id"],
                "credit_card",
                data,
                result,
                score=result["score"],
                label=result["label"],
            )
            return render_template(
                "modules/model_result.html",
                view=present_model_result("credit_card", data, result),
                analysis_id=analysis_id,
                module_name="credit_card",
            )

        return render_template("modules/credit_stress.html", schema=schema)




    # ---------------- Loan Risk ----------------
    @app.route("/loan-risk", methods=["GET", "POST"])
    @login_required
    def loan_risk():
        schema = models.loan_schema()
        sample = None
        sample_file = ROOT / "samples" / "loan_risk_sample.json"
        if sample_file.exists():
            sample = json.loads(sample_file.read_text(encoding="utf-8"))

        if request.method == "POST":
            data = request.form.to_dict()
            data.pop("_csrf_token", None)
            result = models.predict_loan_risk(data)
            if not result.get("ok"):
                flash(result.get("detail", "Loan input is incomplete or invalid."), "danger")
                return render_template(
                    "modules/loan_risk.html",
                    schema=schema,
                    form=request.form,
                    sample=sample,
                ), 400

            analysis_id = db.save_analysis(
                session["user_id"],
                "loan_risk",
                data,
                result,
                score=result["risk_score"],
                label=result["label"],
            )
            return render_template(
                "modules/model_result.html",
                view=present_model_result("loan_risk", data, result),
                analysis_id=analysis_id,
                module_name="loan_risk",
            )

        return render_template("modules/loan_risk.html", schema=schema, sample=sample)

    

    # ---------------- Transactions ----------------
    @app.route("/transactions", methods=["GET", "POST"])
    @login_required
    def transactions():
        uid = session["user_id"]
        if request.method == "POST":
            typ = request.form.get("transaction_type", "").strip().lower()
            category = request.form.get("category", "").strip()
            description = request.form.get("description", "").strip()
            payment = request.form.get("payment_method", "").strip()
            tx_date = request.form.get("transaction_date", "").strip()
            try:
                amount = float(request.form.get("amount", "0"))
                datetime.strptime(tx_date, "%Y-%m-%d")
            except (TypeError, ValueError):
                flash("Enter a valid amount and date.", "danger")
                return redirect(url_for("transactions"))
            allowed = INCOME_CATEGORIES if typ == "income" else EXPENSE_CATEGORIES if typ == "expense" else []
            if amount <= 0 or not category or category not in allowed:
                flash("Transaction details are invalid.", "danger")
                return redirect(url_for("transactions"))
            db.add_transaction(uid, typ, amount, category, description, tx_date, payment, request.form.get("is_recurring") == "1")
            flash("Transaction added.", "success")
            return redirect(url_for("transactions"))

        rows = db.list_transactions(uid, limit=250)
        start, end, month = month_range()
        totals = db.transaction_totals(uid, start, end)
        categories = db.expense_by_category(uid, start, end)
        return render_template("finance/transactions.html", rows=rows, totals=totals, month=month,
                               categories=categories, income_categories=INCOME_CATEGORIES,
                               expense_categories=EXPENSE_CATEGORIES, payment_methods=PAYMENT_METHODS,
                               today=date.today().isoformat())

    @app.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
    @login_required
    def transaction_edit(transaction_id):
        uid = session["user_id"]
        row = db.get_transaction(uid, transaction_id)
        if not row:
            abort(404)
        if request.method == "POST":
            typ = request.form.get("transaction_type", "").strip().lower()
            category = request.form.get("category", "").strip()
            tx_date = request.form.get("transaction_date", "").strip()
            try:
                amount = float(request.form.get("amount", "0"))
                datetime.strptime(tx_date, "%Y-%m-%d")
            except (TypeError, ValueError):
                amount = -1
            allowed = INCOME_CATEGORIES if typ == "income" else EXPENSE_CATEGORIES if typ == "expense" else []
            if amount <= 0 or category not in allowed:
                flash("Transaction details are invalid.", "danger")
            else:
                db.update_transaction(uid, transaction_id, typ, amount, category,
                                      request.form.get("description", "").strip(), tx_date,
                                      request.form.get("payment_method", "").strip(),
                                      request.form.get("is_recurring") == "1")
                flash("Transaction updated.", "success")
                return redirect(url_for("transactions"))
        return render_template("finance/transaction_edit.html", row=row,
                               income_categories=INCOME_CATEGORIES, expense_categories=EXPENSE_CATEGORIES,
                               payment_methods=PAYMENT_METHODS)

    @app.post("/transactions/<int:transaction_id>/delete")
    @login_required
    def transaction_delete(transaction_id):
        db.delete_transaction(session["user_id"], transaction_id)
        flash("Transaction deleted.", "info")
        return redirect(url_for("transactions"))

    @app.post("/transactions/demo")
    @login_required
    def transactions_demo():
        uid = session["user_id"]
        existing = db.list_transactions(uid, limit=1)
        if existing and request.form.get("force") != "1":
            flash("Demo data was not added because your ledger already has transactions.", "warning")
            return redirect(url_for("transactions"))
        for row in generate_demo_transactions():
            db.add_transaction(uid, **row)
        flash("Six months of demo transactions added.", "success")
        return redirect(url_for("transactions"))

    @app.get("/transactions/export.csv")
    @login_required
    def transactions_export():
        rows = db.list_transactions(session["user_id"], limit=1000)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["date", "type", "category", "amount", "description", "payment_method", "recurring"])
        for r in reversed(rows):
            writer.writerow([r.get("transaction_date"), r.get("transaction_type"), r.get("category"),
                             r.get("amount"), r.get("description"), r.get("payment_method"), r.get("is_recurring")])
        return Response(buffer.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=financeai_transactions.csv"})

    @app.post("/transactions/import.csv")
    @login_required
    def transactions_import():
        file = request.files.get("file")
        if not file or not file.filename.lower().endswith(".csv"):
            flash("Choose a CSV file.", "danger")
            return redirect(url_for("transactions"))
        try:
            text = file.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            count = 0
            for row in reader:
                desc = (row.get("description") or row.get("narration") or row.get("merchant") or row.get("remarks") or "").strip()
                debit = row.get("debit") or row.get("withdrawal") or row.get("debit_amount")
                credit = row.get("credit") or row.get("deposit") or row.get("credit_amount")
                typ = (row.get("type") or row.get("transaction_type") or ("expense" if debit else "income" if credit else "")).strip().lower()
                raw_amount = row.get("amount") or debit or credit or 0
                amount = abs(float(str(raw_amount).replace(",", "") or 0))
                tx_date = (row.get("date") or row.get("transaction_date") or row.get("txn_date") or "").strip()
                category = (row.get("category") or "").strip() or (smart_category(desc) if typ == "expense" else "Other Income")
                if typ not in {"income", "expense"} or amount <= 0:
                    continue
                datetime.strptime(tx_date, "%Y-%m-%d")
                payment = (row.get("payment_method") or ("UPI" if "upi" in desc.lower() else "Bank Transfer")).strip()
                db.add_transaction(session["user_id"], typ, amount, category,
                                   desc, tx_date, payment,
                                   str(row.get("recurring", "")).lower() in {"1", "true", "yes"})
                count += 1
            flash(f"Imported {count} transaction(s).", "success")
        except Exception as exc:
            flash(f"CSV import failed: {exc}", "danger")
        return redirect(url_for("transactions"))

    # ---------------- Budget planner ----------------
    @app.route("/budget", methods=["GET", "POST"])
    @login_required
    def budget():
        uid = session["user_id"]
        selected_month = request.values.get("month") or date.today().strftime("%Y-%m")
        try:
            start, end, selected_month = month_range(selected_month)
        except ValueError:
            start, end, selected_month = month_range()
        if request.method == "POST":
            category = request.form.get("category", "").strip()
            try:
                limit = float(request.form.get("monthly_limit", "0"))
            except ValueError:
                limit = -1
            if not category or limit < 0:
                flash("Enter a valid category and monthly budget.", "danger")
            else:
                db.upsert_budget(uid, category, limit, selected_month)
                flash("Budget saved.", "success")
            return redirect(url_for("budget", month=selected_month))
        totals = db.transaction_totals(uid, start, end)
        categories = db.expense_by_category(uid, start, end)
        budgets = db.list_budgets(uid, selected_month)
        snapshot = budget_snapshot(totals, categories, budgets)
        return render_template("finance/budget.html", month=selected_month, totals=totals, snapshot=snapshot,
                               plan=budget_plan(totals["income"]), expense_categories=EXPENSE_CATEGORIES)

    @app.post("/budget/<int:budget_id>/delete")
    @login_required
    def budget_delete(budget_id):
        month = request.form.get("month") or date.today().strftime("%Y-%m")
        db.delete_budget(session["user_id"], budget_id)
        flash("Budget removed.", "info")
        return redirect(url_for("budget", month=month))

    # ---------------- Goals ----------------
    @app.route("/goals", methods=["GET", "POST"])
    @login_required
    def goals():
        uid = session["user_id"]
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            target_date = request.form.get("target_date", "").strip() or None
            try:
                target = float(request.form.get("target_amount", "0"))
                current = float(request.form.get("current_amount", "0") or 0)
                if target_date: datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                target, current = -1, 0
            if not title or target <= 0 or current < 0:
                flash("Enter valid goal details.", "danger")
            else:
                db.add_goal(uid, title, target, current, target_date)
                flash("Goal created.", "success")
            return redirect(url_for("goals"))
        rows = enrich_goals(db.list_goals(uid))
        return render_template("finance/goals.html", goals=rows, today=date.today().isoformat())

    @app.post("/goals/<int:goal_id>/progress")
    @login_required
    def goal_progress(goal_id):
        try:
            amount = float(request.form.get("current_amount", "0"))
            db.update_goal_progress(session["user_id"], goal_id, amount)
            flash("Goal progress updated.", "success")
        except ValueError:
            flash("Enter a valid amount.", "danger")
        return redirect(url_for("goals"))

    @app.post("/goals/<int:goal_id>/delete")
    @login_required
    def goal_delete(goal_id):
        db.delete_goal(session["user_id"], goal_id)
        flash("Goal deleted.", "info")
        return redirect(url_for("goals"))

    # ---------------- Decision simulators ----------------
    @app.route("/what-if", methods=["GET", "POST"])
    @login_required
    def what_if_simulator():
        uid=session["user_id"]
        start,end,_=month_range()
        totals=db.transaction_totals(uid,start,end)
        result=None
        if request.method == "POST":
            try:
                result=what_if(request.form.get("income", totals.get("income",0)), request.form.get("expenses", totals.get("expense",0)),
                               request.form.get("income_change",0), request.form.get("expense_change",0),
                               request.form.get("discretionary_cut",0), request.form.get("emi_change",0))
            except ValueError: flash("Enter valid numbers.","danger")
        return render_template("finance/what_if.html", totals=totals, result=result)

    @app.route("/emergency-fund", methods=["GET", "POST"])
    @login_required
    def emergency_fund():
        uid=session["user_id"]
        start,end,_=month_range()
        totals=db.transaction_totals(uid,start,end)
        result=None
        if request.method == "POST":
            try:
                result=emergency_plan(request.form.get("monthly_expense",totals.get("expense",0)), request.form.get("current_fund",0),
                                      request.form.get("target_months",6), request.form.get("monthly_contribution",0))
            except ValueError: flash("Enter valid numbers.","danger")
        return render_template("finance/emergency_fund.html", totals=totals, result=result)

    # ---------------- Forecast + spending analytics ----------------
    @app.route("/forecast", methods=["GET", "POST"])
    @login_required
    def forecast():
        rows = db.list_transactions(session["user_id"], limit=1000)
        result = forecast_finances(rows)
        if request.method == "POST" and result.get("ok"):
            db.save_analysis(session["user_id"], "cashflow_forecast", {"transaction_count": len(rows)}, result,
                             score=result["horizons"][0]["savings_rate"], label=f"{result['method']} forecast")
            flash("Forecast snapshot saved to analysis history.", "success")
            return redirect(url_for("forecast"))
        return render_template("finance/forecast.html", result=result)

    @app.get("/spending-insights")
    @login_required
    def spending_insights():
        uid = session["user_id"]
        rows = db.list_transactions(uid, limit=1000)
        category_rows = db.expense_by_category(uid)
        anomaly = detect_anomalies(rows)
        behavior = spending_behavior(category_rows)
        return render_template("finance/spending_insights.html", anomaly=anomaly, behavior=behavior,
                               categories=category_rows)

    # ---------------- Net worth ----------------
    @app.route("/net-worth", methods=["GET", "POST"])
    @login_required
    def net_worth():
        uid = session["user_id"]
        if request.method == "POST":
            typ = request.form.get("item_type", "").strip()
            category = request.form.get("category", "").strip()
            name = request.form.get("name", "").strip()
            as_of = request.form.get("as_of_date", "").strip()
            try:
                amount = float(request.form.get("amount", "0"))
                datetime.strptime(as_of, "%Y-%m-%d")
            except ValueError:
                amount = -1
            if typ not in {"asset", "investment", "liability"} or not category or not name or amount < 0:
                flash("Enter valid net-worth item details.", "danger")
            else:
                db.add_net_worth_item(uid, typ, category, name, amount, as_of)
                flash("Net-worth item added.", "success")
            return redirect(url_for("net_worth"))
        items = db.list_net_worth_items(uid)
        summary = db.net_worth_summary(uid)
        return render_template("finance/net_worth.html", items=items, summary=summary, today=date.today().isoformat())

    @app.post("/net-worth/<int:item_id>/delete")
    @login_required
    def net_worth_delete(item_id):
        db.delete_net_worth_item(session["user_id"], item_id)
        flash("Item deleted.", "info")
        return redirect(url_for("net_worth"))

    # ---------------- Schemes + Model Lab ----------------
    @app.get("/schemes")
    @login_required
    def schemes():
        return render_template("finance/schemes.html", schemes=government_schemes())

    @app.get("/model-lab")
    @login_required
    def model_lab():
        uid = session["user_id"]
        rows = db.list_transactions(uid, limit=1000)
        category_rows = db.expense_by_category(uid)
        lab = {
            "credit": models.credit_schema(),
            "loan": models.loan_schema(),
            "forecast": forecast_finances(rows),
            "anomaly": detect_anomalies(rows),
            "behavior": spending_behavior(category_rows),
            "rag_chunks": len(rag.docs),
        }
        return render_template("finance/model_lab.html", lab=lab)

    # ---------------- History ----------------
    @app.get("/history")
    @login_required
    def history():
        raw_rows = db.list_analyses(session["user_id"], limit=200)
        rows = [present_history_row(row) for row in raw_rows]
        return render_template("history/list.html", rows=rows)

    @app.get("/history/export.csv")
    @login_required
    def history_export():
        rows = db.list_analyses(session["user_id"], limit=500)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Record ID", "Analysis", "Result", "Score", "Meaning", "Date"])
        for row in rows:
            display = present_history_row(row)
            writer.writerow([
                row.get("id"), display.get("title"), display.get("result_display") or "—",
                display.get("score_display"), display.get("meaning"), display.get("date_display")
            ])
        return Response(
            buffer.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=financeai_history.csv"},
        )

    @app.get("/history/<int:analysis_id>")
    @login_required
    def history_detail(analysis_id):
        row = db.get_analysis(session["user_id"], analysis_id)
        if not row:
            abort(404)
        detail = present_analysis_detail(row)
        return render_template("history/detail.html", row=row, detail=detail)

    @app.get("/history/<int:analysis_id>/report.pdf")
    @login_required
    def analysis_pdf(analysis_id):
        row = db.get_analysis(session["user_id"], analysis_id)
        if not row:
            abort(404)
        user = db.get_user_by_id(session["user_id"])
        pdf = build_analysis_pdf(row, user)
        filename = f"financeai_{row['module_name']}_{analysis_id}.pdf"
        return Response(
            pdf.getvalue(),
            mimetype="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.post("/history/<int:analysis_id>/delete")
    @login_required
    def history_delete(analysis_id):
        db.delete_analysis(session["user_id"], analysis_id)
        flash("Analysis deleted.", "info")
        return redirect(url_for("history"))
    # ---------------- Assistant ----------------
    @app.route("/assistant", methods=["GET", "POST"])
    @login_required
    def assistant():
        if request.method == "POST":
            message = request.form.get("message", "").strip()
            if not message:
                flash("Enter a question.", "warning")
            else:
                uid = session["user_id"]
                latest = db.latest_personal_finance_result(uid)
                start, end, _ = month_range()
                month_totals = db.transaction_totals(uid, start, end)
                category_rows = db.expense_by_category(uid, start, end)
                net = db.net_worth_summary(uid)
                active_goals = db.list_goals(uid, include_completed=False)

                health = (latest or {}).get("health", latest or {})
                recent_analyses = db.list_analyses(uid, limit=30)
                latest_credit = next((r for r in recent_analyses if r.get("module_name") == "credit_card"), None)
                latest_loan = next((r for r in recent_analyses if r.get("module_name") == "loan_risk"), None)

                context = {
                    "month": month_totals,
                    "health_score": health.get("financial_health_score") if isinstance(health, dict) else None,
                    "health_level": health.get("financial_health_level") if isinstance(health, dict) else None,
                    "net_worth": net.get("net_worth", 0),
                    "active_goals": len(active_goals),
                    "top_expense_categories": category_rows[:5],
                    "credit_stress": latest_credit,
                    "loan_risk": latest_loan,
                }
                rag_answer, rag_hits = rag.answer(message, context)
                rules_answer = assistant_respond(message, latest)
                answer = rules_answer + "\n\n" + rag_answer
                db.save_assistant_message(uid, message, answer)
                return redirect(url_for("assistant"))

        messages = db.list_assistant_messages(session["user_id"], limit=30)
        return render_template("assistant.html", messages=messages)

    @app.post("/assistant/clear")
    @login_required
    def assistant_clear():
        db.clear_assistant_messages(session["user_id"])
        flash("Chat cleared successfully.", "info")
        return redirect(url_for("assistant"))
    # ---------------- JSON API ----------------
    @app.get("/api/v1/status")
    def api_status():
        status = build_status(models)
        status["version"] = APP_VERSION
        return jsonify(status)

    @app.post("/api/v1/personal-finance")
    def api_personal_finance():
        data = payload()
        errors = validate_personal_finance(data)
        if errors:
            return jsonify({"ok": False, "errors": errors}), 400
        health = calculate_financial_health(data)
        recs = generate_recommendations(data, health)
        result = {"ok": True, "health": health, "recommendations": recs}
        save_if_logged_in(
            "personal_finance",
            data,
            result,
            score=health["financial_health_score"],
            label=health["financial_health_level"],
        )
        return jsonify(result)

    @app.get("/api/v1/credit-stress/schema")
    def api_credit_schema():
        return jsonify(models.credit_schema())

    @app.post("/api/v1/credit-stress")
    def api_credit_stress():
        data = payload()
        result = models.predict_credit_stress(data)
        if not result.get("ok"):
            return jsonify(result), 400
        save_if_logged_in("credit_card", data, result, score=result["score"], label=result["label"])
        return jsonify(result)

    @app.get("/api/v1/loan-risk/schema")
    def api_loan_schema():
        return jsonify(models.loan_schema())

    @app.post("/api/v1/loan-risk")
    def api_loan_risk():
        data = payload()
        result = models.predict_loan_risk(data)
        if not result.get("ok"):
            return jsonify(result), 400
        save_if_logged_in("loan_risk", data, result, score=result["risk_score"], label=result["label"])
        return jsonify(result)

    @app.get("/api/v1/history")
    @login_required
    def api_history():
        return jsonify({"ok": True, "items": db.list_analyses(session["user_id"], limit=200)})

    @app.get("/api/v1/transactions")
    @login_required
    def api_transactions():
        return jsonify({"ok": True, "items": db.list_transactions(session["user_id"], limit=500)})

    @app.get("/api/v1/forecast")
    @login_required
    def api_forecast():
        return jsonify({"ok": True, **forecast_finances(db.list_transactions(session["user_id"], limit=1000))})

    @app.get("/api/v1/spending-insights")
    @login_required
    def api_spending_insights():
        uid = session["user_id"]
        tx = db.list_transactions(uid, limit=1000)
        return jsonify({"ok": True, "anomalies": detect_anomalies(tx), "behavior": spending_behavior(db.expense_by_category(uid))})

    @app.get("/api/v1/net-worth")
    @login_required
    def api_net_worth():
        uid = session["user_id"]
        return jsonify({"ok": True, "summary": db.net_worth_summary(uid), "items": db.list_net_worth_items(uid)})

    # ---------------- Errors ----------------
    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "error": "bad_request", "detail": str(error)}), 400
        return render_template("errors/400.html", error=error), 400

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "error": "not_found"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "error": "internal_server_error"}), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(413)
    def too_large(error):
        return jsonify({"ok": False, "error": "payload_too_large"}), 413

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5050")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
