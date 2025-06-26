"""
Evaluation pipeline runner for RAG monitoring system.
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rag_system.simple_rag import rag_system
from src.evaluation.custom_evaluators import RAGEvaluator
from src.utils.logging import rag_logger
from src.utils.config import config


def load_evaluation_dataset() -> List[Dict[str, Any]]:
    """Load evaluation dataset."""
    
    # Sample evaluation dataset
    evaluation_data = [
        {
            "query": "What is artificial intelligence?",
            "expected_keywords": ["computer science", "intelligent machines", "human-like"],
            "category": "ai_basics"
        },
        {
            "query": "Explain machine learning",
            "expected_keywords": ["subset of AI", "learn from data", "algorithms"],
            "category": "ml_basics"
        },
        {
            "query": "What is deep learning?",
            "expected_keywords": ["neural networks", "multiple layers", "complex patterns"],
            "category": "dl_basics"
        },
        {
            "query": "How does natural language processing work?",
            "expected_keywords": ["NLP", "human language", "text processing"],
            "category": "nlp_basics"
        },
        {
            "query": "What is retrieval-augmented generation?",
            "expected_keywords": ["RAG", "retrieval", "generation", "context"],
            "category": "rag_basics"
        },
        {
            "query": "Tell me about computer vision",
            "expected_keywords": ["images", "visual data", "recognition"],
            "category": "cv_basics"
        },
        {
            "query": "What are the applications of AI?",
            "expected_keywords": ["applications", "real-world", "industries"],
            "category": "ai_applications"
        },
        {
            "query": "How do neural networks learn?",
            "expected_keywords": ["training", "weights", "backpropagation"],
            "category": "neural_networks"
        }
    ]
    
    return evaluation_data


def run_evaluation_pipeline():
    """Run the complete evaluation pipeline."""
    
    print("🔍 Starting RAG Evaluation Pipeline...")
    
    # Load evaluation dataset
    print("📊 Loading evaluation dataset...")
    eval_data = load_evaluation_dataset()
    print(f"   Loaded {len(eval_data)} test cases")
    
    # Initialize evaluator
    evaluator = RAGEvaluator()
    
    # Run evaluations
    print("🧪 Running evaluations...")
    results = []
    
    for i, test_case in enumerate(eval_data):
        query = test_case["query"]
        category = test_case["category"]
        
        print(f"   Evaluating {i+1}/{len(eval_data)}: {query[:50]}...")
        
        try:
            # Get RAG response
            response = rag_system.query(
                query=query,
                user_id="evaluation_pipeline",
                session_id=f"eval_{int(time.time())}",
                include_evaluation=True
            )
            
            # Extract metrics
            metrics = response.metadata.get("evaluation_metrics", {})
            
            # Create result record
            result = {
                "query": query,
                "response": response.response,
                "category": category,
                "metrics": metrics,
                "performance": {
                    "retrieval_time": response.retrieval_time,
                    "generation_time": response.generation_time,
                    "total_time": response.total_time
                },
                "retrieved_documents": len(response.retrieved_documents),
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            results.append(result)
            
            # Log progress
            overall_quality = metrics.get("overall_quality", 0)
            print(f"   ✅ Quality Score: {overall_quality:.3f}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            rag_logger.log_error(e, {"query": query, "category": category})
    
    # Generate summary
    print("\n📊 Generating evaluation summary...")
    summary = generate_evaluation_summary(results)
      # Save results
    output_file = Path("outputs") / f"evaluation_results_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": summary,
            "results": results,
            "metadata": {
                "total_test_cases": len(eval_data),
                "successful_evaluations": len(results),
                "evaluation_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                "config": {
                    "model": config.gemini.model,
                    "embedding_model": config.retrieval.embedding_model,
                    "top_k": config.retrieval.top_k
                }
            }
        }, f, indent=2)
    
    print(f"💾 Results saved to: {output_file}")
    
    # Print summary
    print_evaluation_summary(summary)
    
    return results, summary


def generate_evaluation_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics from evaluation results."""
    
    if not results:
        return {"error": "No results to summarize"}
    
    # Extract metrics
    all_metrics = [result["metrics"] for result in results if result["metrics"]]
    
    if not all_metrics:
        return {"error": "No metrics available"}
    
    # Calculate averages
    metric_names = list(all_metrics[0].keys())
    summary = {}
    
    for metric_name in metric_names:
        values = [metrics[metric_name] for metrics in all_metrics if metric_name in metrics]
        if values:
            summary[f"{metric_name}_avg"] = sum(values) / len(values)
            summary[f"{metric_name}_min"] = min(values)
            summary[f"{metric_name}_max"] = max(values)
    
    # Performance metrics
    perf_metrics = [result["performance"] for result in results]
    summary["avg_retrieval_time"] = sum(p["retrieval_time"] for p in perf_metrics) / len(perf_metrics)
    summary["avg_generation_time"] = sum(p["generation_time"] for p in perf_metrics) / len(perf_metrics)
    summary["avg_total_time"] = sum(p["total_time"] for p in perf_metrics) / len(perf_metrics)
    
    # Category breakdown
    categories = {}
    for result in results:
        category = result["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(result["metrics"].get("overall_quality", 0))
    
    summary["category_scores"] = {
        cat: sum(scores) / len(scores) for cat, scores in categories.items()
    }
    
    # Overall stats
    summary["total_evaluations"] = len(results)
    summary["evaluation_success_rate"] = len(all_metrics) / len(results)
    
    return summary


def print_evaluation_summary(summary: Dict[str, Any]):
    """Print evaluation summary to console."""
    
    print("\n" + "="*60)
    print("📊 EVALUATION SUMMARY")
    print("="*60)
    
    # Overall metrics
    print(f"Total Evaluations: {summary.get('total_evaluations', 0)}")
    print(f"Success Rate: {summary.get('evaluation_success_rate', 0):.1%}")
    
    # Quality metrics
    print(f"\n🎯 Quality Metrics:")
    if 'overall_quality_avg' in summary:
        print(f"   Overall Quality: {summary['overall_quality_avg']:.3f} (±{summary.get('overall_quality_max', 0) - summary.get('overall_quality_min', 0):.3f})")
    if 'relevancy_avg' in summary:
        print(f"   Relevancy: {summary['relevancy_avg']:.3f}")
    if 'faithfulness_avg' in summary:
        print(f"   Faithfulness: {summary['faithfulness_avg']:.3f}")
    if 'answer_relevance_avg' in summary:
        print(f"   Answer Relevance: {summary['answer_relevance_avg']:.3f}")
    if 'hallucination_score_avg' in summary:
        print(f"   Hallucination Score: {summary['hallucination_score_avg']:.3f} (lower is better)")
    
    # Performance metrics
    print(f"\n⚡ Performance Metrics:")
    print(f"   Avg Retrieval Time: {summary.get('avg_retrieval_time', 0):.3f}s")
    print(f"   Avg Generation Time: {summary.get('avg_generation_time', 0):.3f}s")
    print(f"   Avg Total Time: {summary.get('avg_total_time', 0):.3f}s")
    
    # Category breakdown
    if 'category_scores' in summary:
        print(f"\n📂 Category Breakdown:")
        for category, score in summary['category_scores'].items():
            print(f"   {category}: {score:.3f}")
    
    print("="*60)


def run_quick_evaluation():
    """Run a quick evaluation with fewer test cases."""
    
    print("🚀 Running Quick Evaluation...")
    
    quick_tests = [
        "What is artificial intelligence?",
        "Explain machine learning",
        "What is deep learning?"
    ]
    
    results = []
    
    for query in quick_tests:
        print(f"   Testing: {query}")
        
        try:
            response = rag_system.query(query, include_evaluation=True)
            metrics = response.metadata.get("evaluation_metrics", {})
            
            result = {
                "query": query,
                "overall_quality": metrics.get("overall_quality", 0),
                "relevancy": metrics.get("relevancy", 0),
                "faithfulness": metrics.get("faithfulness", 0),
                "total_time": response.total_time
            }
            
            results.append(result)
            print(f"   ✅ Quality: {result['overall_quality']:.3f}, Time: {result['total_time']:.3f}s")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    if results:
        avg_quality = sum(r["overall_quality"] for r in results) / len(results)
        avg_time = sum(r["total_time"] for r in results) / len(results)
        
        print(f"\n📊 Quick Results:")
        print(f"   Average Quality: {avg_quality:.3f}")
        print(f"   Average Time: {avg_time:.3f}s")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run RAG evaluation pipeline")
    parser.add_argument("--quick", action="store_true", help="Run quick evaluation")
    args = parser.parse_args()
    
    if args.quick:
        run_quick_evaluation()
    else:
        run_evaluation_pipeline()
