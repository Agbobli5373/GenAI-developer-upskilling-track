#!/bin/bash
# Frontend startup script

echo "🚀 Starting RAG Frontend Application..."
echo "===================================="

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start development server
echo "🌐 Starting Vite development server..."
echo "Frontend will be available at: http://localhost:5173"
echo "Make sure backend is running at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"

npm run dev
