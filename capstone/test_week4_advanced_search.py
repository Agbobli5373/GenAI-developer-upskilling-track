#!/usr/bin/env python3
"""
Test script for Week 4 Advanced Search Features
Tests the AdvancedLegalSearchService functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Set the PYTHONPATH environment variable for relative imports
os.environ['PYTHONPATH'] = str(backend_path)

from app.services.search_service import AdvancedLegalSearchService
from app.services.embedding_service import LegalEmbeddingService
from app.core.database import supabase


class Week4AdvancedSearchTester:
    def __init__(self):
        self.advanced_search = AdvancedLegalSearchService()
        self.embedding_service = LegalEmbeddingService()
        self.test_user_id = "test-user-advanced-search"
        
    async def setup_test_data(self):
        """Setup test documents and embeddings if needed"""
        print("🔧 Setting up test data...")
        
        try:
            # Check if we have documents and embeddings
            docs_result = supabase.table("documents").select("id, title").limit(5).execute()
            
            if not docs_result.data:
                print("❌ No documents found. Please upload some documents first.")
                return False
                
            self.test_documents = docs_result.data
            print(f"✅ Found {len(self.test_documents)} test documents")
            
            # Check embedding coverage
            stats = await self.embedding_service.get_embedding_stats()
            print(f"📊 Embedding coverage: {stats.get('embedding_coverage', 0)}%")
            
            if stats.get('embedded_chunks', 0) < 10:
                print("⚠️  Low embedding coverage. Results may be limited.")
                
            return True
            
        except Exception as e:
            print(f"❌ Error setting up test data: {str(e)}")
            return False
    
    async def test_query_analysis(self):
        """Test legal query analysis functionality"""
        print("\n🔍 Testing Legal Query Analysis...")
        
        test_queries = [
            "What are the termination clauses in employment contracts?",
            "How to handle data breach notifications?",
            "Define force majeure in contract law",
            "When does the statute of limitations expire?",
            "What are my obligations under GDPR?"
        ]
        
        for query in test_queries:
            try:
                print(f"\n📝 Analyzing query: '{query}'")
                
                # Test legal entity extraction
                entities = await self.advanced_search._extract_legal_entities(query)
                print(f"   Legal entities: {entities[:3]}...")  # Show first 3
                
                # Test query intent analysis  
                intent = await self.advanced_search._analyze_query_intent(query, entities)
                print(f"   Intent type: {intent.get('type', 'unknown')}")
                print(f"   Legal concepts: {intent.get('legal_concepts', [])}")
                
                # Test query expansion
                expanded = await self.advanced_search._expand_legal_query(query, entities)
                print(f"   Expanded terms: {expanded[:3]}...")  # Show first 3
                
            except Exception as e:
                print(f"   ❌ Error analyzing query: {str(e)}")
        
        print("✅ Query analysis tests completed")
    
    async def test_advanced_search(self):
        """Test advanced semantic search functionality"""
        print("\n🚀 Testing Advanced Semantic Search...")
        
        test_queries = [
            "termination clause employment contract",
            "data protection breach notification requirements",
            "force majeure definition contract"
        ]
        
        for query in test_queries:
            try:
                print(f"\n🔎 Testing search: '{query}'")
                
                # Test advanced search
                results = await self.advanced_search.advanced_semantic_search(
                    query=query,
                    user_id=self.test_user_id,
                    limit=5,
                    enable_query_expansion=True,
                    enable_reranking=True
                )
                
                print(f"   Results found: {results.get('total_results', 0)}")
                print(f"   Search time: {results.get('search_time', 0):.3f}s")
                print(f"   Enhanced scoring: {'✅' if results.get('enhanced_scoring_used', False) else '❌'}")
                
                # Show top result
                if results.get('results'):
                    top_result = results['results'][0]
                    print(f"   Top result score: {top_result.get('combined_score', 0):.3f}")
                    print(f"   Content preview: {top_result.get('content', '')[:100]}...")
                
                # Show suggestions
                suggestions = results.get('suggestions', [])
                if suggestions:
                    print(f"   Suggestions: {suggestions[:2]}")
                
            except Exception as e:
                print(f"   ❌ Error in advanced search: {str(e)}")
        
        print("✅ Advanced search tests completed")
    
    async def test_multi_document_comparison(self):
        """Test multi-document comparison functionality"""
        print("\n📊 Testing Multi-Document Comparison...")
        
        if len(self.test_documents) < 2:
            print("⚠️  Need at least 2 documents for comparison tests")
            return
        
        # Test different comparison types
        comparison_types = ["similarity", "difference", "coverage"]
        doc_ids = [doc['id'] for doc in self.test_documents[:3]]  # Use first 3 docs
        
        for comp_type in comparison_types:
            try:
                print(f"\n📈 Testing {comp_type} comparison...")
                
                results = await self.advanced_search.multi_document_comparison(
                    document_ids=doc_ids,
                    comparison_type=comp_type,
                    user_id=self.test_user_id,
                    analysis_depth="standard"
                )
                
                print(f"   Comparison type: {results.get('comparison_type', 'unknown')}")
                print(f"   Documents analyzed: {results.get('document_count', 0)}")
                
                if comp_type == "similarity":
                    similarities = results.get('similarities', [])
                    print(f"   Similar document pairs: {len(similarities)}")
                    if similarities:
                        top_sim = similarities[0]
                        print(f"   Top similarity score: {top_sim.get('similarity_score', 0):.3f}")
                
                elif comp_type == "difference":
                    differences = results.get('differences', [])
                    print(f"   Documents with unique content: {len(differences)}")
                    if differences:
                        top_diff = differences[0]
                        print(f"   Top uniqueness score: {top_diff.get('uniqueness_score', 0):.3f}")
                
                elif comp_type == "coverage":
                    coverage = results.get('coverage_analysis', {})
                    topics = coverage.get('topic_distribution', {})
                    print(f"   Topics analyzed: {len(topics)}")
                
            except Exception as e:
                print(f"   ❌ Error in {comp_type} comparison: {str(e)}")
        
        print("✅ Multi-document comparison tests completed")
    
    async def test_caching_performance(self):
        """Test caching functionality and performance"""
        print("\n⚡ Testing Caching and Performance...")
        
        test_query = "contract termination clause"
        
        try:
            # First search (should be slower - cache miss)
            print("🔄 First search (cache miss)...")
            start_time = asyncio.get_event_loop().time()
            
            results1 = await self.advanced_search.advanced_semantic_search(
                query=test_query,
                user_id=self.test_user_id,
                limit=5
            )
            
            first_time = asyncio.get_event_loop().time() - start_time
            print(f"   First search time: {first_time:.3f}s")
            
            # Second search (should be faster - cache hit)
            print("🔄 Second search (cache hit)...")
            start_time = asyncio.get_event_loop().time()
            
            results2 = await self.advanced_search.advanced_semantic_search(
                query=test_query,
                user_id=self.test_user_id,
                limit=5
            )
            
            second_time = asyncio.get_event_loop().time() - start_time
            print(f"   Second search time: {second_time:.3f}s")
            
            # Check if caching improved performance
            if second_time < first_time * 0.8:  # 20% improvement threshold
                print("   ✅ Caching appears to be working (performance improved)")
            else:
                print("   ⚠️  Caching may not be working optimally")
            
            # Verify results consistency
            if (results1.get('total_results', 0) == results2.get('total_results', 0) and
                len(results1.get('results', [])) == len(results2.get('results', []))):
                print("   ✅ Cache consistency verified")
            else:
                print("   ❌ Cache consistency issue detected")
                
        except Exception as e:
            print(f"   ❌ Error testing caching: {str(e)}")
        
        print("✅ Caching performance tests completed")
    
    async def test_search_analytics(self):
        """Test search analytics and logging"""
        print("\n📈 Testing Search Analytics...")
        
        try:
            # Perform some searches to generate analytics data
            test_queries = [
                "employment contract terms", 
                "privacy policy requirements",
                "intellectual property rights"
            ]
            
            for query in test_queries:
                await self.advanced_search.advanced_semantic_search(
                    query=query,
                    user_id=self.test_user_id,
                    limit=3
                )
            
            # Check analytics table
            analytics_result = supabase.table("search_analytics").select("*").limit(10).execute()
            
            if analytics_result.data:
                print(f"   Analytics entries found: {len(analytics_result.data)}")
                
                # Show latest entry
                latest = analytics_result.data[-1]
                print(f"   Latest query: '{latest.get('query', '')}'")
                print(f"   Query type: {latest.get('query_type', 'unknown')}")
                print(f"   Results count: {latest.get('results_count', 0)}")
                print(f"   Search time: {latest.get('search_time', 0):.3f}s")
                
                print("   ✅ Analytics logging is working")
            else:
                print("   ⚠️  No analytics data found")
                
        except Exception as e:
            print(f"   ❌ Error testing analytics: {str(e)}")
        
        print("✅ Search analytics tests completed")
    
    async def run_all_tests(self):
        """Run all advanced search tests"""
        print("🧪 Starting Week 4 Advanced Search Tests")
        print("=" * 50)
        
        # Setup
        if not await self.setup_test_data():
            print("❌ Test setup failed. Aborting tests.")
            return False
        
        # Run tests
        await self.test_query_analysis()
        await self.test_advanced_search()
        await self.test_multi_document_comparison()
        await self.test_caching_performance()
        await self.test_search_analytics()
        
        print("\n" + "=" * 50)
        print("🎉 Week 4 Advanced Search Tests Completed!")
        print("\nNext steps:")
        print("- Run the FastAPI server to test API endpoints")
        print("- Test frontend integration")
        print("- Optimize performance based on results")
        
        return True


async def main():
    """Main test function"""
    tester = Week4AdvancedSearchTester()
    
    try:
        success = await tester.run_all_tests()
        return success
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
