#!/usr/bin/env python3
"""
Test script to verify the Settings configuration fix
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    print("✅ Configuration loaded successfully!")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"API_V1_STR: {settings.API_V1_STR}")
    print(f"SUPABASE_URL: {settings.SUPABASE_URL[:50]}..." if settings.SUPABASE_URL else "SUPABASE_URL: Not set")
    print(f"DATABASE_URL: {settings.DATABASE_URL[:50]}..." if settings.DATABASE_URL else "DATABASE_URL: Not set")
    print("✅ All settings loaded without errors!")
    
except Exception as e:
    print(f"❌ Error loading configuration: {e}")
    sys.exit(1)
