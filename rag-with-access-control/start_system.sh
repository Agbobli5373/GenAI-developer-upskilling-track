#!/bin/bash
# Complete system startup script

echo "🚀 Starting RAG with Access Control System"
echo "=========================================="

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $1 is already in use"
        return 1
    fi
    return 0
}

# Check if required ports are available
if ! check_port 8000; then
    echo "Backend port 8000 is in use. Please stop the existing service."
    exit 1
fi

if ! check_port 5173; then
    echo "Frontend port 5173 is in use. Please stop the existing service."
    exit 1
fi

# Start backend
echo "🔧 Starting Backend Server..."
cd backend
if [ ! -f ".env" ]; then
    echo "❌ Backend .env file not found. Please create it with GOOGLE_API_KEY."
    exit 1
fi

# Install backend dependencies
pip install -r requirements.txt


# Start backend in background
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
echo "⏳ Waiting for backend to be ready..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID
    exit 1
fi

# Start frontend
echo "🎨 Starting Frontend Application..."
cd ../frontend

# Install frontend dependencies
npm install

# Start frontend
echo "🌐 Frontend will be available at: http://localhost:5173"
echo "🔗 Backend API available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Trap Ctrl+C to cleanup
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID; exit 0' INT

# Start frontend (this will block)
npm run dev

# If we reach here, frontend exited
echo "🛑 Stopping backend..."
kill $BACKEND_PID
