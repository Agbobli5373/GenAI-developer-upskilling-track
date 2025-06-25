from typing import List, Union, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True
    )
    
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DEBUG: bool = False
    
    # CORS - Use a simple string field without complex parsing
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Ensure CORS origins is always a string"""
        if isinstance(v, str):
            return v
        elif isinstance(v, list):
            return ",".join(v)
        return str(v)

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]
        return []

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # Database  
    DATABASE_URL: str = ""
    
    # Google Gemini
    GOOGLE_API_KEY: str = ""
    
    # JWT Settings
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Vector Search Settings
    EMBEDDING_DIMENSION: int = 768  # Gemini embedding dimension
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.7
    MAX_SEARCH_RESULTS: int = 20
    MAX_RAG_CONTEXT_CHUNKS: int = 5

    # File upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt"]
    
    # Storage
    UPLOAD_DIR: Path = Path("uploads")


settings = Settings()
