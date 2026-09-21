import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "financeai-dev-change-this-secret-key")
    DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").strip().lower()
    _SQLITE_RAW = os.getenv("SQLITE_PATH", "instance/financeai.db")
    SQLITE_PATH = str(Path(_SQLITE_RAW) if Path(_SQLITE_RAW).is_absolute() else (BASE_DIR / _SQLITE_RAW).resolve())

    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "financeai")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
    PERMANENT_SESSION_LIFETIME_MINUTES = int(os.getenv("SESSION_MINUTES", "120"))

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    JSON_SORT_KEYS = False
