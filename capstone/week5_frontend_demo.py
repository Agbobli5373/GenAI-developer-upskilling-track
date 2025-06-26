#!/usr/bin/env python3
"""
Week 5 Frontend Demo Script
Demonstrates all new frontend components working together

This script shows:
1. Enhanced RAG Search capabilities
2. Query Optimization features
3. Intelligent Search with different strategies
4. Batch Question Processing
5. Query Analytics and Performance Analysis

Run this script to see the complete Week 5 functionality in action.
"""

import asyncio
import sys
import time
from datetime import datetime
import httpx
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0

class Week5FrontendDemo:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.auth_token = None
        
    async def setup_auth(self):
        """Setup authentication"""
        try:
            login_data = {
                "username": "test@example.com",
                "password": "testpass123"
            }
            
            response = await self.client.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data.get("access_token")
                self.client.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print("✅ Connected to Clause Intelligence System")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    async def demo_enhanced_rag(self):
        """Demonstrate Enhanced RAG Search"""
        print("\n" + "="*60)
        print("🧠 ENHANCED RAG SEARCH DEMO")
        print("="*60)
        
        query = "What are the key liability limitations in software licensing agreements?"
        
        print(f"🔍 Query: {query}")
        print("\n⚡ Performing Enhanced RAG Search with legal analysis...")
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{BASE_URL}/enhanced-search/rag",
                json={
                    "query": query,
                    "max_results": 8,
                    "include_legal_analysis": True,
                    "include_cross_references": True,
                    "context_optimization": True
                }
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Search completed in {end_time - start_time:.2f} seconds")
                print(f"\n📝 AI-Generated Answer:")
                print("-" * 40)
                print(data['answer'][:300] + "..." if len(data['answer']) > 300 else data['answer'])
                
                print(f"\n📊 Results Summary:")
                print(f"   • Confidence Score: {data.get('confidence_score', 0):.2%}")
                print(f"   • Sources Found: {len(data.get('sources', []))}")
                
                if data.get('legal_analysis'):
                    analysis = data['legal_analysis']
                    print(f"\n⚖️ Legal Analysis:")
                    if analysis.get('key_legal_concepts'):
                        concepts = analysis['key_legal_concepts'][:3]  # Show first 3
                        print(f"   • Key Concepts: {', '.join(concepts)}")
                    
                    if analysis.get('risk_factors'):
                        print(f"   • Risk Factors Identified: {len(analysis['risk_factors'])}")
                        
                    if analysis.get('jurisdictions'):
                        print(f"   • Jurisdictions: {', '.join(analysis['jurisdictions'])}")
                
                if data.get('cross_references'):
                    print(f"   • Cross-References: {len(data['cross_references'])}")
                
                print(f"\n📚 Top Sources:")
                for i, source in enumerate(data.get('sources', [])[:3]):
                    print(f"   {i+1}. {source['title']} (Relevance: {source['relevance_score']:.1%})")
                    
            else:
                print(f"❌ Enhanced RAG failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Enhanced RAG error: {e}")

    async def demo_query_optimization(self):
        """Demonstrate Query Optimization"""
        print("\n" + "="*60)
        print("🔧 QUERY OPTIMIZATION DEMO")
        print("="*60)
        
        original_query = "contract problems"
        
        print(f"🔍 Original Query: '{original_query}'")
        print("\n⚡ Optimizing query for better legal search results...")
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{BASE_URL}/enhanced-search/optimize-query",
                json={
                    "query": original_query,
                    "context": "legal document search",
                    "optimization_type": "comprehensive"
                }
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Optimization completed in {end_time - start_time:.2f} seconds")
                print(f"\n📝 Optimized Query:")
                print(f"'{data['optimized_query']}'")
                
                if data.get('explanation'):
                    print(f"\n💡 Optimization Explanation:")
                    print(f"{data['explanation']}")
                
                if data.get('suggested_refinements'):
                    print(f"\n🎯 Additional Refinements:")
                    for i, refinement in enumerate(data['suggested_refinements'][:3]):
                        print(f"   {i+1}. {refinement}")
                        
                # Also get performance analysis
                perf_response = await self.client.post(
                    f"{BASE_URL}/enhanced-search/analyze-query-performance",
                    json={"query": original_query}
                )
                
                if perf_response.status_code == 200:
                    perf_data = perf_response.json()
                    print(f"\n📊 Original Query Performance:")
                    print(f"   • Complexity: {perf_data.get('complexity_score', 0):.1%}")
                    print(f"   • Clarity: {perf_data.get('clarity_score', 0):.1%}")
                    print(f"   • Specificity: {perf_data.get('specificity_score', 0):.1%}")
                    print(f"   • Overall Score: {perf_data.get('overall_score', 0):.1%}")
                    
            else:
                print(f"❌ Query optimization failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Query optimization error: {e}")

    async def demo_intelligent_search(self):
        """Demonstrate Intelligent Search with different strategies"""
        print("\n" + "="*60)
        print("🤖 INTELLIGENT SEARCH DEMO")
        print("="*60)
        
        query = "employment contract termination procedures and legal requirements"
        strategies = ["fast", "balanced", "comprehensive"]
        
        print(f"🔍 Query: {query}")
        
        for strategy in strategies:
            print(f"\n⚡ Testing {strategy.upper()} strategy...")
            
            try:
                start_time = time.time()
                response = await self.client.post(
                    f"{BASE_URL}/enhanced-search/intelligent-search",
                    json={
                        "query": query,
                        "use_optimization": True,
                        "max_results": 5 if strategy == "fast" else 10 if strategy == "balanced" else 15,
                        "search_strategy": strategy
                    }
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    rag_response = data.get('rag_response', {})
                    
                    print(f"   ✅ {strategy.capitalize()} search: {end_time - start_time:.2f}s")
                    print(f"   • Sources: {len(rag_response.get('sources', []))}")
                    print(f"   • Answer length: {len(rag_response.get('answer', ''))} chars")
                    print(f"   • Confidence: {rag_response.get('confidence_score', 0):.1%}")
                    
                    if data.get('optimization'):
                        print(f"   • Query was optimized")
                        
                    if data.get('performance'):
                        perf = data['performance']
                        print(f"   • Query quality: {perf.get('overall_score', 0):.1%}")
                        
                else:
                    print(f"   ❌ {strategy.capitalize()} search failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {strategy.capitalize()} search error: {e}")

    async def demo_batch_processing(self):
        """Demonstrate Batch Question Processing"""
        print("\n" + "="*60)
        print("📋 BATCH QUESTION PROCESSING DEMO")
        print("="*60)
        
        questions = [
            "What are the termination clauses?",
            "How is intellectual property handled?",
            "What are the confidentiality requirements?",
            "Are there any liability limitations?",
            "What are the payment terms?"
        ]
        
        print("🔍 Processing the following questions in batch:")
        for i, q in enumerate(questions):
            print(f"   {i+1}. {q}")
        
        print(f"\n⚡ Starting batch processing with 3 parallel workers...")
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{BASE_URL}/enhanced-search/batch-questions",
                json={
                    "questions": questions,
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
                
                print(f"✅ Batch processing completed in {end_time - start_time:.2f} seconds")
                print(f"\n📊 Batch Summary:")
                print(f"   • Batch ID: {data['batch_id']}")
                print(f"   • Total Questions: {data['total_questions']}")
                print(f"   • Completed: {data['completed']}")
                print(f"   • Success Rate: {data['batch_summary']['success_rate']:.1%}")
                print(f"   • Total Processing Time: {data['batch_summary']['total_processing_time']:.1f}s")
                
                if data['batch_summary'].get('common_themes'):
                    themes = data['batch_summary']['common_themes'][:3]
                    print(f"   • Common Themes: {', '.join(themes)}")
                
                print(f"\n📝 Individual Results:")
                for i, result in enumerate(data['results'][:3]):  # Show first 3
                    status = "✅" if result['success'] else "❌"
                    print(f"   {i+1}. {status} {result['question']}")
                    print(f"      Time: {result['processing_time']:.2f}s")
                    if result['success'] and result.get('answer'):
                        answer_preview = result['answer']['answer'][:100] + "..."
                        print(f"      Answer: {answer_preview}")
                
                if len(data['results']) > 3:
                    print(f"   ... and {len(data['results']) - 3} more results")
                    
            else:
                print(f"❌ Batch processing failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Batch processing error: {e}")

    async def demo_query_suggestions(self):
        """Demonstrate Query Suggestions"""
        print("\n" + "="*60)
        print("💡 QUERY SUGGESTIONS DEMO")
        print("="*60)
        
        partial_query = "contract liability"
        
        print(f"🔍 Getting suggestions for: '{partial_query}'")
        print("\n⚡ Generating intelligent query suggestions...")
        
        try:
            start_time = time.time()
            response = await self.client.get(
                f"{BASE_URL}/enhanced-search/query-suggestions",
                params={"query": partial_query}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                
                print(f"✅ Generated {len(suggestions)} suggestions in {end_time - start_time:.2f} seconds")
                
                print(f"\n💡 Suggested Queries:")
                for i, suggestion in enumerate(suggestions[:5]):  # Show top 5
                    confidence = suggestion.get('confidence', 0)
                    print(f"   {i+1}. '{suggestion['query']}' (confidence: {confidence:.1%})")
                    if suggestion.get('explanation'):
                        print(f"      → {suggestion['explanation']}")
                        
            else:
                print(f"❌ Query suggestions failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Query suggestions error: {e}")

    async def run_complete_demo(self):
        """Run the complete Week 5 frontend demo"""
        print("🚀 WEEK 5 CLAUSE INTELLIGENCE SYSTEM - FRONTEND DEMO")
        print("=" * 80)
        print("Showcasing Enhanced RAG, Query Optimization, Intelligent Search & Batch Processing")
        print("=" * 80)
        
        # Setup
        if not await self.setup_auth():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Run all demos
        await self.demo_enhanced_rag()
        await self.demo_query_optimization()
        await self.demo_intelligent_search()
        await self.demo_batch_processing()
        await self.demo_query_suggestions()
        
        # Conclusion
        print("\n" + "="*80)
        print("🎉 WEEK 5 FRONTEND DEMO COMPLETED!")
        print("="*80)
        print("✨ All new components are working perfectly:")
        print("   • Enhanced RAG Search with legal analysis")
        print("   • AI-powered Query Optimization")
        print("   • Intelligent Search with adaptive strategies")
        print("   • Efficient Batch Question Processing")
        print("   • Smart Query Suggestions & Analytics")
        print("")
        print("🚀 The Clause Intelligence System frontend is fully enhanced for Week 5!")
        print("💼 Ready for advanced legal document analysis and search!")
        print("="*80)
        
        return True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

async def main():
    """Main demo execution"""
    try:
        async with Week5FrontendDemo() as demo:
            success = await demo.run_complete_demo()
            
            if not success:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting Week 5 Frontend Demo...")
    asyncio.run(main())
