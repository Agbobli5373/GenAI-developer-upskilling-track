#!/bin/bash
# API Testing Script using curl
# Run this after starting the server with: uvicorn main:app --port 8000

echo "🧪 Testing RAG API with Access Control"
echo "======================================"

BASE_URL="http://localhost:8000"

# Test health endpoint
echo "1. Testing Health Endpoint"
curl -X GET "$BASE_URL/health" | jq '.'
echo -e "\n"

# Test login for HR role
echo "2. Testing Login - HR Role"
HR_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"role": "hr"}')
echo $HR_RESPONSE | jq '.'
HR_TOKEN=$(echo $HR_RESPONSE | jq -r '.access_token')
echo -e "\n"

# Test login for Engineering role
echo "3. Testing Login - Engineering Role"
ENG_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"role": "engineering"}')
echo $ENG_RESPONSE | jq '.'
ENG_TOKEN=$(echo $ENG_RESPONSE | jq -r '.access_token')
echo -e "\n"

# Test login for Public role
echo "4. Testing Login - Public Role"
PUBLIC_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"role": "public"}')
echo $PUBLIC_RESPONSE | jq '.'
PUBLIC_TOKEN=$(echo $PUBLIC_RESPONSE | jq -r '.access_token')
echo -e "\n"

# Test RAG endpoint with HR token
echo "5. Testing RAG Endpoint - HR Role"
curl -s -X POST "$BASE_URL/api/rag" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $HR_TOKEN" \
  -d '{"question": "What are the performance review guidelines?"}' | jq '.'
echo -e "\n"

# Test RAG endpoint with Engineering token
echo "6. Testing RAG Endpoint - Engineering Role"
curl -s -X POST "$BASE_URL/api/rag" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENG_TOKEN" \
  -d '{"question": "How does our CI/CD pipeline work?"}' | jq '.'
echo -e "\n"

# Test RAG endpoint with Public token
echo "7. Testing RAG Endpoint - Public Role"
curl -s -X POST "$BASE_URL/api/rag" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PUBLIC_TOKEN" \
  -d '{"question": "What is the company mission?"}' | jq '.'
echo -e "\n"

# Test unauthorized access
echo "8. Testing Unauthorized Access"
curl -s -X POST "$BASE_URL/api/rag" \
  -H "Content-Type: application/json" \
  -d '{"question": "This should fail"}' | jq '.'
echo -e "\n"

# Test invalid token
echo "9. Testing Invalid Token"
curl -s -X POST "$BASE_URL/api/rag" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token" \
  -d '{"question": "This should also fail"}' | jq '.'
echo -e "\n"

echo "✅ API Testing Complete!"
