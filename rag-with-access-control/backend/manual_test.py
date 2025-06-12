"""
Manual test script to verify the RAG API endpoints.
This script demonstrates the API functionality with different user roles.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login_and_get_token(role):
    """Login with a specific role and get JWT token."""
    print(f"\n=== Testing Login for role: {role} ===")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"role": role}
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if response.status_code == 200:
            return data["access_token"]
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_rag_endpoint(token, question, role):
    """Test the RAG endpoint with authentication."""
    print(f"\n=== Testing RAG Endpoint for role: {role} ===")
    print(f"Question: {question}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/api/rag",
            json={"question": question},
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting RAG API Manual Tests")
    print("=" * 50)
    
    # Test health endpoint
    if not test_health_endpoint():
        print("❌ Health endpoint failed")
        return
    
    # Test different user roles
    roles = ["hr", "engineering", "public"]
    questions = {
        "hr": "What are the performance review guidelines?",
        "engineering": "How does our CI/CD pipeline work?",
        "public": "What is the company mission?"
    }
    
    all_passed = True
    
    for role in roles:
        # Get token for role
        token = test_login_and_get_token(role)
        if not token:
            print(f"❌ Failed to get token for role: {role}")
            all_passed = False
            continue
        
        # Test RAG endpoint with role-specific question
        question = questions.get(role, "Tell me about the company")
        if not test_rag_endpoint(token, question, role):
            print(f"❌ RAG endpoint failed for role: {role}")
            all_passed = False
    
    # Test cross-role queries to verify access control
    print("\n=== Testing Access Control ===")
    hr_token = test_login_and_get_token("hr")
    public_token = test_login_and_get_token("public")
    
    if hr_token and public_token:
        # HR asking engineering question
        test_rag_endpoint(hr_token, "What are the technical architecture patterns?", "hr")
        # Public asking HR question  
        test_rag_endpoint(public_token, "What are the salary bands?", "public")
    
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")

if __name__ == "__main__":
    main()
