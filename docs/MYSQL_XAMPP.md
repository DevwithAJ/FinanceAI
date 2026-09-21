# XAMPP / MySQL Setup

1. Start **Apache** and **MySQL** in XAMPP.
2. Open phpMyAdmin.
3. Run:

```sql
CREATE DATABASE financeai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. Copy `.env.example` to `.env`.
5. Set:

```env
DB_BACKEND=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=financeai
```

6. Run:

```powershell
python init_db.py
python app.py
```

FinanceAI will automatically create the required tables.
