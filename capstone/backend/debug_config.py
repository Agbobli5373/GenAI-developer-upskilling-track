import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    print("Step 1: Loading environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded")
    
    print("Step 2: Importing settings...")
    from app.core.config import settings
    print("✓ Settings imported successfully")
    
    print("Step 3: Testing configuration values...")
    print(f"✓ SUPABASE_URL: {settings.SUPABASE_URL}")
    print(f"✓ SECRET_KEY: {settings.SECRET_KEY[:10]}...")
    print(f"✓ CORS Origins: {settings.get_cors_origins()}")
    
    print("Step 4: Testing main app import...")
    from app.main import app
    print("✓ Main app imported successfully")
    
    print("All configuration tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
