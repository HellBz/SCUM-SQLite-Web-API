@echo off
title SCUM API Server
echo ==========================================
echo   SCUM SQLite API - Setup & Start
echo ==========================================
echo.

REM === Change working directory to your SCUM SaveFiles folder ===
cd /d "D:\SERVER\SCUM\SCUM\Saved\SaveFiles"
echo [INFO] Current directory: %CD%
echo.

REM === Check if Python is available ===
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found! Please install Python 3.9 or newer.
    pause
    exit /b
)

echo [INFO] Installing required packages...
pip install --upgrade pip >nul
pip install fastapi uvicorn orjson >nul

REM === Check if API script exists ===
if not exist scum_api.py (
    echo [ERROR] scum_api.py not found in this directory!
    echo Please copy the API script into:
    echo    %CD%
    echo.
    pause
    exit /b
)

REM === Check if SCUM.db exists ===
if not exist SCUM.db (
    echo [WARNING] SCUM.db not found in this directory!
    echo Make sure your SCUM.db is located here:
    echo    %CD%
    echo.
    pause
)

echo [INFO] Starting FastAPI server...
echo.
uvicorn scum_api:app --reload --host 0.0.0.0 --port 8000

pause
