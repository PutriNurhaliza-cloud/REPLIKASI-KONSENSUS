@echo off
REM Raft Simulator - Startup Script for Windows

echo ==================================
echo     RAFT SIMULATOR - STARTUP
echo ==================================
echo.
echo Initializing Raft Simulator...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [+] Python found

REM Check if virtual environment exists
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

echo [+] Virtual environment ready

REM Install dependencies
echo [*] Installing/verifying dependencies...
venv\Scripts\pip install -q -r requirements.txt
echo [+] Dependencies installed

REM Run the app
echo.
echo ==================================
echo [*] Starting Flask server...
echo.
echo     URL: http://localhost:5000
echo.
echo     Lab 1: http://localhost:5000/lab1
echo     Lab 2: http://localhost:5000/lab2
echo     Lab 3: http://localhost:5000/lab3
echo     Lab 4: http://localhost:5000/lab4
echo.
echo Press CTRL+C to stop server
echo ==================================
echo.

venv\Scripts\python app.py
pause
