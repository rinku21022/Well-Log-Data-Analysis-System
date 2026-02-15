@echo off
echo ========================================
echo Well-Log Data Analysis System - Startup
echo ========================================
echo.

echo Starting Backend Server...
start cmd /k "cd backend && venv\Scripts\activate && python app.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul
