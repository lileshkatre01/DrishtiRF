@echo off
echo ========================================================
echo   Starting DrishtiRF - SIGINT Analysis Platform
echo ========================================================
echo.

:: 1. Start Backend in background window
echo [1/2] Launching Backend Server (FastAPI on port 8000)...
start "DrishtiRF Backend" cmd /k ".\drishti_venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000"

:: 2. Start Frontend in background window
echo [2/2] Launching Frontend Dev Server (Vite on port 5173)...
start "DrishtiRF Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   Servers launched!
echo   Open your browser at: http://localhost:5173
echo ========================================================
echo.
timeout /t 3 >nul
start http://localhost:5173
