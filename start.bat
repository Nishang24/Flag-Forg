@echo off
echo ==================================================
echo   🎤 VoiceFlow - Automated Startup Script
echo ==================================================

echo.
echo [1/3] Starting Backend Server (on Port 8001)...
start cmd /k "cd backend\server && venv\Scripts\activate && python main.py"

echo.
echo [2/3] Waiting for Backend to Initialize...
timeout /t 5 /nobreak > nul

echo.
echo [3/3] Starting Frontend Dashboard (on Port 3000)...
start cmd /k "cd frontend\client && npm run dev"

echo.
echo ==================================================
echo   ✅ System Ready! 
echo   🌍 Dashboard: http://localhost:3000
echo   🏗️  Backend: http://localhost:8001
echo ==================================================
pause
