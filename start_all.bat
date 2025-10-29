@echo off
echo Starting QA Agent Full Stack...
echo ================================

echo Starting Backend in new window...
start "QA Agent Backend" cmd /k start_backend.bat

timeout /t 3 /nobreak

echo Starting Frontend in new window...
start "QA Agent Frontend" cmd /k start_frontend.bat

echo.
echo Both services are starting!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.

pause
