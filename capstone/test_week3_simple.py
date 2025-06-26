#!/usr/bin/env python3
"""
Simple Week 3 Test - Vector Search Foundation
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_imports():
    """Test if all Week 3 services can be imported"""
    try:
        print("🧪 Testing Week 3 Service Imports...")
        
        from app.services.embedding_service import LegalEmbeddingService
        print("✅ LegalEmbeddingService imported successfully")
        
        from app.services.search_service import LegalSearchService
        print("✅ LegalSearchService imported successfully")
        
        from app.services.rag_service import LegalRAGService
        print("✅ LegalRAGService imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_embedding_service():
    """Test embedding service functionality"""
    try:
        print("\n🔧 Testing Embedding Service...")
        
        from app.services.embedding_service import LegalEmbeddingService
        
        service = LegalEmbeddingService()
        print("✅ Embedding service initialized")
        
        # Test text embedding generation
        test_text = "This agreement shall terminate upon thirty days written notice"
        embedding = service._generate_text_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"✅ Generated embedding with {len(embedding)} dimensions")
            print(f"   Sample values: {embedding[:3]}...")
            return True
        else:
            print("❌ Failed to generate embedding")
            return False
            
    except Exception as e:
        print(f"❌ Embedding service error: {str(e)}")
        return False

def test_search_service():
    """Test search service functionality"""
    try:
        print("\n🔍 Testing Search Service...")
        
        from app.services.search_service import LegalSearchService
        
        service = LegalSearchService()
        print("✅ Search service initialized")
        
        # Test query enhancement
        test_query = "contract termination"
        enhanced = service.enhance_legal_query(test_query)
        
        if enhanced and len(enhanced) > len(test_query):
            print(f"✅ Query enhanced: '{test_query}' -> '{enhanced[:50]}...'")
            return True
        else:
            print("❌ Failed to enhance query")
            return False
            
    except Exception as e:
        print(f"❌ Search service error: {str(e)}")
        return False

def test_rag_service():
    """Test RAG service functionality"""
    try:
        print("\n🤖 Testing RAG Service...")
        
        from app.services.rag_service import LegalRAGService
        
        service = LegalRAGService()
        print("✅ RAG service initialized")
        
        # Test legal pattern extraction
        test_text = "The contractor shall indemnify and hold harmless the client"
        patterns = service.extract_legal_patterns(test_text)
        
        if patterns and len(patterns) > 0:
            print(f"✅ Extracted {len(patterns)} legal patterns")
            for pattern in patterns[:2]:  # Show first 2 patterns
                print(f"   - {pattern['type']}: {pattern['description']}")
            return True
        else:
            print("❌ Failed to extract legal patterns")
            return False
            
    except Exception as e:
        print(f"❌ RAG service error: {str(e)}")
        return False

def test_api_endpoints():
    """Test if search API endpoints are properly configured"""
    try:
        print("\n🌐 Testing API Endpoints...")
        
        from app.api.api_v1.endpoints.search import router
        print("✅ Search router imported successfully")
        
        # Check if routes are registered
        routes = [route.path for route in router.routes]
        expected_routes = ['/semantic-search', '/rag-query', '/embedding/generate']
        
        found_routes = [route for route in expected_routes if any(route in r for r in routes)]
        
        if len(found_routes) >= 2:
            print(f"✅ Found {len(found_routes)} expected API routes")
            return True
        else:
            print(f"❌ Only found {len(found_routes)} expected routes")
            return False
            
    except Exception as e:
        print(f"❌ API endpoints error: {str(e)}")
        return False

def main():
    """Run all Week 3 tests"""
    print("🚀 Week 3 Vector Search Foundation - Functionality Test")
    print("=" * 60)
    
    tests = [
        ("Service Imports", test_imports),
        ("Embedding Service", test_embedding_service),
        ("Search Service", test_search_service),
        ("RAG Service", test_rag_service),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Week 3 core functionality is working!")
        print("\n📝 Next Steps:")
        print("   1. Test with real documents")
        print("   2. Generate embeddings for existing documents")
        print("   3. Test semantic search functionality")
        print("   4. Integrate with frontend")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
