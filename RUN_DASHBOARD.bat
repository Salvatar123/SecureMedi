@echo off
REM SecureMedi Dashboard v2.0 - Complete Auto Launcher for Windows

setlocal enabledelayedexpansion
cls

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  SecureMedi Dashboard v2.0 - Full Stack Launcher          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if this script is in the right directory
if not exist "backend\app\main.py" (
    echo ❌ Error: Cannot find backend files
    echo Make sure you run this from the SecureMedi root directory
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ❌ Error: Cannot find frontend files
    echo Make sure you run this from the SecureMedi root directory
    pause
    exit /b 1
)

REM Start Backend
echo [1/2] Starting FastAPI Backend on port 8000...
echo.

cd /d "%~dp0backend"

REM Check if uvicorn is installed
python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo ❌ Cannot find uvicorn. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install backend dependencies
        pause
        exit /b 1
    )
)

echo Starting backend...
start "SecureMedi Backend" cmd /k python -m uvicorn app.main:app --port 8000

echo ✅ Backend launched (check new window)
echo.

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start Frontend
cd /d "%~dp0frontend"
echo [2/2] Starting Next.js Frontend on port 3000...
echo.

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found! Please install Node.js
    echo   Download from: https://nodejs.org/
    echo   Then restart this launcher
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo ❌ Failed to install frontend dependencies
        pause
        exit /b 1
    )
)

echo Starting frontend...
start "SecureMedi Frontend" cmd /k npm run dev

echo ✅ Frontend launched (check new window)
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║  🚀 SecureMedi Dashboard is Starting!                     ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║  📊 Dashboard:  http://localhost:3000                     ║
echo ║  📚 API Docs:   http://localhost:8000/docs               ║
echo ║  ⏳ Wait 10-15 seconds for services to fully start        ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║  ⛔ To stop: Close both terminal windows                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

timeout /t 5

REM Open browser
echo Opening browser...
start http://localhost:3000

timeout /t 3

cd /d "%~dp0"
echo All done! Check browser and terminal windows
pause
