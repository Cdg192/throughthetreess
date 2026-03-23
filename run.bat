@echo off
REM Setup and run ASTHENIA game on Windows

echo.
echo ==============================
echo      ASTHENIA Game Setup
echo ==============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from python.org
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting ASTHENIA...
python asthenia.py

pause
