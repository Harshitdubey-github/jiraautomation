@echo off
setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed. Please install Node.js 14 or higher.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "backend\venv" (
    echo Creating Python virtual environment...
    python -m venv backend\venv
)

REM Activate virtual environment
echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

REM Install backend dependencies
echo Installing backend dependencies...
pip install -r backend\requirements.txt

REM Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

REM Start backend server in a new window
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && python -m uvicorn main:app --reload"

REM Start frontend development server
echo Starting frontend development server...
cd frontend
npm start

REM Note: The backend server window will need to be closed manually 