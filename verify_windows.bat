@echo off
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
  echo [FinanceAI] Virtual environment not found.
  echo Run setup_windows.bat first.
  pause
  exit /b 1
)

echo [FinanceAI] Running core ML/service smoke tests...
venv\Scripts\python.exe smoke_test.py
if errorlevel 1 goto :fail

echo.
echo [FinanceAI] Running browser route smoke tests...
venv\Scripts\python.exe web_smoke_test.py
if errorlevel 1 goto :fail

echo.
echo [FinanceAI] All verification tests passed.
echo You can now run START_FINANCEAI.bat or press F5 in VS Code.
pause
exit /b 0

:fail
echo.
echo [FinanceAI] Verification failed. Read the error above.
pause
exit /b 1
