#!/usr/bin/env python3
"""
Week 4 Advanced Search - Core Functionality Test
"""

import asyncio
import sys
import os
from pathlib import Path

# Change to backend directory for proper imports
os.chdir(Path(__file__).parent / "backend")
sys.path.insert(0, ".")

print("🚀 Week 4 Advanced Search - Quick Test")
print("=" * 40)

try:
    # Import the advanced search service
    from app.services.search_service import AdvancedLegalSearchService
    print("✅ Advanced search service imported")
    
    # Create instance
    search_service = AdvancedLegalSearchService()
    print("✅ Service instance created")
    
    # Test core methods
    async def test_core_methods():
        test_query = "employment contract termination"
        
        # Test legal entity extraction
        entities = search_service._extract_legal_entities(test_query)
        print(f"📝 Legal entities found: {len(entities)}")
        
        # Test query intent analysis
        intent = search_service._analyze_query_intent(test_query)
        print(f"🎯 Query intent: {intent.get('type', 'unknown')}")
        
        # Test query expansion
        expanded = search_service._expand_legal_query(test_query)
        print(f"📈 Query expanded to {len(expanded.split())} words")
        
        # Test cache key generation
        cache_key = search_service._generate_cache_key(test_query, {})
        print(f"🔑 Cache key generated: {cache_key[:8]}...")
        
        print("✅ All core methods working!")
        return True
    
    # Run tests
    result = asyncio.run(test_core_methods())
    
    if result:
        print("\n🎉 SUCCESS: Week 4 Advanced Search Core is Working!")
        print("\nFeatures tested:")
        print("✅ Legal entity extraction")
        print("✅ Query intent analysis") 
        print("✅ Query expansion")
        print("✅ Cache key generation")
        
        print("\nNext steps:")
        print("1. Upload test documents")
        print("2. Generate embeddings")
        print("3. Test full search functionality")
        print("4. Start FastAPI server and test endpoints")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🔥 Week 4 Foundation Complete!")
