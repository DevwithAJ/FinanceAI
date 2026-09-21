@echo off
setlocal
cd /d %~dp0

echo =====================================================
echo FinanceAI 2.0 - Windows / VS Code Setup
echo =====================================================

where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo [ERROR] Python was not found in PATH.
    echo Install Python 3.11 or 3.12 and enable Add Python to PATH.
    pause
    exit /b 1
  )
  set PYTHON_CMD=python
) else (
  set PYTHON_CMD=py
)

if not exist venv\Scripts\python.exe (
  echo Creating virtual environment: venv
  %PYTHON_CMD% -m venv venv
  if errorlevel 1 goto :setup_error
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto :install_error
python -m pip install -r requirements.txt
if errorlevel 1 goto :install_error

if not exist .env copy .env.example .env >nul

rem Generate a random SECRET_KEY when the example placeholder is still present.
python -c "from pathlib import Path; import secrets; p=Path('.env'); s=p.read_text(encoding='utf-8'); old='SECRET_KEY=change-this-to-a-long-random-secret'; s=s.replace(old,'SECRET_KEY='+secrets.token_urlsafe(48)); p.write_text(s,encoding='utf-8')"
if errorlevel 1 goto :setup_error

python init_db.py
if errorlevel 1 goto :setup_error

echo.
echo [OK] FinanceAI 2.0 setup complete.
echo NEXT: run verify_windows.bat
echo Then run START_FINANCEAI.bat or press F5 in VS Code.
pause
exit /b 0

:install_error
echo.
echo [ERROR] Python package installation failed. Check your internet connection and retry.
pause
exit /b 1

:setup_error
echo.
echo [ERROR] FinanceAI setup failed. Read the error above.
pause
exit /b 1
