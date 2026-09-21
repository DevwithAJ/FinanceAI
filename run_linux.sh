#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ ! -x venv/bin/python ]; then
  echo "Virtual environment not found. Run ./setup_linux.sh first."
  exit 1
fi
source venv/bin/activate
export HOST="${HOST:-127.0.0.1}"
export PORT="${PORT:-5050}"
export FLASK_DEBUG="${FLASK_DEBUG:-0}"
python app.py
