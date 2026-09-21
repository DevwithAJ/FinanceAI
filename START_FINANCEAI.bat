@echo off
setlocal
cd /d %~dp0

echo =====================================================
echo FinanceAI 2.0 - Start
echo =====================================================

if not exist venv\Scripts\python.exe (
  echo [ERROR] Setup not found. Run setup_windows.bat first.
  pause
  exit /b 1
)

call venv\Scripts\activate.bat
set HOST=127.0.0.1
set PORT=5050
set FLASK_DEBUG=0

echo FinanceAI URL: http://127.0.0.1:5050/login
echo Version check: http://127.0.0.1:5050/version
echo.
start "" http://127.0.0.1:5050/login
python app.py
pause
