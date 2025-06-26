"""
Streamlit dashboard for RAG monitoring and evaluation.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# Import our RAG system components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_system.simple_rag import rag_system
from src.monitoring.performance_monitor import performance_tracker
from src.evaluation.custom_evaluators import RAGEvaluator
from src.utils.config import config


def main():
    """Main dashboard application."""
    
    st.set_page_config(
        page_title="RAG Monitoring Dashboard",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 RAG Monitoring and Evaluation Dashboard")
    st.markdown("Real-time monitoring and evaluation of Retrieval-Augmented Generation systems")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Overview", "Query Testing", "Performance Metrics", "Evaluation Results", "System Health"]
    )
    
    if page == "Overview":
        show_overview()
    elif page == "Query Testing":
        show_query_testing()
    elif page == "Performance Metrics":
        show_performance_metrics()
    elif page == "Evaluation Results":
        show_evaluation_results()
    elif page == "System Health":
        show_system_health()


def show_overview():
    """Show overview dashboard."""
    
    st.header("📊 System Overview")
    
    # Get system stats
    try:
        stats = rag_system.get_system_stats()
        perf_summary = stats.get("performance_summary", {})
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Documents",
                stats.get("total_documents", 0)
            )
        
        with col2:
            overall_stats = perf_summary.get("overall_stats", {})
            st.metric(
                "Total Queries",
                overall_stats.get("total_operations", 0)
            )
        
        with col3:
            success_rate = overall_stats.get("overall_success_rate", 0)
            st.metric(
                "Success Rate",
                f"{success_rate:.1%}",
                delta=f"{(success_rate - 0.95):.1%}" if success_rate > 0 else None
            )
        
        with col4:
            avg_duration = overall_stats.get("avg_duration", 0)
            st.metric(
                "Avg Response Time",
                f"{avg_duration:.2f}s",
                delta=f"{(2.0 - avg_duration):.2f}s" if avg_duration > 0 else None
            )
        
        # Recent activity
        st.subheader("Recent Activity")
        
        # Mock recent queries for demo
        recent_queries = [
            {"timestamp": "2024-01-15 10:30:00", "query": "What is artificial intelligence?", "status": "Success", "duration": 1.2},
            {"timestamp": "2024-01-15 10:28:00", "query": "Explain machine learning", "status": "Success", "duration": 0.8},
            {"timestamp": "2024-01-15 10:25:00", "query": "Deep learning basics", "status": "Success", "duration": 1.5},
        ]
        
        df_recent = pd.DataFrame(recent_queries)
        st.dataframe(df_recent, use_container_width=True)
        
        # Alerts
        alerts = perf_summary.get("alerts", [])
        if alerts:
            st.subheader("🚨 Active Alerts")
            for alert in alerts:
                severity_color = "red" if alert.get("severity") == "high" else "orange"
                st.error(f"**{alert.get('type', 'Unknown')}**: {alert}")
        else:
            st.success("✅ No active alerts")
            
    except Exception as e:
        st.error(f"Error loading system stats: {str(e)}")


def show_query_testing():
    """Show query testing interface."""
    
    st.header("🔍 Query Testing")
    
    # Query input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Enter your query:",
            placeholder="e.g., What is machine learning?"
        )
    
    with col2:
        include_eval = st.checkbox("Include Evaluation", value=True)
    
    if st.button("Submit Query", type="primary"):
        if query:
            with st.spinner("Processing query..."):
                try:
                    # Process the query
                    response = rag_system.query(
                        query=query,
                        user_id="dashboard_user",
                        session_id="dashboard_session",
                        include_evaluation=include_eval
                    )
                    
                    # Display results
                    st.subheader("Response")
                    st.write(response.response)
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Retrieval Time", f"{response.retrieval_time:.3f}s")
                    
                    with col2:
                        st.metric("Generation Time", f"{response.generation_time:.3f}s")
                    
                    with col3:
                        st.metric("Total Time", f"{response.total_time:.3f}s")
                    
                    # Show retrieved documents
                    if response.retrieved_documents:
                        st.subheader("Retrieved Documents")
                        for i, doc in enumerate(response.retrieved_documents):
                            with st.expander(f"Document {i+1} (Score: {response.similarity_scores[i]:.3f})"):
                                st.write(doc.content)
                                if doc.metadata:
                                    st.json(doc.metadata)
                    
                    # Show evaluation metrics
                    if include_eval and "evaluation_metrics" in response.metadata:
                        st.subheader("Evaluation Metrics")
                        metrics = response.metadata["evaluation_metrics"]
                        
                        # Create metrics visualization
                        metrics_df = pd.DataFrame([
                            {"Metric": k.replace("_", " ").title(), "Score": v}
                            for k, v in metrics.items()
                        ])
                        
                        fig = px.bar(
                            metrics_df,
                            x="Metric",
                            y="Score",
                            title="Evaluation Scores",
                            color="Score",
                            color_continuous_scale="RdYlGn"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
        else:
            st.warning("Please enter a query")


def show_performance_metrics():
    """Show performance metrics."""
    
    st.header("📈 Performance Metrics")
    
    try:
        # Get performance summary
        perf_summary = rag_system.get_system_stats()["performance_summary"]
        
        # Overall stats
        overall_stats = perf_summary.get("overall_stats", {})
        
        if overall_stats.get("total_operations", 0) > 0:
            # Operations by type
            ops_by_type = overall_stats.get("operations_by_type", {})
            if ops_by_type:
                st.subheader("Operations by Type")
                
                fig = px.pie(
                    values=list(ops_by_type.values()),
                    names=list(ops_by_type.keys()),
                    title="Distribution of Operations"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Performance by operation type
            st.subheader("Performance by Operation Type")
            
            operation_types = ["rag_query", "document_retrieval", "response_generation", "evaluation"]
            perf_data = []
            
            for op_type in operation_types:
                stats = perf_summary.get(f"{op_type}_stats", {})
                if isinstance(stats, dict) and "avg_duration" in stats:
                    perf_data.append({
                        "Operation": op_type.replace("_", " ").title(),
                        "Avg Duration (s)": stats["avg_duration"],
                        "Success Rate": stats.get("success_rate", 0) * 100,
                        "Total Calls": stats.get("total_calls", 0)
                    })
            
            if perf_data:
                df_perf = pd.DataFrame(perf_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        df_perf,
                        x="Operation",
                        y="Avg Duration (s)",
                        title="Average Duration by Operation",
                        color="Avg Duration (s)",
                        color_continuous_scale="RdYlBu_r"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        df_perf,
                        x="Operation",
                        y="Success Rate",
                        title="Success Rate by Operation",
                        color="Success Rate",
                        color_continuous_scale="RdYlGn"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No performance data available. Run some queries to see metrics.")
            
    except Exception as e:
        st.error(f"Error loading performance metrics: {str(e)}")


def show_evaluation_results():
    """Show evaluation results."""
    
    st.header("📊 Evaluation Results")
    
    # Test case input
    st.subheader("Batch Evaluation")
    
    # Sample test cases
    sample_test_cases = [
        {"query": "What is artificial intelligence?", "expected_answer": "AI is a branch of computer science"},
        {"query": "Explain machine learning", "expected_answer": "ML is a subset of AI"},
        {"query": "What is deep learning?", "expected_answer": "Deep learning uses neural networks"},
    ]
    
    # Allow user to edit test cases
    test_cases_json = st.text_area(
        "Test Cases (JSON format):",
        value=json.dumps(sample_test_cases, indent=2),
        height=200
    )
    
    if st.button("Run Batch Evaluation"):
        try:
            test_cases = json.loads(test_cases_json)
            
            with st.spinner("Running batch evaluation..."):
                results = rag_system.batch_evaluate(test_cases)
                
                # Display results
                st.subheader("Evaluation Results")
                
                # Convert to DataFrame for display
                eval_data = []
                for result in results:
                    metrics = result.get("metrics", {})
                    eval_data.append({
                        "Query": result["query"][:50] + "..." if len(result["query"]) > 50 else result["query"],
                        "Overall Quality": metrics.get("overall_quality", 0),
                        "Relevancy": metrics.get("relevancy", 0),
                        "Faithfulness": metrics.get("faithfulness", 0),
                        "Answer Relevance": metrics.get("answer_relevance", 0),
                        "Hallucination Score": metrics.get("hallucination_score", 0),
                        "Total Time (s)": result["performance"]["total_time"]
                    })
                
                df_eval = pd.DataFrame(eval_data)
                st.dataframe(df_eval, use_container_width=True)
                
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Overall quality distribution
                    fig = px.histogram(
                        df_eval,
                        x="Overall Quality",
                        title="Overall Quality Distribution",
                        nbins=10
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Metrics comparison
                    metrics_cols = ["Relevancy", "Faithfulness", "Answer Relevance"]
                    avg_scores = [df_eval[col].mean() for col in metrics_cols]
                    
                    fig = px.bar(
                        x=metrics_cols,
                        y=avg_scores,
                        title="Average Evaluation Scores",
                        color=avg_scores,
                        color_continuous_scale="RdYlGn"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Summary statistics
                st.subheader("Summary Statistics")
                
                summary_stats = {
                    "Average Overall Quality": df_eval["Overall Quality"].mean(),
                    "Average Relevancy": df_eval["Relevancy"].mean(),
                    "Average Faithfulness": df_eval["Faithfulness"].mean(),
                    "Average Answer Relevance": df_eval["Answer Relevance"].mean(),
                    "Average Hallucination Score": df_eval["Hallucination Score"].mean(),
                    "Average Response Time": df_eval["Total Time (s)"].mean()
                }
                
                col1, col2, col3 = st.columns(3)
                
                for i, (metric, value) in enumerate(summary_stats.items()):
                    with [col1, col2, col3][i % 3]:
                        st.metric(metric, f"{value:.3f}")
                
        except json.JSONDecodeError:
            st.error("Invalid JSON format in test cases")
        except Exception as e:
            st.error(f"Error running batch evaluation: {str(e)}")


def show_system_health():
    """Show system health metrics."""
    
    st.header("🔧 System Health")
    
    try:
        # Get system stats
        stats = rag_system.get_system_stats()
        perf_summary = stats.get("performance_summary", {})
        
        # System overview
        st.subheader("System Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Documents", stats.get("total_documents", 0))
        
        with col2:
            overall_stats = perf_summary.get("overall_stats", {})
            st.metric("Active Operations", overall_stats.get("active_operations", 0))
        
        with col3:
            st.metric("System Status", "✅ Healthy")
        
        # Alerts
        alerts = perf_summary.get("alerts", [])
        
        st.subheader("🚨 Alerts")
        
        if alerts:
            for alert in alerts:
                alert_type = alert.get("type", "Unknown")
                severity = alert.get("severity", "medium")
                
                if severity == "high":
                    st.error(f"**HIGH**: {alert_type} - {alert}")
                else:
                    st.warning(f"**MEDIUM**: {alert_type} - {alert}")
        else:
            st.success("No active alerts")
        
        # System metrics (mock data for demo)
        st.subheader("System Metrics")
        
        # Create mock time series data
        import numpy as np
        
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(hours=1),
            end=datetime.now(),
            freq='1min'
        )
        
        # Mock CPU and memory data
        cpu_data = 20 + 10 * np.sin(np.arange(len(timestamps)) * 0.1) + np.random.normal(0, 5, len(timestamps))
        memory_data = 40 + 15 * np.sin(np.arange(len(timestamps)) * 0.05) + np.random.normal(0, 3, len(timestamps))
        
        df_metrics = pd.DataFrame({
            'timestamp': timestamps,
            'cpu_percent': np.clip(cpu_data, 0, 100),
            'memory_percent': np.clip(memory_data, 0, 100)
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                df_metrics,
                x='timestamp',
                y='cpu_percent',
                title='CPU Usage (%)',
                labels={'cpu_percent': 'CPU %'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                df_metrics,
                x='timestamp',
                y='memory_percent',
                title='Memory Usage (%)',
                labels={'memory_percent': 'Memory %'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Configuration
        st.subheader("Configuration")
        config_data = {
            "Model": "gemini-1.5-flash",
            "Embedding Model": "sentence-transformers/all-MiniLM-L6-v2",
            "Retrieval Top-K": 5,
            "Max Tokens": 1000,
            "Temperature": 0.1
        }
        
        for key, value in config_data.items():
            st.write(f"**{key}**: {value}")
            
    except Exception as e:
        st.error(f"Error loading system health: {str(e)}")


if __name__ == "__main__":
    main()
