"""
System initialization script for RAG monitoring project.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.utils.config import config
from src.utils.logging import rag_logger
from src.rag_system.simple_rag import rag_system
from src.monitoring.performance_monitor import performance_tracker


def initialize_system():
    """Initialize the RAG monitoring system."""
    
    print("🚀 Initializing RAG Monitoring and Evaluation System...")
    
    # Check configuration
    print("✅ Configuration loaded successfully")
    print(f"   - Data path: {config.data.data_path}")
    print(f"   - Log level: {config.monitoring.log_level}")
    print(f"   - Dashboard port: {config.dashboard.port}")
    
    # Initialize directories
    print("📁 Creating directories...")
    directories = [
        config.data.data_path,
        config.data.datasets_path,
        config.data.logs_path,
        "outputs",
        "reports"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   - Created: {directory}")
    
    # Initialize RAG system
    print("🔍 Initializing RAG system...")
    stats = rag_system.get_system_stats()
    print(f"   - Loaded {stats['total_documents']} documents")
    
    # Test logging
    print("📝 Testing logging system...")
    rag_logger.logger.info("System initialization complete")
    
    # Test performance monitoring
    print("📊 Testing performance monitoring...")
    with performance_tracker.track_query("system_initialization_test"):
        import time
        time.sleep(0.1)  # Simulate work
    
    print("✅ System initialization complete!")
    print("\n🎯 Next steps:")
    print("   1. Set up your .env file with API keys")
    print("   2. Run the dashboard: streamlit run src/dashboard/app.py")
    print("   3. Try the evaluation pipeline: python src/evaluation/run_evaluation.py")
    print("   4. Generate reports: python src/reporting/generate_report.py")


def run_system_test():
    """Run a basic system test."""
    
    print("\n🧪 Running system test...")
    
    # Test queries
    test_queries = [
        "What is artificial intelligence?",
        "Explain machine learning",
        "What is deep learning?"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"   Testing query {i+1}: {query[:30]}...")
        
        try:
            response = rag_system.query(query, user_id="test_user")
            print(f"   ✅ Success - Response length: {len(response.response)} chars")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Get performance summary
    perf_summary = performance_tracker.get_rag_performance_summary()
    overall_stats = perf_summary.get("overall_stats", {})
    
    print(f"\n📊 Performance Summary:")
    print(f"   - Total operations: {overall_stats.get('total_operations', 0)}")
    print(f"   - Success rate: {overall_stats.get('overall_success_rate', 0):.1%}")
    print(f"   - Average duration: {overall_stats.get('avg_duration', 0):.3f}s")
    
    print("✅ System test complete!")


if __name__ == "__main__":
    initialize_system()
    run_system_test()
