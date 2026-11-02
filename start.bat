@echo off
REM ============================================
REM  GradeSense - Student Performance Analytics
REM  Startup Script for Windows
REM ============================================

echo.
echo  ===================================
echo   GradeSense - Starting Application
echo  ===================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

REM Check if dataset exists
if not exist "data\raw\student-mat.csv" (
    echo [INFO] Dataset not found. Attempting to download...
    python src\data_preprocessing.py
    if %errorlevel% neq 0 (
        echo.
        echo [WARNING] Dataset download may have failed.
        echo Please manually download from:
        echo   https://archive.ics.uci.edu/dataset/320/student+performance
        echo Place student-mat.csv in: data\raw\
        echo.
    )
)

REM Check if models exist
if not exist "models\early_performance_model.joblib" (
    echo [INFO] Trained models not found. Training models...
    python src\train_models.py
    if %errorlevel% neq 0 (
        echo [ERROR] Model training failed. Check the error messages above.
        pause
        exit /b 1
    )
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)

echo.
echo [INFO] Starting backend server on http://localhost:8000 ...
echo [INFO] Starting frontend dev server on http://localhost:5173 ...
echo.
echo Press Ctrl+C to stop both servers.
echo.

REM Start backend in background
start "GradeSense Backend" cmd /c "cd /d %~dp0 && python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload"

REM Give backend a moment to start
timeout /t 3 /nobreak >nul

REM Start frontend
cd frontend
npm run dev

pause
