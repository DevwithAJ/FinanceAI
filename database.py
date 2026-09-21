import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, config):
        self.backend = config.DB_BACKEND
        self.sqlite_path = Path(config.SQLITE_PATH)
        self.mysql_settings = {
            "host": config.MYSQL_HOST,
            "port": config.MYSQL_PORT,
            "user": config.MYSQL_USER,
            "password": config.MYSQL_PASSWORD,
            "database": config.MYSQL_DATABASE,
        }

    @contextmanager
    def connection(self):
        if self.backend == "mysql":
            try:
                import pymysql
            except ImportError as exc:
                raise RuntimeError(
                    "PyMySQL is required for DB_BACKEND=mysql. Run pip install -r requirements.txt"
                ) from exc
            conn = pymysql.connect(
                **self.mysql_settings,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
        else:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row

        try:
            yield conn
        finally:
            conn.close()

    def _sql(self, query):
        return query.replace("?", "%s") if self.backend == "mysql" else query

    def execute(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(self._sql(query), params)
            result = None
            if fetchone:
                row = cur.fetchone()
                result = dict(row) if row is not None else None
            elif fetchall:
                rows = cur.fetchall()
                result = [dict(r) for r in rows]
            if commit:
                conn.commit()
            return result

    def insert(self, query, params=()):
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(self._sql(query), params)
            conn.commit()
            return int(cur.lastrowid)

    def init_schema(self, base_dir):
        base_dir = Path(base_dir)
        schema_file = (
            base_dir / "database" / "schema_mysql.sql"
            if self.backend == "mysql"
            else base_dir / "database" / "schema_sqlite.sql"
        )
        sql = schema_file.read_text(encoding="utf-8")

        with self.connection() as conn:
            if self.backend == "mysql":
                cur = conn.cursor()
                statements = [s.strip() for s in sql.split(";") if s.strip()]
                for statement in statements:
                    cur.execute(statement)
                conn.commit()
            else:
                conn.executescript(sql)
                conn.commit()

    # ---------------- Users ----------------
    def create_user(self, full_name, email, password_hash):
        return self.insert(
            """
            INSERT INTO users (full_name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (full_name, email, password_hash),
        )

    def get_user_by_email(self, email):
        return self.execute(
            "SELECT * FROM users WHERE email = ? LIMIT 1",
            (email,),
            fetchone=True,
        )

    def get_user_by_id(self, user_id):
        return self.execute(
            "SELECT id, full_name, email, created_at, last_login FROM users WHERE id = ? LIMIT 1",
            (user_id,),
            fetchone=True,
        )

    def update_last_login(self, user_id):
        self.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
            commit=True,
        )

    def update_password(self, user_id, password_hash):
        self.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id),
            commit=True,
        )

    # ---------------- Analysis history ----------------
    def save_analysis(self, user_id, module_name, input_data, result_data, score=None, label=None):
        return self.insert(
            """
            INSERT INTO analysis_runs
            (user_id, module_name, input_json, result_json, score, label)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                module_name,
                json.dumps(input_data, ensure_ascii=False, default=str),
                json.dumps(result_data, ensure_ascii=False, default=str),
                score,
                label,
            ),
        )

    def list_analyses(self, user_id, limit=100):
        limit = max(1, min(int(limit), 500))
        # LIMIT cannot reliably use bind syntax across all MySQL configs, so interpolate validated int.
        return self.execute(
            f"""
            SELECT id, module_name, score, label, created_at
            FROM analysis_runs
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT {limit}
            """,
            (user_id,),
            fetchall=True,
        )

    def get_analysis(self, user_id, analysis_id):
        row = self.execute(
            """
            SELECT * FROM analysis_runs
            WHERE id = ? AND user_id = ?
            LIMIT 1
            """,
            (analysis_id, user_id),
            fetchone=True,
        )
        if row:
            row["input_data"] = json.loads(row.pop("input_json"))
            row["result_data"] = json.loads(row.pop("result_json"))
        return row

    def delete_analysis(self, user_id, analysis_id):
        self.execute(
            "DELETE FROM analysis_runs WHERE id = ? AND user_id = ?",
            (analysis_id, user_id),
            commit=True,
        )

    def dashboard_stats(self, user_id):
        total = self.execute(
            "SELECT COUNT(*) AS n FROM analysis_runs WHERE user_id = ?",
            (user_id,),
            fetchone=True,
        )["n"]

        modules = self.execute(
            """
            SELECT module_name, COUNT(*) AS n
            FROM analysis_runs
            WHERE user_id = ?
            GROUP BY module_name
            """,
            (user_id,),
            fetchall=True,
        )

        latest_health = self.execute(
            """
            SELECT score, label, created_at
            FROM analysis_runs
            WHERE user_id = ? AND module_name = 'personal_finance'
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
            fetchone=True,
        )

        return {
            "total": int(total),
            "modules": {r["module_name"]: int(r["n"]) for r in modules},
            "latest_health": latest_health,
        }
    # ---------------- Assistant history ----------------
    def save_assistant_message(self, user_id, user_message, assistant_message):
        return self.insert(
            """
            INSERT INTO assistant_messages
            (user_id, user_message, assistant_message)
            VALUES (?, ?, ?)
            """,
            (user_id, user_message, assistant_message),
        )

    def list_assistant_messages(self, user_id, limit=30):
        limit = max(1, min(int(limit), 100))
        rows = self.execute(
            f"""
            SELECT id, user_message, assistant_message, created_at
            FROM assistant_messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT {limit}
            """,
            (user_id,),
            fetchall=True,
        )
        return list(reversed(rows))

    def clear_assistant_messages(self, user_id):
        self.execute(
            "DELETE FROM assistant_messages WHERE user_id = ?",
            (user_id,),
            commit=True,
        )

    def latest_personal_finance_result(self, user_id):
        row = self.execute(
            """
            SELECT result_json
            FROM analysis_runs
            WHERE user_id = ? AND module_name = 'personal_finance'
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
            fetchone=True,
        )
        if not row:
            return None
        return json.loads(row["result_json"])
    # ---------------- Transactions ----------------
    def add_transaction(self, user_id, transaction_type, amount, category, description, transaction_date, payment_method=None, is_recurring=False):
        return self.insert(
            """INSERT INTO transactions
               (user_id, transaction_type, amount, category, description, transaction_date, payment_method, is_recurring)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, transaction_type, float(amount), category, description or None, transaction_date, payment_method or None, int(bool(is_recurring))),
        )

    def list_transactions(self, user_id, limit=250, transaction_type=None, category=None, start_date=None, end_date=None):
        limit = max(1, min(int(limit), 1000))
        where = ["user_id = ?"]
        params = [user_id]
        if transaction_type:
            where.append("transaction_type = ?")
            params.append(transaction_type)
        if category:
            where.append("category = ?")
            params.append(category)
        if start_date:
            where.append("transaction_date >= ?")
            params.append(start_date)
        if end_date:
            where.append("transaction_date <= ?")
            params.append(end_date)
        return self.execute(
            f"""SELECT id, transaction_type, amount, category, description, transaction_date,
                       payment_method, is_recurring, created_at
                FROM transactions WHERE {' AND '.join(where)}
                ORDER BY transaction_date DESC, id DESC LIMIT {limit}""",
            tuple(params), fetchall=True,
        )

    def delete_transaction(self, user_id, transaction_id):
        self.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id), commit=True)

    def transaction_categories(self, user_id):
        rows = self.execute(
            "SELECT DISTINCT category FROM transactions WHERE user_id = ? ORDER BY category",
            (user_id,), fetchall=True,
        )
        return [r["category"] for r in rows]

    def transaction_totals(self, user_id, start_date=None, end_date=None):
        where = ["user_id = ?"]
        params = [user_id]
        if start_date:
            where.append("transaction_date >= ?")
            params.append(start_date)
        if end_date:
            where.append("transaction_date <= ?")
            params.append(end_date)
        rows = self.execute(
            f"""SELECT transaction_type, COALESCE(SUM(amount),0) AS total, COUNT(*) AS n
                FROM transactions WHERE {' AND '.join(where)} GROUP BY transaction_type""",
            tuple(params), fetchall=True,
        )
        out = {"income": 0.0, "expense": 0.0, "count": 0}
        for r in rows:
            out[r["transaction_type"]] = float(r["total"] or 0)
            out["count"] += int(r["n"] or 0)
        out["balance"] = out["income"] - out["expense"]
        out["savings_rate"] = round((out["balance"] / out["income"] * 100), 2) if out["income"] > 0 else 0.0
        return out

    def expense_by_category(self, user_id, start_date=None, end_date=None):
        where = ["user_id = ?", "transaction_type = 'expense'"]
        params = [user_id]
        if start_date:
            where.append("transaction_date >= ?")
            params.append(start_date)
        if end_date:
            where.append("transaction_date <= ?")
            params.append(end_date)
        rows = self.execute(
            f"""SELECT category, COALESCE(SUM(amount),0) AS total, COUNT(*) AS n
                FROM transactions WHERE {' AND '.join(where)}
                GROUP BY category ORDER BY total DESC""",
            tuple(params), fetchall=True,
        )
        return [{**r, "total": float(r["total"] or 0), "n": int(r["n"] or 0)} for r in rows]

    # ---------------- Budgets ----------------
    def upsert_budget(self, user_id, category, monthly_limit, budget_month):
        existing = self.execute(
            "SELECT id FROM budgets WHERE user_id = ? AND category = ? AND budget_month = ? LIMIT 1",
            (user_id, category, budget_month), fetchone=True,
        )
        if existing:
            self.execute(
                "UPDATE budgets SET monthly_limit = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
                (float(monthly_limit), existing["id"], user_id), commit=True,
            )
            return int(existing["id"])
        return self.insert(
            "INSERT INTO budgets (user_id, category, monthly_limit, budget_month) VALUES (?, ?, ?, ?)",
            (user_id, category, float(monthly_limit), budget_month),
        )

    def list_budgets(self, user_id, budget_month):
        rows = self.execute(
            "SELECT id, category, monthly_limit, budget_month, created_at, updated_at FROM budgets WHERE user_id = ? AND budget_month = ? ORDER BY category",
            (user_id, budget_month), fetchall=True,
        )
        for r in rows:
            r["monthly_limit"] = float(r["monthly_limit"])
        return rows

    def delete_budget(self, user_id, budget_id):
        self.execute("DELETE FROM budgets WHERE id = ? AND user_id = ?", (budget_id, user_id), commit=True)

    # ---------------- Goals ----------------
    def add_goal(self, user_id, title, target_amount, current_amount=0, target_date=None):
        return self.insert(
            "INSERT INTO goals (user_id, title, target_amount, current_amount, target_date) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, float(target_amount), float(current_amount or 0), target_date or None),
        )

    def list_goals(self, user_id, include_completed=True):
        query = "SELECT * FROM goals WHERE user_id = ?"
        params = [user_id]
        if not include_completed:
            query += " AND status = ?"
            params.append("active")
        query += " ORDER BY CASE WHEN status='active' THEN 0 ELSE 1 END, target_date, id DESC"
        rows = self.execute(query, tuple(params), fetchall=True)
        for r in rows:
            r["target_amount"] = float(r["target_amount"])
            r["current_amount"] = float(r["current_amount"])
        return rows

    def update_goal_progress(self, user_id, goal_id, current_amount):
        row = self.execute("SELECT target_amount FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id), fetchone=True)
        if not row:
            return False
        amount = max(0.0, float(current_amount))
        status = "completed" if amount >= float(row["target_amount"]) else "active"
        self.execute(
            "UPDATE goals SET current_amount = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
            (amount, status, goal_id, user_id), commit=True,
        )
        return True

    def delete_goal(self, user_id, goal_id):
        self.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id), commit=True)

    # ---------------- Net worth ----------------
    def add_net_worth_item(self, user_id, item_type, category, name, amount, as_of_date):
        return self.insert(
            "INSERT INTO net_worth_items (user_id, item_type, category, name, amount, as_of_date) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, item_type, category, name, float(amount), as_of_date),
        )

    def list_net_worth_items(self, user_id):
        rows = self.execute(
            "SELECT id, item_type, category, name, amount, as_of_date, created_at FROM net_worth_items WHERE user_id = ? ORDER BY item_type, amount DESC",
            (user_id,), fetchall=True,
        )
        for r in rows:
            r["amount"] = float(r["amount"])
        return rows

    def delete_net_worth_item(self, user_id, item_id):
        self.execute("DELETE FROM net_worth_items WHERE id = ? AND user_id = ?", (item_id, user_id), commit=True)

    def net_worth_summary(self, user_id):
        rows = self.execute(
            "SELECT item_type, COALESCE(SUM(amount),0) AS total FROM net_worth_items WHERE user_id = ? GROUP BY item_type",
            (user_id,), fetchall=True,
        )
        result = {"asset": 0.0, "investment": 0.0, "liability": 0.0}
        for r in rows:
            result[r["item_type"]] = float(r["total"] or 0)
        result["total_assets"] = result["asset"] + result["investment"]
        result["net_worth"] = result["total_assets"] - result["liability"]
        return result

    def get_transaction(self, user_id, transaction_id):
        return self.execute(
            "SELECT id, transaction_type, amount, category, description, transaction_date, payment_method, is_recurring FROM transactions WHERE id = ? AND user_id = ? LIMIT 1",
            (transaction_id, user_id), fetchone=True,
        )

    def update_transaction(self, user_id, transaction_id, transaction_type, amount, category, description, transaction_date, payment_method=None, is_recurring=False):
        self.execute(
            """UPDATE transactions SET transaction_type = ?, amount = ?, category = ?, description = ?,
               transaction_date = ?, payment_method = ?, is_recurring = ? WHERE id = ? AND user_id = ?""",
            (transaction_type, float(amount), category, description or None, transaction_date,
             payment_method or None, int(bool(is_recurring)), transaction_id, user_id), commit=True,
        )
