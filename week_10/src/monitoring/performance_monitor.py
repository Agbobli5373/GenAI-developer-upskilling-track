"""
Performance monitoring system for RAG applications.
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import contextmanager
from collections import defaultdict, deque

from ..utils.config import config
from ..utils.logging import rag_logger


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def finish(self, success: bool = True, error_message: Optional[str] = None):
        """Mark the operation as finished."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message


class PerformanceMonitor:
    """Monitors and tracks performance metrics for RAG operations."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.active_operations = {}
        self.operation_counts = defaultdict(int)
        self.operation_durations = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.lock = threading.Lock()
        
        # Start system monitoring
        self.system_metrics = []
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_system_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    @contextmanager
    def track_operation(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager to track operation performance."""
        
        metrics = PerformanceMetrics(
            operation=operation,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        operation_id = f"{operation}_{id(metrics)}"
        
        with self.lock:
            self.active_operations[operation_id] = metrics
        
        try:
            yield metrics
            metrics.finish(success=True)
            
        except Exception as e:
            metrics.finish(success=False, error_message=str(e))
            raise
            
        finally:
            with self.lock:
                self.active_operations.pop(operation_id, None)
                self.metrics_history.append(metrics)
                self.operation_counts[operation] += 1
                self.operation_durations[operation].append(metrics.duration or 0)
                
                if not metrics.success:
                    self.error_counts[operation] += 1
            
            # Log the performance metric
            rag_logger.log_performance(
                operation=operation,
                duration=metrics.duration or 0,
                success=metrics.success,
                metadata=metrics.metadata
            )
    
    def get_operation_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics for operations."""
        
        with self.lock:
            if operation:
                # Stats for specific operation
                if operation not in self.operation_counts:
                    return {"error": f"No data for operation: {operation}"}
                
                durations = self.operation_durations[operation]
                return {
                    "operation": operation,
                    "total_calls": self.operation_counts[operation],
                    "total_errors": self.error_counts[operation],
                    "success_rate": (self.operation_counts[operation] - self.error_counts[operation]) / self.operation_counts[operation],
                    "avg_duration": sum(durations) / len(durations) if durations else 0,
                    "min_duration": min(durations) if durations else 0,
                    "max_duration": max(durations) if durations else 0,
                    "recent_calls": len([m for m in self.metrics_history if m.operation == operation and m.end_time and m.end_time > time.time() - 3600])
                }
            else:
                # Overall stats
                total_operations = sum(self.operation_counts.values())
                total_errors = sum(self.error_counts.values())
                
                all_durations = []
                for durations in self.operation_durations.values():
                    all_durations.extend(durations)
                
                return {
                    "total_operations": total_operations,
                    "total_errors": total_errors,
                    "overall_success_rate": (total_operations - total_errors) / total_operations if total_operations > 0 else 0,
                    "avg_duration": sum(all_durations) / len(all_durations) if all_durations else 0,
                    "operations_by_type": dict(self.operation_counts),
                    "errors_by_type": dict(self.error_counts),
                    "active_operations": len(self.active_operations)
                }
    
    def get_recent_metrics(self, minutes: int = 60) -> List[PerformanceMetrics]:
        """Get metrics from the last N minutes."""
        
        cutoff_time = time.time() - (minutes * 60)
        
        with self.lock:
            return [
                metrics for metrics in self.metrics_history
                if metrics.end_time and metrics.end_time > cutoff_time
            ]
    
    def _monitor_system_resources(self):
        """Monitor system resources in the background."""
        
        while self.monitoring_active:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                system_metric = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                }
                
                # Keep only recent system metrics
                self.system_metrics.append(system_metric)
                if len(self.system_metrics) > 720:  # Keep 12 hours at 1-minute intervals
                    self.system_metrics.pop(0)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                rag_logger.log_error(e, {"operation": "system_monitoring"})
                time.sleep(60)
    
    def get_system_metrics(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get system metrics from the last N hours."""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metric for metric in self.system_metrics
            if datetime.fromisoformat(metric["timestamp"]) > cutoff_time
        ]
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds."""
        
        alerts = []
        
        # Check for high error rates
        for operation, total_calls in self.operation_counts.items():
            if total_calls > 10:  # Only check operations with significant volume
                error_rate = self.error_counts[operation] / total_calls
                if error_rate > config.alerts.error_rate_threshold:
                    alerts.append({
                        "type": "high_error_rate",
                        "operation": operation,
                        "error_rate": error_rate,
                        "threshold": config.alerts.error_rate_threshold,
                        "severity": "high" if error_rate > 0.2 else "medium"
                    })
        
        # Check for high latency
        for operation, durations in self.operation_durations.items():
            if durations:
                avg_duration = sum(durations[-10:]) / min(len(durations), 10)  # Recent average
                if avg_duration > config.alerts.latency_threshold:
                    alerts.append({
                        "type": "high_latency",
                        "operation": operation,
                        "avg_duration": avg_duration,
                        "threshold": config.alerts.latency_threshold,
                        "severity": "high" if avg_duration > config.alerts.latency_threshold * 2 else "medium"
                    })
        
        # Check system resources
        if self.system_metrics:
            latest_metrics = self.system_metrics[-1]
            
            if latest_metrics["cpu_percent"] > 80:
                alerts.append({
                    "type": "high_cpu_usage",
                    "cpu_percent": latest_metrics["cpu_percent"],
                    "severity": "high" if latest_metrics["cpu_percent"] > 90 else "medium"
                })
            
            if latest_metrics["memory_percent"] > 80:
                alerts.append({
                    "type": "high_memory_usage",
                    "memory_percent": latest_metrics["memory_percent"],
                    "severity": "high" if latest_metrics["memory_percent"] > 90 else "medium"
                })
        
        return alerts
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        
        with self.lock:
            self.metrics_history.clear()
            self.operation_counts.clear()
            self.operation_durations.clear()
            self.error_counts.clear()
            self.system_metrics.clear()
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)


class RAGPerformanceTracker:
    """Specialized performance tracker for RAG operations."""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
    
    @contextmanager
    def track_query(self, query: str, user_id: Optional[str] = None):
        """Track a complete RAG query."""
        
        metadata = {
            "query_length": len(query),
            "user_id": user_id,
            "query_preview": query[:100]
        }
        
        with self.monitor.track_operation("rag_query", metadata) as metrics:
            yield metrics
    
    @contextmanager
    def track_retrieval(self, query: str, top_k: int):
        """Track document retrieval."""
        
        metadata = {
            "query_length": len(query),
            "top_k": top_k
        }
        
        with self.monitor.track_operation("document_retrieval", metadata) as metrics:
            yield metrics
    
    @contextmanager
    def track_generation(self, context_length: int, model: str):
        """Track response generation."""
        
        metadata = {
            "context_length": context_length,
            "model": model
        }
        
        with self.monitor.track_operation("response_generation", metadata) as metrics:
            yield metrics
    
    @contextmanager
    def track_evaluation(self, evaluator_name: str):
        """Track evaluation process."""
        
        metadata = {
            "evaluator": evaluator_name
        }
        
        with self.monitor.track_operation("evaluation", metadata) as metrics:
            yield metrics
    
    def get_rag_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive RAG performance summary."""
        
        summary = {
            "overall_stats": self.monitor.get_operation_stats(),
            "query_stats": self.monitor.get_operation_stats("rag_query"),
            "retrieval_stats": self.monitor.get_operation_stats("document_retrieval"),
            "generation_stats": self.monitor.get_operation_stats("response_generation"),
            "evaluation_stats": self.monitor.get_operation_stats("evaluation"),
            "system_health": self.monitor.get_system_metrics(hours=1),
            "alerts": self.monitor.get_alerts(),
            "timestamp": datetime.now().isoformat()
        }
        
        return summary


# Global performance tracker instance
performance_tracker = RAGPerformanceTracker()
