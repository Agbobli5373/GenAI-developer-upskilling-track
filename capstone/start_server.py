#!/usr/bin/env python3
"""
Start FastAPI Server for Week 3 Testing
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Clause Intelligence System API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False  # Set to False for production testing
    )
