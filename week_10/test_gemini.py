"""
Quick test script to verify Gemini integration.
"""

import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    import google.generativeai as genai
    from src.utils.config import config
    
    def test_gemini_connection():
        """Test Gemini API connection."""
        
        print("🔍 Testing Gemini API connection...")
        
        # Check if API key is configured
        if not config.gemini.api_key or config.gemini.api_key == "your_google_api_key_here":
            print("❌ Google API key not configured!")
            print("   Please update your .env file with your actual API key.")
            print("   See GOOGLE_API_SETUP.md for instructions.")
            return False
        
        try:
            # Configure Gemini
            genai.configure(api_key=config.gemini.api_key)
            model = genai.GenerativeModel(config.gemini.model)
            
            # Test with a simple prompt
            response = model.generate_content(
                "Say 'Hello from Gemini!' if you can hear me.",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=20
                )
            )
            
            print(f"✅ Gemini API connected successfully!")
            print(f"   Model: {config.gemini.model}")
            print(f"   Test response: {response.text}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Gemini: {str(e)}")
            return False
    
    def test_rag_system():
        """Test RAG system with Gemini."""
        
        print("\n🔍 Testing RAG system...")
        
        try:
            from src.rag_system.simple_rag import rag_system
            
            # Test query
            test_query = "What is artificial intelligence?"
            print(f"   Query: {test_query}")
            
            response = rag_system.query(test_query, include_evaluation=False)
            
            print(f"✅ RAG system working!")
            print(f"   Response: {response.response[:100]}...")
            print(f"   Generation time: {response.generation_time:.3f}s")
            print(f"   Retrieved documents: {len(response.retrieved_documents)}")
            
            return True
            
        except Exception as e:
            print(f"❌ RAG system test failed: {str(e)}")
            return False
    
    if __name__ == "__main__":
        print("🚀 Running Gemini Integration Tests...\n")
        
        # Test 1: Gemini connection
        gemini_ok = test_gemini_connection()
        
        if gemini_ok:
            # Test 2: RAG system
            rag_ok = test_rag_system()
            
            if rag_ok:
                print(f"\n✅ All tests passed! Your RAG system is ready to use with Gemini.")
                print(f"   Next steps:")
                print(f"   1. Run the dashboard: streamlit run src/dashboard/app.py")
                print(f"   2. Try evaluation: python src/evaluation/run_evaluation.py --quick")
            else:
                print(f"\n⚠️ Gemini works but RAG system needs attention.")
        else:
            print(f"\n❌ Please fix Gemini configuration first.")

except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print(f"   Please install required packages:")
    print(f"   pip install google-generativeai")
    print(f"   pip install -r requirements.txt")
