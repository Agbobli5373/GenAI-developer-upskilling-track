"""
Configuration management for RAG Monitoring and Evaluation System.
"""

import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GeminiConfig(BaseModel):
    """Google Gemini API configuration."""
    
    api_key: str
    model: str = "gemini-1.5-flash"
    temperature: float = 0.1
    max_tokens: int = 1000
    
    def __init__(self):
        super().__init__(
            api_key=os.getenv("GOOGLE_API_KEY", ""),
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            temperature=float(os.getenv("TEMPERATURE", 0.1)),
            max_tokens=int(os.getenv("MAX_TOKENS", 1000))
        )


class LangSmithConfig(BaseModel):
    """LangSmith configuration for tracking and evaluation."""
    
    tracing_enabled: bool = True
    endpoint: str = "https://api.smith.langchain.com"
    api_key: str
    project: str = "rag-monitoring-week10"
    
    def __init__(self):
        super().__init__(
            tracing_enabled=os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true",
            endpoint=os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
            api_key=os.getenv("LANGCHAIN_API_KEY", ""),
            project=os.getenv("LANGCHAIN_PROJECT", "rag-monitoring-week10")
        )


class DatabaseConfig(BaseModel):
    """Database configuration."""
    
    chroma_db_path: str = "./data/chroma_db"
    collection_name: str = "rag_documents"
    
    def __init__(self):
        super().__init__(
            chroma_db_path=os.getenv("CHROMA_DB_PATH", "./data/chroma_db"),
            collection_name=os.getenv("VECTOR_DB_COLLECTION", "rag_documents")
        )


class MonitoringConfig(BaseModel):
    """Monitoring and logging configuration."""
    
    log_level: str = "INFO"
    log_format: str = "json"
    metrics_port: int = 8000
    prometheus_port: int = 8001
    
    def __init__(self):
        super().__init__(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            metrics_port=int(os.getenv("METRICS_PORT", 8000)),
            prometheus_port=int(os.getenv("PROMETHEUS_PORT", 8001))
        )


class DashboardConfig(BaseModel):
    """Dashboard configuration."""
    
    port: int = 8501
    host: str = "localhost"
    
    def __init__(self):
        super().__init__(
            port=int(os.getenv("DASHBOARD_PORT", 8501)),
            host=os.getenv("DASHBOARD_HOST", "localhost")
        )


class EvaluationConfig(BaseModel):
    """Evaluation pipeline configuration."""
    
    batch_size: int = 10
    timeout: int = 300
    parallel_workers: int = 4
    
    def __init__(self):
        super().__init__(
            batch_size=int(os.getenv("EVAL_BATCH_SIZE", 10)),
            timeout=int(os.getenv("EVAL_TIMEOUT", 300)),
            parallel_workers=int(os.getenv("EVAL_PARALLEL_WORKERS", 4))
        )


class DataConfig(BaseModel):
    """Data paths configuration."""
    
    data_path: str = "./data"
    datasets_path: str = "./data/datasets"
    logs_path: str = "./data/logs"
    
    def __init__(self):
        super().__init__(
            data_path=os.getenv("DATA_PATH", "./data"),
            datasets_path=os.getenv("DATASETS_PATH", "./data/datasets"),
            logs_path=os.getenv("LOGS_PATH", "./data/logs")
        )


class RetrievalConfig(BaseModel):
    """Retrieval system configuration."""
    
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    def __init__(self):
        super().__init__(
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            top_k=int(os.getenv("RETRIEVAL_TOP_K", 5)),
            chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 200))
        )


class AlertConfig(BaseModel):
    """Alert configuration."""
    
    email: Optional[str] = None
    latency_threshold: float = 5.0
    error_rate_threshold: float = 0.1
    
    def __init__(self):
        super().__init__(
            email=os.getenv("ALERT_EMAIL"),
            latency_threshold=float(os.getenv("ALERT_THRESHOLD_LATENCY", 5.0)),
            error_rate_threshold=float(os.getenv("ALERT_THRESHOLD_ERROR_RATE", 0.1))
        )


class Config:
    """Main configuration class that aggregates all configurations."""
    
    def __init__(self):
        self.gemini = GeminiConfig()
        self.langsmith = LangSmithConfig()
        self.database = DatabaseConfig()
        self.monitoring = MonitoringConfig()
        self.dashboard = DashboardConfig()
        self.evaluation = EvaluationConfig()
        self.data = DataConfig()
        self.retrieval = RetrievalConfig()
        self.alerts = AlertConfig()
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.data.data_path,
            self.data.datasets_path,
            self.data.logs_path,
            self.database.chroma_db_path,
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Global configuration instance
config = Config()
