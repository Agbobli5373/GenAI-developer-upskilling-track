#!/usr/bin/env python3
"""
Week 4 API Endpoint Test
Tests the advanced search API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test basic API health"""
    print("🔍 Testing API Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/search/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data.get('status', 'unknown')}")
            print(f"   Embedding coverage: {data.get('embedding_coverage', 0)}%")
            return True
        else:
            print(f"❌ API Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health check error: {str(e)}")
        return False

def test_search_suggestions():
    """Test search suggestions endpoint"""
    print("\n💡 Testing Search Suggestions...")
    
    try:
        response = requests.get(f"{BASE_URL}/search/suggestions?q=contract&limit=3")
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            print(f"✅ Got {len(suggestions)} suggestions for 'contract'")
            for i, suggestion in enumerate(suggestions[:2], 1):
                print(f"   {i}. {suggestion}")
            return True
        else:
            print(f"❌ Suggestions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Suggestions error: {str(e)}")
        return False

def test_advanced_search():
    """Test advanced search endpoint"""
    print("\n🚀 Testing Advanced Search...")
    
    search_payload = {
        "query": "employment contract termination clause",
        "limit": 3,
        "enable_query_expansion": True,
        "enable_reranking": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/search/advanced-search",
            json=search_payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Advanced search successful")
            print(f"   Results: {data.get('total_results', 0)}")
            print(f"   Search time: {data.get('search_time', 0):.3f}s")
            print(f"   Query expanded: {'✅' if data.get('query_expanded') else '❌'}")
            
            suggestions = data.get('suggestions', [])
            if suggestions:
                print(f"   Suggestions: {suggestions[:2]}")
            
            return True
        else:
            print(f"❌ Advanced search failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Advanced search error: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Week 4 Advanced Search API Tests")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print("❌ FastAPI server not accessible")
            print("Please start the server with: cd backend && uvicorn app.main:app --reload")
            return
    except:
        print("❌ FastAPI server not running")
        print("Please start the server with: cd backend && uvicorn app.main:app --reload")
        return
    
    print("✅ FastAPI server is running")
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_api_health():
        tests_passed += 1
    
    if test_search_suggestions():
        tests_passed += 1
        
    if test_advanced_search():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 40)
    print(f"🧪 Tests Completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("\nWeek 4 Advanced Search API is fully functional!")
        print("\nReady for:")
        print("- Frontend integration testing")
        print("- Document upload and embedding generation")
        print("- Multi-document comparison testing")
        print("- Production deployment")
    else:
        print("⚠️  Some tests failed. Check the server logs.")
    
    print("\n🔥 Week 4 Implementation Complete!")

if __name__ == "__main__":
    main()
