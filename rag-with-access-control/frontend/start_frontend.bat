@echo off
REM Frontend startup script for Windows

echo 🚀 Starting RAG Frontend Application...
echo ====================================

REM Install dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
)

REM Start development server
echo 🌐 Starting Vite development server...
echo Frontend will be available at: http://localhost:5173
echo Make sure backend is running at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server

npm run dev
