#!/usr/bin/env python3
"""
Test Week 4 Complete Frontend and Backend Integration
Tests the advanced search features, multi-document comparison, and frontend integration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import httpx
import json
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_AUTH = {
    "email": "test@example.com",
    "password": "testpassword123"
}

class Week4CompleteTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = {"Content-Type": "application/json"}
        self.access_token = None

    async def authenticate(self):
        """Get authentication token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/auth/login",
                    json=TEST_AUTH,
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.access_token}"
                    print("✅ Authentication successful")
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Authentication error: {e}")
                return False

    async def test_advanced_search_endpoint(self):
        """Test advanced search endpoint"""
        print("\n🔍 Testing Advanced Search Endpoint...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Test advanced search with various parameters
                test_cases = [
                    {
                        "name": "Basic Advanced Search",
                        "params": {
                            "query": "employment contract termination",
                            "limit": 5,
                            "enable_query_expansion": True,
                            "enable_reranking": True
                        }
                    },
                    {
                        "name": "Legal Entity Search",
                        "params": {
                            "query": "liability clause indemnification",
                            "limit": 3,
                            "enable_query_expansion": True,
                            "enable_reranking": False
                        }
                    },
                    {
                        "name": "Definition Search",
                        "params": {
                            "query": "what is force majeure",
                            "limit": 5,
                            "enable_query_expansion": False,
                            "enable_reranking": True
                        }
                    }
                ]

                for test_case in test_cases:
                    print(f"  📋 {test_case['name']}...")
                    response = await client.post(
                        f"{self.base_url}/search/advanced-search",
                        json=test_case["params"],
                        headers=self.headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✅ Success: {len(data.get('results', []))} results")
                        
                        # Check response structure
                        if 'results' in data:
                            print(f"    📊 Results found: {len(data['results'])}")
                            if data['results']:
                                first_result = data['results'][0]
                                print(f"    🎯 Top result score: {first_result.get('combined_score', 'N/A')}")
                        
                        if 'search_metadata' in data:
                            metadata = data['search_metadata']
                            print(f"    ⏱️  Search time: {metadata.get('search_time_ms', 'N/A')}ms")
                            print(f"    🔄 Query expanded: {metadata.get('query_expanded', False)}")
                            print(f"    📈 Results reranked: {metadata.get('results_reranked', False)}")
                    else:
                        print(f"    ❌ Failed: {response.status_code}")
                        print(f"    Error: {response.text}")

            except Exception as e:
                print(f"❌ Advanced search test error: {e}")

    async def test_multi_document_comparison(self):
        """Test multi-document comparison endpoint"""
        print("\n📊 Testing Multi-Document Comparison...")
        
        async with httpx.AsyncClient() as client:
            try:
                # First get available documents
                response = await client.get(
                    f"{self.base_url}/documents",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    print("❌ Failed to get documents for comparison")
                    return
                
                documents = response.json()
                if len(documents) < 2:
                    print("⚠️  Need at least 2 documents for comparison test")
                    return

                # Select first 2-3 documents for comparison
                doc_ids = [doc["id"] for doc in documents[:min(3, len(documents))]]
                print(f"  📝 Comparing {len(doc_ids)} documents...")

                test_cases = [
                    {
                        "name": "Similarity Analysis",
                        "params": {
                            "document_ids": doc_ids,
                            "comparison_type": "similarity",
                            "analysis_depth": "standard"
                        }
                    },
                    {
                        "name": "Difference Analysis", 
                        "params": {
                            "document_ids": doc_ids,
                            "comparison_type": "differences",
                            "analysis_depth": "detailed"
                        }
                    },
                    {
                        "name": "Coverage Analysis",
                        "params": {
                            "document_ids": doc_ids,
                            "comparison_type": "coverage",
                            "analysis_depth": "comprehensive"
                        }
                    }
                ]

                for test_case in test_cases:
                    print(f"  🔍 {test_case['name']}...")
                    response = await client.post(
                        f"{self.base_url}/search/multi-document-comparison",
                        json=test_case["params"],
                        headers=self.headers,
                        timeout=45.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✅ Success: {data.get('comparison_type', 'N/A')} analysis")
                        print(f"    📄 Documents analyzed: {data.get('document_count', 0)}")
                        
                        if 'similarities' in data and data['similarities']:
                            print(f"    🔗 Similarities found: {len(data['similarities'])}")
                        
                        if 'differences' in data and data['differences']:
                            print(f"    🔀 Differences found: {len(data['differences'])}")
                            
                        if 'coverage_analysis' in data:
                            coverage = data['coverage_analysis']
                            print(f"    📊 Coverage gaps: {len(coverage.get('coverage_gaps', []))}")
                    else:
                        print(f"    ❌ Failed: {response.status_code}")
                        print(f"    Error: {response.text}")

            except Exception as e:
                print(f"❌ Multi-document comparison test error: {e}")

    async def test_search_suggestions(self):
        """Test search suggestions endpoint"""
        print("\n💡 Testing Search Suggestions...")
        
        async with httpx.AsyncClient() as client:
            try:
                test_queries = [
                    "termination",
                    "liability",
                    "contract",
                    "employment",
                    "force"
                ]

                for query in test_queries:
                    print(f"  📝 Getting suggestions for: '{query}'...")
                    response = await client.get(
                        f"{self.base_url}/search/suggestions",
                        params={"q": query, "limit": 5},
                        headers=self.headers,
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        suggestions = data.get("suggestions", [])
                        print(f"    ✅ Success: {len(suggestions)} suggestions")
                        for i, suggestion in enumerate(suggestions[:3], 1):
                            print(f"    {i}. {suggestion}")
                    else:
                        print(f"    ❌ Failed: {response.status_code}")

            except Exception as e:
                print(f"❌ Search suggestions test error: {e}")

    async def test_semantic_search_compatibility(self):
        """Test that existing semantic search still works"""
        print("\n🔄 Testing Semantic Search Compatibility...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/search/semantic-search",
                    json={
                        "query": "employment agreement terms",
                        "limit": 5,
                        "similarity_threshold": 0.7,
                        "include_hybrid": True
                    },
                    headers=self.headers,
                    timeout=20.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Semantic search working: {len(data.get('results', []))} results")
                else:
                    print(f"  ❌ Semantic search failed: {response.status_code}")

            except Exception as e:
                print(f"❌ Semantic search compatibility test error: {e}")

    async def test_rag_functionality(self):
        """Test RAG (Ask Question) functionality"""
        print("\n🤖 Testing RAG Functionality...")
        
        async with httpx.AsyncClient() as client:
            try:
                test_questions = [
                    "What are the termination clauses in employment contracts?",
                    "How is liability handled in these agreements?",
                    "What are the key obligations mentioned?"
                ]

                for question in test_questions:
                    print(f"  ❓ Asking: '{question[:50]}...'")
                    response = await client.post(
                        f"{self.base_url}/search/ask",
                        json={
                            "question": question,
                            "context_limit": 5,
                            "min_similarity": 0.7,
                            "include_analysis": True
                        },
                        headers=self.headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✅ Answer generated: {len(data.get('answer', ''))} chars")
                        print(f"    📚 Sources used: {len(data.get('sources', []))}")
                        if 'confidence_score' in data:
                            print(f"    🎯 Confidence: {data['confidence_score']:.2f}")
                    else:
                        print(f"    ❌ Failed: {response.status_code}")

            except Exception as e:
                print(f"❌ RAG functionality test error: {e}")

    async def run_all_tests(self):
        """Run all Week 4 tests"""
        print("🚀 Starting Week 4 Complete Integration Tests")
        print("=" * 60)

        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed, cannot proceed with tests")
            return False

        # Run all tests
        await self.test_advanced_search_endpoint()
        await self.test_multi_document_comparison()
        await self.test_search_suggestions()
        await self.test_semantic_search_compatibility()
        await self.test_rag_functionality()

        print("\n" + "=" * 60)
        print("🏁 Week 4 Complete Integration Tests Finished")

        return True

async def main():
    """Main test execution"""
    tester = Week4CompleteTester()
    success = await tester.run_all_tests()
    
    if success:
        print("✅ Week 4 testing completed successfully!")
        print("\n📋 Week 4 Features Tested:")
        print("  • Advanced Legal Search with Query Analysis")
        print("  • Multi-Document Comparison (Similarity, Differences, Coverage)")
        print("  • Intelligent Search Suggestions") 
        print("  • Enhanced RAG with Legal Context")
        print("  • Backward Compatibility with Existing Features")
        print("\n🎯 Ready for Week 5: RAG Enhancement and Query Optimization!")
    else:
        print("❌ Week 4 testing encountered issues")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
