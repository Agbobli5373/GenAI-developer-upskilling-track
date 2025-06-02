"""
Configuration settings for the Gemini AI client.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for Gemini AI client."""
    
    # API Configuration
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    
    # Model Configuration
    DEFAULT_MODELS: List[str] = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    
    # Retry Configuration
    MAX_RETRIES: int = 3
    INITIAL_RETRY_DELAY: int = 2  # seconds
    MAX_RETRY_DELAY: int = 60  # seconds
    BACKOFF_MULTIPLIER: float = 2.0
    
    # Response Configuration
    DEFAULT_RESPONSE_MIME_TYPE: str = "text/plain"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 1024
    
    # Logging Configuration
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "gemini_client.log"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        if not cls.DEFAULT_MODELS:
            raise ValueError("At least one model must be configured")
        
        return True
