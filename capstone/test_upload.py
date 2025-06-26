#!/usr/bin/env python3

import requests
import json
import os
from io import BytesIO

# Test the document upload functionality
BASE_URL = "http://localhost:8000"

def test_login():
    """Test user login and get auth token"""
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.text}")
    
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_upload(token):
    """Test document upload"""
    if not token:
        print("No token available for upload test")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple test file
    test_content = b"This is a test document content for testing upload functionality."
    
    files = {
        "file": ("test_document.txt", BytesIO(test_content), "text/plain")
    }
    
    data = {
        "title": "Test Upload Document",
        "description": "Testing upload functionality",
        "document_type": "contract"
    }
    
    print("Attempting to upload document...")
    response = requests.post(f"{BASE_URL}/api/v1/documents/upload", headers=headers, files=files, data=data)
    
    print(f"Upload response status: {response.status_code}")
    print(f"Upload response: {response.text}")
    
    return response.status_code == 200

def main():
    print("Testing document upload functionality...")
    
    # Test login
    token = test_login()
    if not token:
        print("Failed to get auth token")
        return
    
    print(f"Got auth token: {token[:20]}...")
    
    # Test upload
    success = test_upload(token)
    if success:
        print("✅ Upload test successful!")
    else:
        print("❌ Upload test failed!")

if __name__ == "__main__":
    main()
