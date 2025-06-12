@echo off
REM Complete system startup script for Windows

echo 🚀 Starting RAG with Access Control System
echo ==========================================

REM Start backend
echo 🔧 Starting Backend Server...
cd backend

if not exist ".env" (
    echo ❌ Backend .env file not found. Please create it with GOOGLE_API_KEY.
    pause
    exit /b 1
)

REM Install backend dependencies
pip install -r requirements.txt

REM Start backend in background
start "Backend Server" cmd /c "uvicorn main:app --host 0.0.0.0 --port 8000"

echo ✅ Backend started
echo ⏳ Waiting for backend to be ready...
timeout /t 5 /nobreak > nul

REM Start frontend
echo 🎨 Starting Frontend Application...
cd ..\frontend

REM Install frontend dependencies
npm install

echo 🌐 Frontend will be available at: http://localhost:5173
echo 🔗 Backend API available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the frontend (backend will continue running)
echo.

REM Start frontend
npm run dev

echo.
echo Frontend stopped. Backend is still running.
echo To stop backend, close the "Backend Server" window or use Task Manager.
pause
