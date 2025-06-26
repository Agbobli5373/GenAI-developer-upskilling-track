"""
Report generation system for RAG monitoring.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rag_system.simple_rag import rag_system
from src.monitoring.performance_monitor import performance_tracker
from src.utils.logging import rag_logger
from src.utils.config import config


class RAGReportGenerator:
    """Generate comprehensive reports for RAG system performance."""
    
    def __init__(self):
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily performance report."""
        
        print("📊 Generating daily report...")
        
        # Get system stats
        system_stats = rag_system.get_system_stats()
        perf_summary = system_stats.get("performance_summary", {})
        
        # Create report structure
        report = {
            "report_type": "daily_performance",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start": (datetime.now() - timedelta(days=1)).isoformat(),
                "end": datetime.now().isoformat()
            },
            "system_overview": {
                "total_documents": system_stats.get("total_documents", 0),
                "system_status": "operational"
            },
            "performance_metrics": self._extract_performance_metrics(perf_summary),
            "quality_metrics": self._extract_quality_metrics(),
            "alerts": perf_summary.get("alerts", []),
            "recommendations": self._generate_recommendations(perf_summary)
        }
        
        # Save report
        filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        report_path = self.output_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, indent=2, fp=f)
        
        print(f"💾 Daily report saved to: {report_path}")
        return report
    
    def generate_evaluation_report(self, evaluation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate evaluation report from results."""
        
        print("📋 Generating evaluation report...")
        
        if not evaluation_results:
            return {"error": "No evaluation results provided"}
        
        # Calculate metrics
        metrics_summary = self._calculate_evaluation_metrics(evaluation_results)
        
        # Create report
        report = {
            "report_type": "evaluation_analysis",
            "generated_at": datetime.now().isoformat(),
            "dataset_info": {
                "total_queries": len(evaluation_results),
                "categories": list(set(r.get("category", "unknown") for r in evaluation_results))
            },
            "metrics_summary": metrics_summary,
            "performance_analysis": self._analyze_performance(evaluation_results),
            "quality_analysis": self._analyze_quality(evaluation_results),
            "detailed_results": evaluation_results[:10],  # Top 10 for brevity
            "insights": self._generate_insights(evaluation_results)
        }
        
        # Save report
        filename = f"evaluation_report_{int(time.time())}.json"
        report_path = self.output_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, indent=2, fp=f)
        
        print(f"💾 Evaluation report saved to: {report_path}")
        return report
    
    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML version of the report."""
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>RAG System Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e9ecef; border-radius: 3px; }}
                .alert {{ background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 3px; margin: 5px 0; }}
                .recommendation {{ background-color: #d4edda; color: #155724; padding: 10px; border-radius: 3px; margin: 5px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 RAG System Report</h1>
                <p><strong>Report Type:</strong> {report_type}</p>
                <p><strong>Generated:</strong> {generated_at}</p>
            </div>
            
            {content}
        </body>
        </html>
        """
        
        # Generate content based on report type
        if report_data.get("report_type") == "daily_performance":
            content = self._generate_daily_html_content(report_data)
        elif report_data.get("report_type") == "evaluation_analysis":
            content = self._generate_evaluation_html_content(report_data)
        else:
            content = "<p>Unknown report type</p>"
        
        html = html_template.format(
            report_type=report_data.get("report_type", "Unknown"),
            generated_at=report_data.get("generated_at", "Unknown"),
            content=content
        )
          # Save HTML report
        filename = f"report_{int(time.time())}.html"
        html_path = self.output_dir / filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"🌐 HTML report saved to: {html_path}")
        return str(html_path)
    
    def _extract_performance_metrics(self, perf_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics from summary."""
        
        overall_stats = perf_summary.get("overall_stats", {})
        
        return {
            "total_operations": overall_stats.get("total_operations", 0),
            "success_rate": overall_stats.get("overall_success_rate", 0),
            "average_duration": overall_stats.get("avg_duration", 0),
            "operations_by_type": overall_stats.get("operations_by_type", {}),
            "error_rate": 1 - overall_stats.get("overall_success_rate", 1)
        }
    
    def _extract_quality_metrics(self) -> Dict[str, Any]:
        """Extract quality metrics (placeholder for now)."""
        
        return {
            "average_relevancy": 0.75,
            "average_faithfulness": 0.80,
            "average_answer_relevance": 0.78,
            "hallucination_rate": 0.15,
            "overall_quality": 0.77
        }
    
    def _generate_recommendations(self, perf_summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on performance."""
        
        recommendations = []
        overall_stats = perf_summary.get("overall_stats", {})
        
        # Performance recommendations
        avg_duration = overall_stats.get("avg_duration", 0)
        if avg_duration > 3.0:
            recommendations.append("Consider optimizing retrieval performance - average response time is above 3 seconds")
        
        success_rate = overall_stats.get("overall_success_rate", 1)
        if success_rate < 0.95:
            recommendations.append("Investigate error sources - success rate is below 95%")
        
        # Alert-based recommendations
        alerts = perf_summary.get("alerts", [])
        if alerts:
            recommendations.append(f"Address {len(alerts)} active alerts to improve system stability")
        
        # General recommendations
        recommendations.extend([
            "Regularly update the document collection to maintain relevancy",
            "Monitor hallucination rates and implement additional fact-checking",
            "Consider A/B testing different retrieval strategies"
        ])
        
        return recommendations
    
    def _calculate_evaluation_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate evaluation metrics summary."""
        
        if not results:
            return {}
        
        # Extract all metrics
        all_metrics = []
        for result in results:
            metrics = result.get("metrics", {})
            if metrics:
                all_metrics.append(metrics)
        
        if not all_metrics:
            return {}
        
        # Calculate averages
        summary = {}
        metric_names = set()
        for metrics in all_metrics:
            metric_names.update(metrics.keys())
        
        for metric_name in metric_names:
            values = [m[metric_name] for m in all_metrics if metric_name in m]
            if values:
                summary[metric_name] = {
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        return summary
    
    def _analyze_performance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance aspects of evaluation results."""
        
        times = []
        for result in results:
            perf = result.get("performance", {})
            if perf.get("total_time"):
                times.append(perf["total_time"])
        
        if not times:
            return {}
        
        return {
            "average_response_time": sum(times) / len(times),
            "fastest_response": min(times),
            "slowest_response": max(times),
            "response_time_std": (sum((t - sum(times)/len(times))**2 for t in times) / len(times))**0.5
        }
    
    def _analyze_quality(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality aspects of evaluation results."""
        
        quality_scores = []
        for result in results:
            metrics = result.get("metrics", {})
            if "overall_quality" in metrics:
                quality_scores.append(metrics["overall_quality"])
        
        if not quality_scores:
            return {}
        
        # Quality categories
        high_quality = len([q for q in quality_scores if q > 0.8])
        medium_quality = len([q for q in quality_scores if 0.6 <= q <= 0.8])
        low_quality = len([q for q in quality_scores if q < 0.6])
        
        return {
            "average_quality": sum(quality_scores) / len(quality_scores),
            "quality_distribution": {
                "high_quality_count": high_quality,
                "medium_quality_count": medium_quality,
                "low_quality_count": low_quality,
                "high_quality_percentage": high_quality / len(quality_scores) * 100
            }
        }
    
    def _generate_insights(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from evaluation results."""
        
        insights = []
        
        if not results:
            return ["No evaluation results available for analysis"]
        
        # Performance insights
        perf_analysis = self._analyze_performance(results)
        if perf_analysis:
            avg_time = perf_analysis.get("average_response_time", 0)
            if avg_time > 2.0:
                insights.append(f"Average response time of {avg_time:.2f}s may impact user experience")
            else:
                insights.append(f"Good response time performance at {avg_time:.2f}s average")
        
        # Quality insights
        quality_analysis = self._analyze_quality(results)
        if quality_analysis:
            avg_quality = quality_analysis.get("average_quality", 0)
            quality_dist = quality_analysis.get("quality_distribution", {})
            
            high_quality_pct = quality_dist.get("high_quality_percentage", 0)
            if high_quality_pct > 70:
                insights.append(f"Excellent quality with {high_quality_pct:.1f}% of responses rated as high quality")
            elif high_quality_pct > 50:
                insights.append(f"Good quality with {high_quality_pct:.1f}% of responses rated as high quality")
            else:
                insights.append(f"Quality needs improvement - only {high_quality_pct:.1f}% of responses rated as high quality")
        
        # Category analysis
        categories = {}
        for result in results:
            category = result.get("category", "unknown")
            quality = result.get("metrics", {}).get("overall_quality", 0)
            
            if category not in categories:
                categories[category] = []
            categories[category].append(quality)
          # Find best and worst performing categories
        if len(categories) > 1:
            cat_averages = {cat: sum(scores)/len(scores) for cat, scores in categories.items()}
            best_cat = max(cat_averages.keys(), key=lambda x: cat_averages[x])
            worst_cat = min(cat_averages.keys(), key=lambda x: cat_averages[x])
            
            insights.append(f"Best performing category: {best_cat} (avg quality: {cat_averages[best_cat]:.3f})")
            insights.append(f"Worst performing category: {worst_cat} (avg quality: {cat_averages[worst_cat]:.3f})")
        
        return insights
    
    def _generate_daily_html_content(self, report: Dict[str, Any]) -> str:
        """Generate HTML content for daily report."""
        
        perf_metrics = report.get("performance_metrics", {})
        quality_metrics = report.get("quality_metrics", {})
        
        content = f"""
        <div class="section">
            <h2>📊 Performance Metrics</h2>
            <div class="metric">Total Operations: {perf_metrics.get('total_operations', 0)}</div>
            <div class="metric">Success Rate: {perf_metrics.get('success_rate', 0):.2%}</div>
            <div class="metric">Average Duration: {perf_metrics.get('average_duration', 0):.3f}s</div>
        </div>
        
        <div class="section">
            <h2>🎯 Quality Metrics</h2>
            <div class="metric">Overall Quality: {quality_metrics.get('overall_quality', 0):.3f}</div>
            <div class="metric">Average Relevancy: {quality_metrics.get('average_relevancy', 0):.3f}</div>
            <div class="metric">Average Faithfulness: {quality_metrics.get('average_faithfulness', 0):.3f}</div>
            <div class="metric">Hallucination Rate: {quality_metrics.get('hallucination_rate', 0):.2%}</div>
        </div>
        """
        
        # Add alerts if any
        alerts = report.get("alerts", [])
        if alerts:
            content += '<div class="section"><h2>🚨 Alerts</h2>'
            for alert in alerts:
                content += f'<div class="alert">{alert}</div>'
            content += '</div>'
        
        # Add recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            content += '<div class="section"><h2>💡 Recommendations</h2>'
            for rec in recommendations:
                content += f'<div class="recommendation">{rec}</div>'
            content += '</div>'
        
        return content
    
    def _generate_evaluation_html_content(self, report: Dict[str, Any]) -> str:
        """Generate HTML content for evaluation report."""
        
        metrics_summary = report.get("metrics_summary", {})
        insights = report.get("insights", [])
        
        content = f"""
        <div class="section">
            <h2>📋 Dataset Information</h2>
            <p>Total Queries: {report.get('dataset_info', {}).get('total_queries', 0)}</p>
            <p>Categories: {', '.join(report.get('dataset_info', {}).get('categories', []))}</p>
        </div>
        """
        
        # Add metrics summary
        if metrics_summary:
            content += '<div class="section"><h2>📊 Metrics Summary</h2><table>'
            content += '<tr><th>Metric</th><th>Average</th><th>Min</th><th>Max</th></tr>'
            
            for metric_name, values in metrics_summary.items():
                if isinstance(values, dict):
                    content += f"""
                    <tr>
                        <td>{metric_name.replace('_', ' ').title()}</td>
                        <td>{values.get('average', 0):.3f}</td>
                        <td>{values.get('min', 0):.3f}</td>
                        <td>{values.get('max', 0):.3f}</td>
                    </tr>
                    """
            
            content += '</table></div>'
        
        # Add insights
        if insights:
            content += '<div class="section"><h2>🔍 Insights</h2>'
            for insight in insights:
                content += f'<p>• {insight}</p>'
            content += '</div>'
        
        return content


def generate_comprehensive_report():
    """Generate a comprehensive system report."""
    
    print("📊 Generating comprehensive RAG system report...")
    
    generator = RAGReportGenerator()
    
    # Generate daily report
    daily_report = generator.generate_daily_report()
    
    # Generate HTML version
    html_path = generator.generate_html_report(daily_report)
    
    print(f"✅ Report generation complete!")
    print(f"   JSON Report: {generator.output_dir}")
    print(f"   HTML Report: {html_path}")
    
    return daily_report


if __name__ == "__main__":
    generate_comprehensive_report()
