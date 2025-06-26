#!/usr/bin/env python3
import os
import sys

# Change to backend directory
backend_dir = r"c:\Users\IsaacAgbobli\OneDrive - AmaliTech gGmbH\Desktop\GenAI developer upskilling track\capstone\backend"
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

# Test configuration
print("Testing Clause Intelligence System Configuration...")
print(f"Working directory: {os.getcwd()}")
print("-" * 50)

try:
    # Test 1: Load dotenv
    print("1. Loading environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✓ Environment variables loaded")
    
    # Test 2: Import settings
    print("2. Importing configuration...")
    from app.core.config import settings
    print("   ✓ Configuration imported successfully")
    
    # Test 3: Check key values
    print("3. Validating configuration values...")
    print(f"   - API V1 String: {settings.API_V1_STR}")
    print(f"   - Supabase URL: {settings.SUPABASE_URL}")
    print(f"   - Google API Key: {'*' * 10} (configured: {'Yes' if settings.GOOGLE_API_KEY else 'No'})")
    print(f"   - Database URL: {'*' * 20}...{settings.DATABASE_URL[-20:] if settings.DATABASE_URL else 'Not configured'}")
    print(f"   - CORS Origins: {settings.get_cors_origins()}")
    
    # Test 4: Import main app
    print("4. Importing FastAPI application...")
    from app.main import app
    print("   ✓ FastAPI app imported successfully")
    
    print("-" * 50)
    print("✅ ALL TESTS PASSED! Configuration is working correctly.")
    print("You can now start the server with:")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("-" * 50)
    import traceback
    traceback.print_exc()
    sys.exit(1)
