#!/usr/bin/env python3

try:
    print("Testing configuration loading...")
    from app.core.config import settings
    print("✓ Configuration loaded successfully!")
    print(f"✓ SUPABASE_URL: {settings.SUPABASE_URL}")
    print(f"✓ CORS Origins: {settings.get_cors_origins()}")
    print(f"✓ SECRET_KEY: {settings.SECRET_KEY[:10]}...")
    
    print("\nTesting main app import...")
    from app.main import app
    print("✓ Main app imported successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
