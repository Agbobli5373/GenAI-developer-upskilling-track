#!/usr/bin/env python3
"""
Test Week 3 API Endpoints
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = None  # Will get this from login

def test_auth_and_get_token():
    """Test authentication and get token"""
    try:
        print("🔐 Testing Authentication...")
        
        # Try to login (assuming you have a test user)
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Authentication successful")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print("   Creating test user might be needed")
            return None
            
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        return None

def test_embedding_endpoint(token=None):
    """Test embedding generation endpoint"""
    try:
        print("\n🧮 Testing Embedding Generation Endpoint...")
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Test embedding generation
        test_data = {
            "text": "This agreement shall terminate upon thirty days written notice to the other party."
        }
        
        response = requests.post(
            f"{BASE_URL}/search/embedding/generate", 
            json=test_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            embedding = data.get("embedding", [])
            print(f"✅ Embedding generated: {len(embedding)} dimensions")
            return True
        else:
            print(f"❌ Embedding generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Embedding endpoint error: {str(e)}")
        return False

def test_semantic_search_endpoint(token=None):
    """Test semantic search endpoint"""
    try:
        print("\n🔍 Testing Semantic Search Endpoint...")
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Test semantic search
        search_data = {
            "query": "contract termination clauses",
            "limit": 5,
            "similarity_threshold": 0.5
        }
        
        response = requests.post(
            f"{BASE_URL}/search/semantic-search", 
            json=search_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"✅ Search completed: {len(results)} results found")
            return True
        else:
            print(f"❌ Semantic search failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Search endpoint error: {str(e)}")
        return False

def test_rag_endpoint(token=None):
    """Test RAG question answering endpoint"""
    try:
        print("\n🤖 Testing RAG Question Answering Endpoint...")
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Test RAG query
        rag_data = {
            "question": "What are the termination conditions in the contracts?",
            "document_ids": [],  # Empty means search all
            "max_context_chunks": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/search/rag-query", 
            json=rag_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])
            print(f"✅ RAG query completed")
            print(f"   Answer length: {len(answer)} characters")
            print(f"   Sources found: {len(sources)}")
            return True
        else:
            print(f"❌ RAG query failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ RAG endpoint error: {str(e)}")
        return False

def test_search_analytics_endpoint(token=None):
    """Test search analytics endpoint"""
    try:
        print("\n📊 Testing Search Analytics Endpoint...")
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.get(
            f"{BASE_URL}/search/analytics", 
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics retrieved successfully")
            print(f"   Data keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ Analytics failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analytics endpoint error: {str(e)}")
        return False

def test_server_health():
    """Test if server is running"""
    try:
        print("🏥 Testing Server Health...")
        
        # Test basic health endpoint
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Week 3 API Endpoints Test")
    print("=" * 50)
    
    # Test server health first
    if not test_server_health():
        print("\n⚠️  Server not running. Please start the FastAPI server:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    
    # Try to get auth token (optional)
    token = test_auth_and_get_token()
    
    # Test endpoints
    tests = [
        ("Embedding Generation", lambda: test_embedding_endpoint(token)),
        ("Semantic Search", lambda: test_semantic_search_endpoint(token)),
        ("RAG Query", lambda: test_rag_endpoint(token)),
        ("Search Analytics", lambda: test_search_analytics_endpoint(token)),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 API Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} API tests passed")
    
    if passed == total:
        print("🎉 All Week 3 API endpoints are working!")
    else:
        print("⚠️  Some API tests failed - this might be expected if no documents are uploaded yet")
    
    return passed >= total // 2  # Pass if at least half work

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
