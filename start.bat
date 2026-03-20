@echo off
REM VoiceFlow - Complete Startup Script for Windows
REM This script starts both backend and frontend servers

echo.
echo ╔════════════════════════════════════════════╗
echo ║   🎤 VoiceFlow - Complete System Startup   ║
echo ╚════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Python and Node.js found
echo.

REM Start Backend
echo Starting Backend Server...
cd backend

REM Check if venv exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if requirements are installed
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo ⚠️  WARNING: backend\.env not found!
    echo.
    echo Please create backend\.env with your OpenAI API key:
    echo.
    echo OPENAI_API_KEY=sk-xxx...
    echo.
    echo Get your key from: https://platform.openai.com/api/keys
    echo.
    pause
)

echo.
echo 🚀 Starting FastAPI Backend on http://localhost:8000
echo.
start cmd /k python main.py

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start Frontend in new window
echo.
echo Starting Frontend Server...
cd ..\frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing Node dependencies...
    call npm install
)

echo.
echo 🎨 Starting Next.js Frontend on http://localhost:3000
echo.
call npm run dev

pause
