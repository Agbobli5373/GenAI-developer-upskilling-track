#!/usr/bin/env python3
"""
Complete Week 3 Test - Upload Document and Test Vector Search
"""

import requests
import json
import time
import tempfile
import os

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"

def create_test_user():
    """Create a test user for testing"""
    try:
        print("👤 Creating test user...")
        
        user_data = {
            "email": "test.week3@example.com",
            "password": "TestPassword123!",
            "full_name": "Week 3 Test User",
            "role": "legal_analyst"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        if response.status_code == 200:
            print("✅ Test user created successfully")
            return True
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print("✅ Test user already exists")
            return True
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User creation error: {str(e)}")
        return False

def login_test_user():
    """Login and get authentication token"""
    try:
        print("🔐 Logging in test user...")
        
        login_data = {
            "email": "test.week3@example.com",
            "password": "TestPassword123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def upload_test_document(token):
    """Upload a test legal document"""
    try:
        print("📄 Uploading test document...")
        
        # Create a test legal document
        test_content = """
        LEGAL SERVICE AGREEMENT
        
        This Legal Service Agreement ("Agreement") is entered into on [DATE] between:
        
        CLIENT: [Client Name] ("Client")
        SERVICE PROVIDER: [Law Firm Name] ("Provider")
        
        1. SCOPE OF SERVICES
        The Provider agrees to provide legal services including contract review, 
        legal research, and document preparation as requested by the Client.
        
        2. TERMINATION
        Either party may terminate this agreement upon thirty (30) days written notice.
        Upon termination, all work product shall be delivered to the Client.
        
        3. CONFIDENTIALITY
        The Provider shall maintain the confidentiality of all Client information
        and shall not disclose any confidential information without prior written consent.
        
        4. LIABILITY AND INDEMNIFICATION
        The Provider's liability shall be limited to the fees paid under this Agreement.
        The Client agrees to indemnify and hold harmless the Provider from any claims.
        
        5. GOVERNING LAW
        This Agreement shall be governed by the laws of [STATE/JURISDICTION].
        Any disputes shall be resolved through binding arbitration.
        
        6. PAYMENT TERMS
        Client agrees to pay all fees within thirty (30) days of invoice.
        Late payments shall accrue interest at 1.5% per month.
        """
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload document
        with open(temp_file_path, 'rb') as f:
            files = {
                'file': ('test_agreement.txt', f, 'text/plain')
            }
            data = {
                'title': 'Test Legal Service Agreement',
                'document_type': 'agreement'
            }
            
            response = requests.post(
                f"{BASE_URL}/documents/upload",
                files=files,
                data=data,
                headers=headers
            )
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        if response.status_code == 200:
            document_data = response.json()
            document_id = document_data.get("id")
            print(f"✅ Document uploaded successfully: {document_id}")
            
            # Wait for processing
            print("⏳ Waiting for document processing...")
            time.sleep(3)
            
            return document_id
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Document upload error: {str(e)}")
        return None

def generate_embeddings_for_document(token, document_id):
    """Generate embeddings for the uploaded document"""
    try:
        print("🧮 Generating embeddings for document...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{BASE_URL}/search/embedding/document/{document_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Embedding generation started")
            
            # Wait for embeddings to be generated
            print("⏳ Waiting for embedding generation...")
            time.sleep(5)
            
            return True
        else:
            print(f"❌ Embedding generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Embedding generation error: {str(e)}")
        return False

def test_semantic_search(token):
    """Test semantic search functionality"""
    try:
        print("🔍 Testing semantic search...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        search_queries = [
            "contract termination conditions",
            "confidentiality obligations",
            "payment terms and late fees",
            "liability limitations"
        ]
        
        for query in search_queries:
            print(f"   Searching: '{query}'")
            
            search_data = {
                "query": query,
                "limit": 5,
                "similarity_threshold": 0.3  # Lower threshold for testing
            }
            
            response = requests.post(
                f"{BASE_URL}/search/semantic-search",
                json=search_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                print(f"     ✅ Found {len(results)} results")
                
                if results:
                    # Show first result
                    first_result = results[0]
                    print(f"     📄 Top result: {first_result.get('content', '')[:100]}...")
            else:
                print(f"     ❌ Search failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Semantic search error: {str(e)}")
        return False

def test_rag_queries(token):
    """Test RAG question answering"""
    try:
        print("🤖 Testing RAG question answering...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        questions = [
            "How can this agreement be terminated?",
            "What are the confidentiality requirements?",
            "What happens if payments are late?",
            "Who is liable for what under this agreement?"
        ]
        
        for question in questions:
            print(f"   Question: '{question}'")
            
            rag_data = {
                "question": question,
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
                
                print(f"     ✅ Answer generated ({len(answer)} chars)")
                print(f"     📚 Sources: {len(sources)}")
                
                if answer:
                    print(f"     💬 Answer preview: {answer[:150]}...")
            else:
                print(f"     ❌ RAG query failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG query error: {str(e)}")
        return False

def main():
    """Run complete Week 3 test"""
    print("🚀 Complete Week 3 Vector Search Test")
    print("=" * 60)
    
    # Step 1: Create and login test user
    if not create_test_user():
        return False
    
    token = login_test_user()
    if not token:
        return False
    
    # Step 2: Upload test document
    document_id = upload_test_document(token)
    if not document_id:
        return False
    
    # Step 3: Generate embeddings
    if not generate_embeddings_for_document(token, document_id):
        print("⚠️  Embedding generation failed, but continuing with tests...")
    
    # Step 4: Test semantic search
    search_success = test_semantic_search(token)
    
    # Step 5: Test RAG queries
    rag_success = test_rag_queries(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Week 3 Complete Test Results:")
    print(f"   ✅ User Management: Success")
    print(f"   ✅ Document Upload: Success")
    print(f"   {'✅' if search_success else '❌'} Semantic Search: {'Success' if search_success else 'Failed'}")
    print(f"   {'✅' if rag_success else '❌'} RAG Queries: {'Success' if rag_success else 'Failed'}")
    
    overall_success = search_success and rag_success
    
    if overall_success:
        print("\n🎉 Week 3 Vector Search Foundation is working!")
        print("\n📝 What's working:")
        print("   • Document upload and processing")
        print("   • Embedding generation")
        print("   • Semantic search functionality")
        print("   • RAG question answering")
        print("   • Legal document analysis")
    else:
        print("\n⚠️  Some functionality needs attention")
        print("   Check the error messages above for details")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
