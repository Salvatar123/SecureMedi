@echo off
REM Start SecureMedi Dashboard - Backend Only

cd /d "%~dp0backend"
echo.
echo Starting FastAPI Backend on port 8000...
echo.

call python -m uvicorn app.main:app --port 8000

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error starting backend
    echo Make sure you run: pip install -r requirements.txt
    pause
)
