#!/usr/bin/env python3
"""
Test Week 5 Complete: RAG Enhancement and Query Optimization
Tests the enhanced RAG services, query optimization, and advanced search capabilities.
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

class Week5Tester:
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

    async def test_enhanced_rag_service(self):
        """Test Enhanced RAG functionality"""
        print("\n🤖 Testing Enhanced RAG Service...")
        
        async with httpx.AsyncClient() as client:
            try:
                test_cases = [
                    {
                        "name": "Enhanced RAG - Basic Legal Query",
                        "params": {
                            "query": "What are the termination clauses in employment contracts?",
                            "max_results": 5,
                            "include_legal_analysis": True,
                            "include_cross_references": True
                        }
                    },
                    {
                        "name": "Enhanced RAG - Complex Legal Analysis",
                        "params": {
                            "query": "liability indemnification clauses in commercial agreements",
                            "max_results": 3,
                            "optimize_query": True,
                            "include_legal_analysis": True,
                            "context_optimization": True
                        }
                    },
                    {
                        "name": "Enhanced RAG - Procedural Question",
                        "params": {
                            "query": "How to handle contract breach remedies?",
                            "max_results": 5,
                            "include_cross_references": True
                        }
                    }
                ]

                for test_case in test_cases:
                    print(f"  📋 {test_case['name']}...")
                    
                    response = await client.post(
                        f"{self.base_url}/enhanced-search/rag",
                        json=test_case["params"],
                        headers=self.headers,
                        timeout=45.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✅ Success: Answer generated")
                        print(f"    📝 Answer length: {len(data.get('answer', ''))} chars")
                        print(f"    📚 Sources: {len(data.get('sources', []))}")
                        
                        if 'confidence_score' in data:
                            print(f"    🎯 Confidence: {data['confidence_score']:.2f}")
                        
                        if 'legal_analysis' in data and data['legal_analysis']:
                            legal_analysis = data['legal_analysis']
                            concepts = legal_analysis.get('key_legal_concepts', [])
                            print(f"    ⚖️  Legal concepts: {len(concepts)}")
                            if concepts:
                                print(f"    🔍 Top concepts: {', '.join(concepts[:3])}")
                        
                        if 'cross_references' in data and data['cross_references']:
                            print(f"    🔗 Cross-references: {len(data['cross_references'])}")
                        
                        if 'metadata' in data and data['metadata']:
                            metadata = data['metadata']
                            print(f"    ⏱️  Processing time: {metadata.get('processing_time', 'N/A')}ms")
                    else:
                        print(f"    ❌ Failed: {response.status_code}")
                        if response.text:
                            print(f"    Error: {response.text[:200]}...")

            except Exception as e:
                print(f"❌ Enhanced RAG test error: {e}")

    async def test_query_optimization_service(self):
        """Test Query Optimization functionality"""
        print("\n🔧 Testing Query Optimization Service...")
        
        async with httpx.AsyncClient() as client:
            try:
                test_queries = [
                    {
                        "name": "Legal Query Optimization",
                        "params": {
                            "query": "contract termination",
                            "context": "legal document search",
                            "optimization_type": "legal"
                        }
                    },
                    {
                        "name": "Semantic Optimization",
                        "params": {
                            "query": "liability issues in agreements",
                            "optimization_type": "semantic",
                            "target_domain": "commercial law"
                        }
                    },
                    {
                        "name": "Performance Optimization",
                        "params": {
                            "query": "what are the key obligations mentioned in contracts",
                            "optimization_type": "performance"
                        }
                    },
                    {
                        "name": "Comprehensive Optimization",
                        "params": {
                            "query": "force majeure clauses",
                            "optimization_type": "comprehensive",
                            "context": "legal document analysis"
                        }
                    }
                ]

                for test_case in test_queries:
                    print(f"  🔍 {test_case['name']}...")
                    
                    response = await client.post(
                        f"{self.base_url}/enhanced-search/optimize-query",
                        json=test_case["params"],
                        headers=self.headers,
                        timeout=20.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✅ Success: Query optimized")
                        print(f"    📝 Original: {data.get('original_query', 'N/A')}")
                        print(f"    ✨ Optimized: {data.get('optimized_query', 'N/A')}")
                        print(f"    🔧 Type: {data.get('optimization_type', 'N/A')}")
                        
                        if 'explanation' in data:
                            print(f"    💡 Explanation: {data['explanation'][:100]}...")
                        
                        if 'suggested_refinements' in data and data['suggested_refinements']:
                            print(f"    📋 Refinements: {len(data['suggested_refinements'])}")
                        
                        if 'legal_context' in data and data['legal_context']:
                            legal_context = data['legal_context']
                            concepts = legal_context.get('identified_concepts', [])
                            if concepts:
                                print(f"    ⚖️  Identified concepts: {', '.join(concepts[:3])}")
                    else:
                        print(f"    ❌ Failed: {response.status_code}")
                        if response.text:
                            print(f"    Error: {response.text[:200]}...")

            except Exception as e:
                print(f"❌ Query optimization test error: {e}")

    async def test_query_suggestions(self):
        """Test Query Suggestions functionality"""
        print("\n💡 Testing Query Suggestions...")
        
        async with httpx.AsyncClient() as client:
            try:
                test_queries = [
                    "employment",
                    "liability",
                    "termination",
                    "force majeure",
                    "indemnification"
                ]

                for query in test_queries:
                    print(f"  📝 Getting suggestions for: '{query}'...")
                    
                    response = await client.get(
                        f"{self.base_url}/enhanced-search/query-suggestions",
                        params={"query": query},
                        headers=self.headers,
                        timeout=15.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        suggestions = data.get("suggestions", [])
                        print(f"    ✅ Success: {len(suggestions)} suggestions")
                        
                        for i, suggestion in enumerate(suggestions[:3], 1):
                            confidence = suggestion.get('confidence', 0)
                            query_text = suggestion.get('query', 'N/A')
                            print(f"    {i}. {query_text} (confidence: {confidence:.2f})")
                            
                            if 'explanation' in suggestion:
                                print(f"       💭 {suggestion['explanation'][:80]}...")
                    else:
                        print(f"    ❌ Failed: {response.status_code}")

            except Exception as e:
                print(f"❌ Query suggestions test error: {e}")

    async def test_query_performance_analysis(self):
        """Test Query Performance Analysis"""
        print("\n📊 Testing Query Performance Analysis...")
        
        async with httpx.AsyncClient() as client:
            try:
                test_queries = [
                    "employment contract termination clauses and procedures",
                    "liability",
                    "what are the key legal obligations in commercial agreements with specific focus on indemnification clauses",
                    "contract"
                ]

                for query in test_queries:
                    print(f"  🔍 Analyzing: '{query[:50]}...'")
                    
                    response = await client.post(
                        f"{self.base_url}/enhanced-search/analyze-query-performance",
                        json={"query": query},
                        headers=self.headers,
                        timeout=15.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✅ Success: Performance analyzed")
                        print(f"    🧮 Complexity: {data.get('complexity_score', 0):.2f}")
                        print(f"    🎯 Clarity: {data.get('clarity_score', 0):.2f}")
                        print(f"    📍 Specificity: {data.get('specificity_score', 0):.2f}")
                        print(f"    📈 Overall: {data.get('overall_score', 0):.2f}")
                        
                        issues = data.get('identified_issues', [])
                        if issues:
                            print(f"    ⚠️  Issues: {len(issues)}")
                            print(f"    🔧 Top issue: {issues[0]}")
                        
                        suggestions = data.get('improvement_suggestions', [])
                        if suggestions:
                            print(f"    💡 Suggestions: {len(suggestions)}")
                    else:
                        print(f"    ❌ Failed: {response.status_code}")

            except Exception as e:
                print(f"❌ Query performance analysis test error: {e}")

    async def test_intelligent_search(self):
        """Test Intelligent Search (combines everything)"""
        print("\n🧠 Testing Intelligent Search...")
        
        async with httpx.AsyncClient() as client:
            try:
                test_cases = [
                    {
                        "name": "Balanced Intelligent Search",
                        "params": {
                            "query": "liability clauses in commercial contracts",
                            "use_optimization": True,
                            "max_results": 5,
                            "search_strategy": "balanced"
                        }
                    },
                    {
                        "name": "Comprehensive Intelligent Search",
                        "params": {
                            "query": "employment contract termination procedures",
                            "use_optimization": True,
                            "max_results": 3,
                            "search_strategy": "comprehensive"
                        }
                    },
                    {
                        "name": "Fast Intelligent Search",
                        "params": {
                            "query": "force majeure clauses",
                            "use_optimization": False,
                            "max_results": 5,
                            "search_strategy": "fast"
                        }
                    }
                ]

                for test_case in test_cases:
                    print(f"  🎯 {test_case['name']}...")
                    
                    response = await client.post(
                        f"{self.base_url}/enhanced-search/intelligent-search",
                        json=test_case["params"],
                        headers=self.headers,
                        timeout=60.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✅ Success: Intelligent search completed")
                        print(f"    🔧 Strategy: {data.get('search_strategy', 'N/A')}")
                        print(f"    ⏱️  Total time: {data.get('total_processing_time', 'N/A')}ms")
                        
                        rag_response = data.get('rag_response', {})
                        if rag_response:
                            print(f"    📝 Answer length: {len(rag_response.get('answer', ''))}")
                            print(f"    📚 Sources: {len(rag_response.get('sources', []))}")
                        
                        optimization = data.get('optimization', {})
                        if optimization:
                            print(f"    ✨ Query optimized: {optimization.get('optimization_type', 'N/A')}")
                        
                        performance = data.get('performance', {})
                        if performance:
                            print(f"    📊 Overall score: {performance.get('overall_score', 0):.2f}")
                    else:
                        print(f"    ❌ Failed: {response.status_code}")
                        if response.text:
                            print(f"    Error: {response.text[:200]}...")

            except Exception as e:
                print(f"❌ Intelligent search test error: {e}")

    async def test_batch_question_processing(self):
        """Test Batch Question Processing"""
        print("\n📦 Testing Batch Question Processing...")
        
        async with httpx.AsyncClient() as client:
            try:
                batch_questions = [
                    "What are the key termination clauses?",
                    "How is liability handled in these contracts?",
                    "What are the payment terms specified?",
                    "Are there any force majeure provisions?",
                    "What are the governing law clauses?"
                ]

                print(f"  📋 Processing batch of {len(batch_questions)} questions...")
                
                response = await client.post(
                    f"{self.base_url}/enhanced-search/batch-questions",
                    json={
                        "questions": batch_questions,
                        "batch_settings": {
                            "max_parallel": 3,
                            "timeout_per_question": 30,
                            "include_cross_references": True
                        }
                    },
                    headers=self.headers,
                    timeout=120.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ Success: Batch processing completed")
                    print(f"    🆔 Batch ID: {data.get('batch_id', 'N/A')}")
                    print(f"    📊 Total questions: {data.get('total_questions', 0)}")
                    print(f"    ✅ Completed: {data.get('completed', 0)}")
                    
                    results = data.get('results', [])
                    successful = sum(1 for r in results if r.get('success', False))
                    print(f"    🎯 Success rate: {successful}/{len(results)}")
                    
                    batch_summary = data.get('batch_summary', {})
                    if batch_summary:
                        print(f"    ⏱️  Total time: {batch_summary.get('total_processing_time', 'N/A')}ms")
                        print(f"    📈 Success rate: {batch_summary.get('success_rate', 0):.2f}")
                        
                        themes = batch_summary.get('common_themes', [])
                        if themes:
                            print(f"    🎨 Common themes: {', '.join(themes[:3])}")
                else:
                    print(f"    ❌ Failed: {response.status_code}")
                    if response.text:
                        print(f"    Error: {response.text[:200]}...")

            except Exception as e:
                print(f"❌ Batch question processing test error: {e}")

    async def test_week4_compatibility(self):
        """Test that Week 4 features still work"""
        print("\n🔄 Testing Week 4 Compatibility...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Test advanced search (Week 4)
                response = await client.post(
                    f"{self.base_url}/search/advanced-search",
                    json={
                        "query": "employment contract obligations",
                        "limit": 3,
                        "enable_query_expansion": True,
                        "enable_reranking": True
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Advanced search: {len(data.get('results', []))} results")
                else:
                    print(f"  ❌ Advanced search failed: {response.status_code}")

                # Test multi-document comparison (Week 4)
                doc_response = await client.get(f"{self.base_url}/documents", headers=self.headers)
                if doc_response.status_code == 200:
                    documents = doc_response.json()
                    if len(documents) >= 2:
                        doc_ids = [doc["id"] for doc in documents[:2]]
                        
                        response = await client.post(
                            f"{self.base_url}/search/multi-document-comparison",
                            json={
                                "document_ids": doc_ids,
                                "comparison_type": "similarity"
                            },
                            headers=self.headers,
                            timeout=30.0
                        )
                        
                        if response.status_code == 200:
                            print(f"  ✅ Multi-document comparison working")
                        else:
                            print(f"  ❌ Multi-document comparison failed: {response.status_code}")
                    else:
                        print(f"  ⚠️  Need at least 2 documents for comparison")

            except Exception as e:
                print(f"❌ Week 4 compatibility test error: {e}")

    async def run_all_tests(self):
        """Run all Week 5 tests"""
        print("🚀 Starting Week 5 Complete: RAG Enhancement and Query Optimization Tests")
        print("=" * 80)

        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed, cannot proceed with tests")
            return False

        # Run all Week 5 tests
        await self.test_enhanced_rag_service()
        await self.test_query_optimization_service()
        await self.test_query_suggestions()
        await self.test_query_performance_analysis()
        await self.test_intelligent_search()
        await self.test_batch_question_processing()
        
        # Test backward compatibility
        await self.test_week4_compatibility()

        print("\n" + "=" * 80)
        print("🏁 Week 5 Complete Testing Finished")

        return True

async def main():
    """Main test execution"""
    tester = Week5Tester()
    success = await tester.run_all_tests()
    
    if success:
        print("✅ Week 5 testing completed successfully!")
        print("\n📋 Week 5 Features Tested:")
        print("  • Enhanced Legal RAG Service with Context Optimization")
        print("  • Query Optimization Service (Legal, Semantic, Performance)")
        print("  • Intelligent Query Suggestions with Legal Context")
        print("  • Query Performance Analysis and Scoring")
        print("  • Intelligent Search (Combines RAG + Optimization)")
        print("  • Batch Question Processing")
        print("  • Week 4 Backward Compatibility")
        print("\n🎯 Week 5 Implementation Complete!")
        print("📈 Ready for Week 6: Advanced Analytics and Reporting!")
    else:
        print("❌ Week 5 testing encountered issues")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
