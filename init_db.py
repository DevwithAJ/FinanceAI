from pathlib import Path

from config import Config
from database import Database

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    db = Database(Config)
    db.init_schema(root)
    print(f"FinanceAI database initialized using backend: {Config.DB_BACKEND}")
