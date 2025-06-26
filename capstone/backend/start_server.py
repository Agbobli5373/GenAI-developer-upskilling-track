#!/usr/bin/env python3
"""
Simple server startup script for debugging
"""
import sys
import os
from pathlib import Path

# Ensure we're in the right directory
project_root = Path(__file__).parent
os.chdir(project_root)

try:
    print("Starting Clause Intelligence System API Server...")
    print(f"Working directory: {os.getcwd()}")
    
    # Test configuration loading
    print("Loading configuration...")
    from app.core.config import settings
    print(f"✓ Configuration loaded")
    print(f"✓ CORS Origins: {len(settings.get_cors_origins())} origins configured")
    
    # Test main app
    print("Loading FastAPI app...")
    from app.main import app
    print("✓ FastAPI app loaded")
    
    # Start server
    print("Starting uvicorn server...")
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
except Exception as e:
    print(f"✗ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
