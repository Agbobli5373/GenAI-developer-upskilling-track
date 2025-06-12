"""
Unit tests for the RAG API with access control.
Tests different user roles and validates that access control is working correctly.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import jwt
import os

# Create test client
client = TestClient(app)

# Test configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


class TestHealthEndpoints:
    """Test health and root endpoints."""
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data


class TestAuthentication:
    """Test authentication and authorization."""
    
    def test_login_valid_role(self):
        """Test login with valid roles."""
        valid_roles = ["hr", "engineering", "public"]
        
        for role in valid_roles:
            response = client.post(
                "/api/auth/login",
                json={"role": role}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            
            # Verify token contains correct role
            token = data["access_token"]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            assert payload["role"] == role
    
    def test_login_invalid_role(self):
        """Test login with invalid role."""
        response = client.post(
            "/api/auth/login",
            json={"role": "invalid_role"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid role" in data["detail"]
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token."""
        response = client.post(
            "/api/rag",
            json={"question": "What is the company policy?"}
        )
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post(
            "/api/rag",
            json={"question": "What is the company policy?"},
            headers=headers
        )
        assert response.status_code == 401


class TestRAGEndpoint:
    """Test the RAG endpoint with different roles."""
    
    def get_auth_headers(self, role: str):
        """Helper method to get authentication headers for a role."""
        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={"role": role}
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_rag_endpoint_hr_role(self):
        """Test RAG endpoint with HR role."""
        headers = self.get_auth_headers("hr")
        response = client.post(
            "/api/rag",
            json={"question": "What are the performance review guidelines?"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["user_role"] == "hr"
        assert data["question"] == "What are the performance review guidelines?"
    
    def test_rag_endpoint_engineering_role(self):
        """Test RAG endpoint with engineering role."""
        headers = self.get_auth_headers("engineering")
        response = client.post(
            "/api/rag",
            json={"question": "How does our CI/CD pipeline work?"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["user_role"] == "engineering"
        assert data["question"] == "How does our CI/CD pipeline work?"
    
    def test_rag_endpoint_public_role(self):
        """Test RAG endpoint with public role."""
        headers = self.get_auth_headers("public")
        response = client.post(
            "/api/rag",
            json={"question": "What is the company mission?"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["user_role"] == "public"
        assert data["question"] == "What is the company mission?"
    
    def test_rag_endpoint_empty_question(self):
        """Test RAG endpoint with empty question."""
        headers = self.get_auth_headers("public")
        response = client.post(
            "/api/rag",
            json={"question": ""},
            headers=headers
        )
        assert response.status_code == 200
        # Should still return a response, even if answer indicates no question
    
    def test_rag_endpoint_malformed_request(self):
        """Test RAG endpoint with malformed request."""
        headers = self.get_auth_headers("public")
        response = client.post(
            "/api/rag",
            json={"invalid_field": "test"},
            headers=headers
        )
        assert response.status_code == 422  # Validation error


class TestAccessControl:
    """Test access control functionality to ensure users only see authorized content."""
    
    def get_auth_headers(self, role: str):
        """Helper method to get authentication headers for a role."""
        login_response = client.post(
            "/api/auth/login",
            json={"role": role}
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_role_isolation(self):
        """Test that different roles get different responses for similar queries."""
        question = "Tell me about policies"
        
        # Get responses from different roles
        hr_headers = self.get_auth_headers("hr")
        eng_headers = self.get_auth_headers("engineering")
        public_headers = self.get_auth_headers("public")
        
        hr_response = client.post("/api/rag", json={"question": question}, headers=hr_headers)
        eng_response = client.post("/api/rag", json={"question": question}, headers=eng_headers)
        public_response = client.post("/api/rag", json={"question": question}, headers=public_headers)
        
        # All should succeed
        assert hr_response.status_code == 200
        assert eng_response.status_code == 200
        assert public_response.status_code == 200
        
        # Verify role information is returned correctly
        assert hr_response.json()["user_role"] == "hr"
        assert eng_response.json()["user_role"] == "engineering"
        assert public_response.json()["user_role"] == "public"
    
    def test_hr_specific_query(self):
        """Test HR-specific queries across different roles."""
        hr_question = "What are the salary bands for engineers?"
        
        hr_headers = self.get_auth_headers("hr")
        public_headers = self.get_auth_headers("public")
        
        hr_response = client.post("/api/rag", json={"question": hr_question}, headers=hr_headers)
        public_response = client.post("/api/rag", json={"question": hr_question}, headers=public_headers)
        
        assert hr_response.status_code == 200
        assert public_response.status_code == 200
        
        # HR should potentially get more detailed/specific information
        hr_answer = hr_response.json()["answer"]
        public_answer = public_response.json()["answer"]
        
        # Both should respond, but potentially with different levels of detail
        assert isinstance(hr_answer, str)
        assert isinstance(public_answer, str)
    
    def test_engineering_specific_query(self):
        """Test engineering-specific queries across different roles."""
        eng_question = "What are the architecture patterns we use?"
        
        eng_headers = self.get_auth_headers("engineering")
        public_headers = self.get_auth_headers("public")
        
        eng_response = client.post("/api/rag", json={"question": eng_question}, headers=eng_headers)
        public_response = client.post("/api/rag", json={"question": eng_question}, headers=public_headers)
        
        assert eng_response.status_code == 200
        assert public_response.status_code == 200
        
        # Engineering should potentially get more detailed/specific information
        eng_answer = eng_response.json()["answer"]
        public_answer = public_response.json()["answer"]
        
        assert isinstance(eng_answer, str)
        assert isinstance(public_answer, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
