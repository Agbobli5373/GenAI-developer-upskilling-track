@echo off
REM Startup script for the RAG API server (Windows)

echo 🚀 Starting RAG API with Access Control...
echo ==================================

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Start the server
echo 🌐 Starting FastAPI server on http://localhost:8000
echo 📚 API Documentation available at http://localhost:8000/docs
echo 🔍 Health check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
