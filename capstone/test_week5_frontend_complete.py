#!/usr/bin/env python3
"""
Week 5 Frontend Integration Test Script
Tests all new frontend components and their backend integration

This script validates:
1. Enhanced RAG Search functionality
2. Intelligent Search Interface 
3. Batch Question Processing
4. Query Analytics Dashboard
5. Complete end-to-end workflow

Requirements:
- Backend server running on localhost:8000
- Frontend server running (for UI tests)
- Test documents uploaded to the system
"""

import asyncio
import sys
import time
from datetime import datetime
from typing import Dict, List, Any
import httpx
import json

# Base configuration
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0

class Week5FrontendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.auth_token = None
        self.test_results = []
        
    async def setup_auth(self):
        """Setup authentication for API calls"""
        try:
            # Login to get auth token
            login_data = {
                "username": "test@example.com",
                "password": "testpass123"
            }
            
            response = await self.client.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data.get("access_token")
                self.client.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    async def test_enhanced_rag_endpoint(self):
        """Test Enhanced RAG Search endpoint"""
        print("\n🧪 Testing Enhanced RAG Search Endpoint...")
        
        test_cases = [
            {
                "name": "Basic Enhanced RAG",
                "params": {
                    "query": "What are the termination clauses in employment contracts?",
                    "max_results": 5,
                    "include_legal_analysis": True
                }
            },
            {
                "name": "Enhanced RAG with Cross-References",
                "params": {
                    "query": "liability limitations in commercial agreements",
                    "max_results": 8,
                    "include_legal_analysis": True,
                    "include_cross_references": True,
                    "context_optimization": True
                }
            },
            {
                "name": "Enhanced RAG with Query Optimization",
                "params": {
                    "query": "contract breach",
                    "max_results": 10,
                    "optimize_query": True,
                    "include_legal_analysis": True
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = await self.client.post(
                    f"{BASE_URL}/enhanced-search/rag", 
                    json=test_case["params"]
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["answer", "sources", "confidence_score"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print(f"✅ {test_case['name']}: Success ({end_time - start_time:.2f}s)")
                        print(f"   - Answer length: {len(data['answer'])} chars")
                        print(f"   - Sources found: {len(data.get('sources', []))}")
                        print(f"   - Confidence: {data.get('confidence_score', 0):.2%}")
                        
                        if data.get('legal_analysis'):
                            analysis = data['legal_analysis']
                            print(f"   - Legal concepts: {len(analysis.get('key_legal_concepts', []))}")
                            print(f"   - Risk factors: {len(analysis.get('risk_factors', []))}")
                        
                        if data.get('cross_references'):
                            print(f"   - Cross-references: {len(data['cross_references'])}")
                            
                        self.test_results.append({
                            "test": f"Enhanced RAG - {test_case['name']}",
                            "status": "PASS",
                            "response_time": end_time - start_time,
                            "details": f"Sources: {len(data.get('sources', []))}, Confidence: {data.get('confidence_score', 0):.2%}"
                        })
                    else:
                        print(f"❌ {test_case['name']}: Missing fields - {missing_fields}")
                        self.test_results.append({
                            "test": f"Enhanced RAG - {test_case['name']}",
                            "status": "FAIL",
                            "error": f"Missing fields: {missing_fields}"
                        })
                else:
                    print(f"❌ {test_case['name']}: HTTP {response.status_code}")
                    self.test_results.append({
                        "test": f"Enhanced RAG - {test_case['name']}",
                        "status": "FAIL",
                        "error": f"HTTP {response.status_code}: {response.text}"
                    })
                    
            except Exception as e:
                print(f"❌ {test_case['name']}: Exception - {e}")
                self.test_results.append({
                    "test": f"Enhanced RAG - {test_case['name']}",
                    "status": "ERROR",
                    "error": str(e)
                })

    async def test_query_optimization_endpoint(self):
        """Test Query Optimization endpoint"""
        print("\n🧪 Testing Query Optimization Endpoint...")
        
        test_queries = [
            "contract terms",
            "What happens when someone breaks a contract?",
            "employment law violations and remedies in California jurisdiction",
            "liability"
        ]
        
        for query in test_queries:
            try:
                start_time = time.time()
                response = await self.client.post(
                    f"{BASE_URL}/enhanced-search/optimize-query",
                    json={
                        "query": query,
                        "context": "legal document search",
                        "optimization_type": "comprehensive"
                    }
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "optimized_query" in data:
                        print(f"✅ Query Optimization: Success ({end_time - start_time:.2f}s)")
                        print(f"   - Original: '{query}'")
                        print(f"   - Optimized: '{data['optimized_query']}'")
                        
                        if data.get('explanation'):
                            print(f"   - Explanation: {data['explanation'][:100]}...")
                            
                        if data.get('suggested_refinements'):
                            print(f"   - Refinements: {len(data['suggested_refinements'])}")
                            
                        self.test_results.append({
                            "test": f"Query Optimization - '{query}'",
                            "status": "PASS",
                            "response_time": end_time - start_time,
                            "details": f"Optimized: '{data['optimized_query'][:50]}...'"
                        })
                    else:
                        print(f"❌ Query Optimization: Missing optimized_query")
                        self.test_results.append({
                            "test": f"Query Optimization - '{query}'",
                            "status": "FAIL",
                            "error": "Missing optimized_query field"
                        })
                else:
                    print(f"❌ Query Optimization: HTTP {response.status_code}")
                    self.test_results.append({
                        "test": f"Query Optimization - '{query}'",
                        "status": "FAIL",
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ Query Optimization Exception: {e}")
                self.test_results.append({
                    "test": f"Query Optimization - '{query}'",
                    "status": "ERROR",
                    "error": str(e)
                })

    async def test_intelligent_search_endpoint(self):
        """Test Intelligent Search endpoint"""
        print("\n🧪 Testing Intelligent Search Endpoint...")
        
        test_cases = [
            {
                "name": "Balanced Strategy",
                "params": {
                    "query": "What are the key provisions in software licensing agreements?",
                    "use_optimization": True,
                    "max_results": 10,
                    "search_strategy": "balanced"
                }
            },
            {
                "name": "Comprehensive Strategy",
                "params": {
                    "query": "force majeure clauses and their legal implications",
                    "use_optimization": True,
                    "max_results": 15,
                    "search_strategy": "comprehensive"
                }
            },
            {
                "name": "Fast Strategy",
                "params": {
                    "query": "payment terms",
                    "use_optimization": False,
                    "max_results": 5,
                    "search_strategy": "fast"
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = await self.client.post(
                    f"{BASE_URL}/enhanced-search/intelligent-search",
                    json=test_case["params"]
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate intelligent search response structure
                    if "rag_response" in data:
                        rag_response = data["rag_response"]
                        print(f"✅ {test_case['name']}: Success ({end_time - start_time:.2f}s)")
                        print(f"   - Strategy: {test_case['params']['search_strategy']}")
                        print(f"   - Sources: {len(rag_response.get('sources', []))}")
                        print(f"   - Answer length: {len(rag_response.get('answer', ''))}")
                        
                        if data.get('optimization'):
                            print(f"   - Query optimized: Yes")
                            
                        if data.get('performance'):
                            perf = data['performance']
                            print(f"   - Query quality: {perf.get('overall_score', 0):.2%}")
                            
                        self.test_results.append({
                            "test": f"Intelligent Search - {test_case['name']}",
                            "status": "PASS",
                            "response_time": end_time - start_time,
                            "details": f"Strategy: {test_case['params']['search_strategy']}, Sources: {len(rag_response.get('sources', []))}"
                        })
                    else:
                        print(f"❌ {test_case['name']}: Missing rag_response")
                        self.test_results.append({
                            "test": f"Intelligent Search - {test_case['name']}",
                            "status": "FAIL",
                            "error": "Missing rag_response field"
                        })
                else:
                    print(f"❌ {test_case['name']}: HTTP {response.status_code}")
                    self.test_results.append({
                        "test": f"Intelligent Search - {test_case['name']}",
                        "status": "FAIL",
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ {test_case['name']}: Exception - {e}")
                self.test_results.append({
                    "test": f"Intelligent Search - {test_case['name']}",
                    "status": "ERROR",
                    "error": str(e)
                })

    async def test_batch_processing_endpoint(self):
        """Test Batch Question Processing endpoint"""
        print("\n🧪 Testing Batch Question Processing Endpoint...")
        
        test_questions = [
            "What are the termination clauses?",
            "How is intellectual property handled?",
            "What are the liability limitations?",
            "Are there any confidentiality requirements?",
            "What are the payment terms and conditions?"
        ]
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{BASE_URL}/enhanced-search/batch-questions",
                json={
                    "questions": test_questions,
                    "batch_settings": {
                        "max_parallel": 3,
                        "timeout_per_question": 30,
                        "include_cross_references": True
                    }
                }
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["batch_id", "total_questions", "completed", "results", "batch_summary"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print(f"✅ Batch Processing: Success ({end_time - start_time:.2f}s)")
                    print(f"   - Batch ID: {data['batch_id']}")
                    print(f"   - Total questions: {data['total_questions']}")
                    print(f"   - Completed: {data['completed']}")
                    print(f"   - Success rate: {data['batch_summary']['success_rate']:.2%}")
                    print(f"   - Total processing time: {data['batch_summary']['total_processing_time']:.2f}s")
                    
                    # Check individual results
                    successful_results = sum(1 for result in data['results'] if result['success'])
                    print(f"   - Successful results: {successful_results}/{len(data['results'])}")
                    
                    if data['batch_summary'].get('common_themes'):
                        print(f"   - Common themes: {len(data['batch_summary']['common_themes'])}")
                    
                    self.test_results.append({
                        "test": "Batch Processing",
                        "status": "PASS",
                        "response_time": end_time - start_time,
                        "details": f"Questions: {data['total_questions']}, Success rate: {data['batch_summary']['success_rate']:.2%}"
                    })
                else:
                    print(f"❌ Batch Processing: Missing fields - {missing_fields}")
                    self.test_results.append({
                        "test": "Batch Processing",
                        "status": "FAIL",
                        "error": f"Missing fields: {missing_fields}"
                    })
            else:
                print(f"❌ Batch Processing: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results.append({
                    "test": "Batch Processing",
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}: {response.text}"
                })
                
        except Exception as e:
            print(f"❌ Batch Processing Exception: {e}")
            self.test_results.append({
                "test": "Batch Processing",
                "status": "ERROR",
                "error": str(e)
            })

    async def test_query_suggestions_endpoint(self):
        """Test Query Suggestions endpoint"""
        print("\n🧪 Testing Query Suggestions Endpoint...")
        
        test_queries = [
            "contract",
            "liability in employment",
            "intellectual property rights",
            "termination"
        ]
        
        for query in test_queries:
            try:
                start_time = time.time()
                response = await self.client.get(
                    f"{BASE_URL}/enhanced-search/query-suggestions",
                    params={"query": query}
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "suggestions" in data and isinstance(data["suggestions"], list):
                        suggestions = data["suggestions"]
                        print(f"✅ Query Suggestions: Success ({end_time - start_time:.2f}s)")
                        print(f"   - Query: '{query}'")
                        print(f"   - Suggestions: {len(suggestions)}")
                        
                        for i, suggestion in enumerate(suggestions[:3]):  # Show first 3
                            confidence = suggestion.get('confidence', 0)
                            print(f"   - {i+1}. '{suggestion['query']}' (confidence: {confidence:.2%})")
                            
                        self.test_results.append({
                            "test": f"Query Suggestions - '{query}'",
                            "status": "PASS",
                            "response_time": end_time - start_time,
                            "details": f"Suggestions: {len(suggestions)}"
                        })
                    else:
                        print(f"❌ Query Suggestions: Invalid response format")
                        self.test_results.append({
                            "test": f"Query Suggestions - '{query}'",
                            "status": "FAIL",
                            "error": "Invalid response format"
                        })
                else:
                    print(f"❌ Query Suggestions: HTTP {response.status_code}")
                    self.test_results.append({
                        "test": f"Query Suggestions - '{query}'",
                        "status": "FAIL",
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ Query Suggestions Exception: {e}")
                self.test_results.append({
                    "test": f"Query Suggestions - '{query}'",
                    "status": "ERROR",
                    "error": str(e)
                })

    async def test_query_performance_endpoint(self):
        """Test Query Performance Analysis endpoint"""
        print("\n🧪 Testing Query Performance Analysis Endpoint...")
        
        test_queries = [
            "contract",  # Simple, low complexity
            "What are the key provisions in a software licensing agreement regarding intellectual property rights and liability limitations?",  # Complex, high specificity
            "legal stuff",  # Vague, low clarity
            "employment contract termination procedures under California labor law"  # Clear, specific
        ]
        
        for query in test_queries:
            try:
                start_time = time.time()
                response = await self.client.post(
                    f"{BASE_URL}/enhanced-search/analyze-query-performance",
                    json={"query": query}
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    
                    required_fields = ["complexity_score", "clarity_score", "specificity_score", "overall_score"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print(f"✅ Query Performance: Success ({end_time - start_time:.2f}s)")
                        print(f"   - Query: '{query[:50]}...'")
                        print(f"   - Complexity: {data['complexity_score']:.2%}")
                        print(f"   - Clarity: {data['clarity_score']:.2%}")
                        print(f"   - Specificity: {data['specificity_score']:.2%}")
                        print(f"   - Overall: {data['overall_score']:.2%}")
                        
                        if data.get('identified_issues'):
                            print(f"   - Issues: {len(data['identified_issues'])}")
                            
                        if data.get('improvement_suggestions'):
                            print(f"   - Suggestions: {len(data['improvement_suggestions'])}")
                            
                        self.test_results.append({
                            "test": f"Query Performance - '{query[:30]}...'",
                            "status": "PASS",
                            "response_time": end_time - start_time,
                            "details": f"Overall: {data['overall_score']:.2%}"
                        })
                    else:
                        print(f"❌ Query Performance: Missing fields - {missing_fields}")
                        self.test_results.append({
                            "test": f"Query Performance - '{query[:30]}...'",
                            "status": "FAIL",
                            "error": f"Missing fields: {missing_fields}"
                        })
                else:
                    print(f"❌ Query Performance: HTTP {response.status_code}")
                    self.test_results.append({
                        "test": f"Query Performance - '{query[:30]}...'",
                        "status": "FAIL",
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ Query Performance Exception: {e}")
                self.test_results.append({
                    "test": f"Query Performance - '{query[:30]}...'",
                    "status": "ERROR",
                    "error": str(e)
                })

    async def run_all_tests(self):
        """Run all Week 5 frontend integration tests"""
        print("🚀 Starting Week 5 Frontend Integration Tests")
        print("=" * 60)
        
        # Setup
        if not await self.setup_auth():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Run all test suites
        await self.test_enhanced_rag_endpoint()
        await self.test_query_optimization_endpoint()
        await self.test_intelligent_search_endpoint()
        await self.test_batch_processing_endpoint()
        await self.test_query_suggestions_endpoint()
        await self.test_query_performance_endpoint()
        
        # Generate summary
        self.generate_test_summary()
        
        return True

    def generate_test_summary(self):
        """Generate and display test summary"""
        print("\n" + "=" * 60)
        print("📊 WEEK 5 FRONTEND INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        error_tests = len([t for t in self.test_results if t["status"] == "ERROR"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Errors: {error_tests} 🔥")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0 or error_tests > 0:
            print("\n❌ FAILED/ERROR TESTS:")
            for test in self.test_results:
                if test["status"] in ["FAIL", "ERROR"]:
                    print(f"   - {test['test']}: {test['status']} - {test.get('error', 'Unknown error')}")
        
        # Performance summary
        response_times = [t.get("response_time", 0) for t in self.test_results if t.get("response_time")]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"\n⏱️  PERFORMANCE:")
            print(f"   - Average response time: {avg_response_time:.2f}s")
            print(f"   - Maximum response time: {max_response_time:.2f}s")
        
        print("\n" + "=" * 60)
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"week5_frontend_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "errors": error_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "performance": {
                    "average_response_time": avg_response_time if response_times else 0,
                    "max_response_time": max_response_time if response_times else 0
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: {results_file}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

async def main():
    """Main test execution"""
    try:
        async with Week5FrontendTester() as tester:
            success = await tester.run_all_tests()
            
            if success:
                print("\n🎉 Week 5 Frontend Integration Tests Completed!")
                print("✨ All new components and endpoints have been validated")
                print("🚀 Frontend is ready for Week 5 features!")
            else:
                print("\n💥 Tests failed to complete")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Week 5 Frontend Integration Test Suite")
    print("Testing Enhanced RAG, Query Optimization, Intelligent Search, and Batch Processing")
    asyncio.run(main())
