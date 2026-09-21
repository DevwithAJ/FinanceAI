#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
python - <<'PY'
from pathlib import Path
import secrets
p=Path('.env')
s=p.read_text(encoding='utf-8')
s=s.replace('SECRET_KEY=change-this-to-a-long-random-secret','SECRET_KEY='+secrets.token_urlsafe(48))
p.write_text(s,encoding='utf-8')
PY
python init_db.py
echo "FinanceAI 2.0 setup complete. Run ./run_linux.sh"
