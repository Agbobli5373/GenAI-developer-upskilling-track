#!/usr/bin/env python3

import requests
import json
import time

# Test the document processing API endpoints
BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if API is responding"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"API Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API not responding: {str(e)}")
        return False

def test_login():
    """Test user login and get auth token"""
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Login successful, got token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_get_documents(token):
    """Get user's documents"""
    if not token:
        print("No token available")
        return []
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/documents/", headers=headers)
        print(f"Get documents response status: {response.status_code}")
        
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ Found {len(docs)} documents")
            for doc in docs:
                print(f"  - {doc['title']} (Status: {doc['status']}, Type: {doc['file_type']})")
            return docs
        else:
            print(f"❌ Get documents failed: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Get documents error: {str(e)}")
        return []

def test_manual_processing(token, document_id):
    """Test manual document processing"""
    if not token:
        print("No token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print(f"🔄 Processing document: {document_id}")
        response = requests.post(f"{BASE_URL}/api/v1/documents/{document_id}/process", headers=headers)
        print(f"Manual processing response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Processing successful: {result.get('message')}")
            if 'chunks' in result:
                print(f"  - Created {result['chunks']} chunks")
            if 'content_preview' in result:
                print(f"  - Content preview: {result['content_preview']}")
            return True
        else:
            print(f"❌ Processing failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        return False

def main():
    print("🧪 Testing Document Processing API")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        print("❌ API is not responding. Make sure the server is running.")
        return
    
    print("✅ API is responding")
    print("\n" + "=" * 50)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
        
    print("\n" + "=" * 50)
    
    # Get documents
    docs = test_get_documents(token)
    if not docs:
        print("❌ No documents found to test")
        return
    
    print("\n" + "=" * 50)
    
    # Test processing on the first document
    test_document = docs[0]
    document_id = test_document['id']
    
    print(f"🎯 Testing with document: {test_document['title']}")
    print(f"   Status: {test_document['status']}")
    print(f"   Type: {test_document['file_type']}")
    
    # Test manual processing
    success = test_manual_processing(token, document_id)
    
    print("\n" + "=" * 50)
    print("🏁 Testing complete!")

if __name__ == "__main__":
    main()
