@echo off
cd backend
call venv\Scripts\activate.bat
echo.
echo ========================================
echo   Starting Well-Log Analysis Backend
echo ========================================
echo.
echo Loading environment from .env...
python test_ai.py
echo.
echo Starting Flask server...
echo.
python app.py
pause
