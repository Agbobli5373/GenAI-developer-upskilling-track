#!/usr/bin/env python3
"""
Week 3 Demo - Vector Search Functionality
Demonstrates core Week 3 features without requiring server startup
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

def demo_embedding_generation():
    """Demonstrate embedding generation"""
    print("🧮 Demo: Embedding Generation")
    print("-" * 40)
    
    from app.services.embedding_service import LegalEmbeddingService
    
    service = LegalEmbeddingService()
    
    # Test with legal text samples
    legal_texts = [
        "This agreement shall terminate upon thirty days written notice",
        "The contractor shall indemnify and hold harmless the client",
        "All confidential information must be kept strictly confidential",
        "Payment is due within thirty days of invoice date"
    ]
    
    print("Generating embeddings for legal text samples:")
    
    for i, text in enumerate(legal_texts, 1):
        print(f"\n{i}. Text: '{text}'")
        
        embedding = service._generate_text_embedding(text)
        
        print(f"   Embedding: {len(embedding)} dimensions")
        print(f"   Sample values: {embedding[:3]}")
        
        # Calculate similarity with first text
        if i > 1:
            first_embedding = service._generate_text_embedding(legal_texts[0])
            
            # Simple cosine similarity
            dot_product = sum(a * b for a, b in zip(embedding, first_embedding))
            magnitude1 = sum(a * a for a in embedding) ** 0.5
            magnitude2 = sum(a * a for a in first_embedding) ** 0.5
            similarity = dot_product / (magnitude1 * magnitude2)
            
            print(f"   Similarity to text 1: {similarity:.3f}")
    
    return True

def demo_search_service():
    """Demonstrate search service functionality"""
    print("\n🔍 Demo: Legal Search Service")
    print("-" * 40)
    
    from app.services.search_service import LegalSearchService
    
    service = LegalSearchService()
    
    # Test query enhancement
    test_queries = [
        "contract termination",
        "payment obligations",
        "confidentiality clause",
        "liability limitation"
    ]
    
    print("Legal query enhancement:")
    
    for query in test_queries:
        enhanced = service._enhance_legal_query(query)
        print(f"\nOriginal: '{query}'")
        print(f"Enhanced: '{enhanced}'")
    
    return True

def demo_rag_service():
    """Demonstrate RAG service functionality"""
    print("\n🤖 Demo: Legal RAG Service")
    print("-" * 40)
    
    from app.services.rag_service import LegalRAGService
    
    service = LegalRAGService()
    
    # Test legal pattern extraction
    legal_text = """
    The Contractor shall indemnify and hold harmless the Client from any and all claims, 
    damages, or liabilities arising from the performance of this Agreement. This agreement 
    may be terminated by either party upon thirty (30) days written notice. All confidential 
    information disclosed must be kept strictly confidential and shall not be disclosed to 
    third parties without prior written consent.
    """
    
    print("Extracting legal patterns from sample text:")
    print(f"Text: {legal_text.strip()}")
    
    patterns = service.extract_legal_patterns(legal_text)
    
    print(f"\nFound {len(patterns)} legal patterns:")
    for pattern in patterns:
        print(f"  • {pattern['type']}: {pattern['description']}")
        if pattern.get('keywords'):
            print(f"    Keywords: {', '.join(pattern['keywords'])}")
    
    return True

def demo_vector_search_functions():
    """Demonstrate vector search SQL functions"""
    print("\n📊 Demo: Vector Search Database Functions")
    print("-" * 40)
    
    # Show the SQL functions that were created
    functions = [
        "search_similar_chunks(query_embedding, threshold, max_results)",
        "hybrid_search_chunks(query_text, query_embedding, threshold, max_results)",
        "get_embedding_health()",
        "update_document_embedding_stats()"
    ]
    
    print("Created PostgreSQL functions for vector search:")
    for func in functions:
        print(f"  • {func}")
    
    print("\nDatabase schema enhancements:")
    print("  • Added pgvector extension")
    print("  • Added embedding column (vector(768)) to document_chunks")
    print("  • Created ivfflat index for fast similarity search")
    print("  • Added search_analytics table for tracking")
    print("  • Implemented RLS policies for security")
    
    return True

def demo_api_endpoints():
    """Show available API endpoints"""
    print("\n🌐 Demo: Week 3 API Endpoints")
    print("-" * 40)
    
    endpoints = [
        ("POST", "/api/v1/search/semantic-search", "Semantic search in documents"),
        ("POST", "/api/v1/search/rag-query", "AI-powered question answering"),
        ("POST", "/api/v1/search/embedding/generate", "Generate embedding for text"),
        ("POST", "/api/v1/search/embedding/document/{id}", "Generate embeddings for document"),
        ("GET", "/api/v1/search/embedding/status/{id}", "Check embedding status"),
        ("GET", "/api/v1/search/analytics", "Get search analytics"),
        ("POST", "/api/v1/search/suggestions", "Get search suggestions"),
        ("POST", "/api/v1/search/summarize", "Summarize documents")
    ]
    
    print("Available search and RAG endpoints:")
    for method, endpoint, description in endpoints:
        print(f"  {method:4} {endpoint}")
        print(f"       {description}")
        print()
    
    return True

def main():
    """Run Week 3 demonstration"""
    print("🚀 Week 3 Vector Search Foundation - Demo")
    print("=" * 60)
    
    try:
        # Test each component
        demo_embedding_generation()
        demo_search_service()
        demo_rag_service()
        demo_vector_search_functions()
        demo_api_endpoints()
        
        print("\n" + "=" * 60)
        print("🎉 Week 3 Demo Complete!")
        print("\n📋 Summary of implemented features:")
        print("  ✅ Legal document embedding generation")
        print("  ✅ Semantic search with legal domain enhancements")
        print("  ✅ RAG question answering with pattern extraction")
        print("  ✅ Vector database schema with pgvector")
        print("  ✅ Complete search and analytics API")
        print("  ✅ Legal domain-specific optimizations")
        
        print("\n🎯 Ready for:")
        print("  • Document upload and processing")
        print("  • Real-time semantic search")
        print("  • AI-powered legal question answering")
        print("  • Search analytics and insights")
        print("  • Frontend integration")
        
        print("\n📝 To test with real documents:")
        print("  1. Start the FastAPI server: uvicorn app.main:app --reload")
        print("  2. Upload legal documents via /api/v1/documents/upload")
        print("  3. Generate embeddings via /api/v1/search/embedding/document/{id}")
        print("  4. Test semantic search via /api/v1/search/semantic-search")
        print("  5. Ask questions via /api/v1/search/rag-query")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
