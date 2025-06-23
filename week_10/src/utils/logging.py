"""
Logging utilities for RAG monitoring system.
"""

import json
import logging
import structlog
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from ..utils.config import config


class RAGLogger:
    """Custom logger for RAG system with structured logging."""
    
    def __init__(self, name: str = "rag_monitor"):
        self.name = name
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> structlog.stdlib.BoundLogger:
        """Set up structured logger with appropriate configuration."""
        
        # Configure standard library logging
        logging.basicConfig(
            level=getattr(logging, config.monitoring.log_level),
            format="%(message)s",
        )
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer() if config.monitoring.log_format == "json"
                else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        return structlog.get_logger(self.name)
    
    def log_query(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """Log user query with metadata."""
        self.logger.info(
            "user_query",
            query=query,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_retrieval(
        self,
        query: str,
        retrieved_docs: list,
        retrieval_time: float,
        similarity_scores: Optional[list] = None,
        **kwargs
    ):
        """Log document retrieval results."""
        self.logger.info(
            "document_retrieval",
            query=query,
            num_docs_retrieved=len(retrieved_docs),
            retrieval_time_seconds=retrieval_time,
            similarity_scores=similarity_scores,
            doc_ids=[doc.get('id', 'unknown') for doc in retrieved_docs],
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_generation(
        self,
        query: str,
        response: str,
        generation_time: float,
        model_used: str,
        context_length: int,
        **kwargs
    ):
        """Log response generation details."""
        self.logger.info(
            "response_generation",
            query=query,
            response_length=len(response),
            generation_time_seconds=generation_time,
            model_used=model_used,
            context_length=context_length,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_evaluation(
        self,
        query: str,
        response: str,
        metrics: Dict[str, float],
        evaluator: str,
        **kwargs
    ):
        """Log evaluation results."""
        self.logger.info(
            "evaluation_result",
            query=query,
            response_preview=response[:100] + "..." if len(response) > 100 else response,
            metrics=metrics,
            evaluator=evaluator,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        **kwargs
    ):
        """Log errors with context."""
        self.logger.error(
            "system_error",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log performance metrics."""
        self.logger.info(
            "performance_metric",
            operation=operation,
            duration_seconds=duration,
            success=success,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat(),
            **kwargs
        )


class QueryLogger:
    """Specialized logger for query tracking and analysis."""
    
    def __init__(self):
        self.logger = RAGLogger("query_tracker")
        self.log_file = Path(config.data.logs_path) / "queries.jsonl"
    
    def log_complete_interaction(
        self,
        query: str,
        response: str,
        retrieved_contexts: list,
        metrics: Dict[str, float],
        timings: Dict[str, float],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """Log complete RAG interaction with all details."""
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "retrieved_contexts": retrieved_contexts,
            "metrics": metrics,
            "timings": timings,
            "user_id": user_id,
            "session_id": session_id,
        }
        
        # Log to structured logger
        self.logger.logger.info("complete_interaction", **interaction_data)
        
        # Also save to JSONL file for easy analysis
        self._save_to_jsonl(interaction_data)
    
    def _save_to_jsonl(self, data: Dict[str, Any]):
        """Save interaction data to JSONL file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.log_error(e, {"context": "saving_to_jsonl"})


# Global logger instances
rag_logger = RAGLogger()
query_logger = QueryLogger()
