@echo off
REM Start SecureMedi Dashboard - Frontend Only

cd /d "%~dp0frontend"
echo.
echo Starting Next.js Frontend on port 3000...
echo.

call npm run dev

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error starting frontend
    echo Make sure you run: npm install
    pause
)
