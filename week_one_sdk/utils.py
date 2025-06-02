"""
Utility functions for the Gemini AI client.
"""
import time
import logging
import functools
from typing import Any, Callable, Dict, List, Optional, Union
from google.genai.errors import ServerError, APIError


def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with the specified configuration.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    exceptions: tuple = (ServerError, APIError)
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff
        exceptions: Tuple of exception types to catch and retry
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(func.__module__)
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )
                    
                    time.sleep(delay)
                    delay = min(delay * backoff_multiplier, max_delay)
                    
                except Exception as e:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                    raise
                    
            return None  # This should never be reached
            
        return wrapper
    return decorator


def sanitize_api_key(api_key: str, visible_chars: int = 8) -> str:
    """
    Sanitize API key for logging purposes.
    
    Args:
        api_key: The API key to sanitize
        visible_chars: Number of characters to show at the beginning and end
        
    Returns:
        Sanitized API key string
    """
    if not api_key:
        return "None"
    
    if len(api_key) <= visible_chars * 2:
        return "*" * len(api_key)
    
    prefix = api_key[:visible_chars//2]
    suffix = api_key[-visible_chars//2:]
    middle = "*" * (len(api_key) - visible_chars)
    
    return f"{prefix}{middle}{suffix}"


def validate_model_name(model: str, available_models: List[str]) -> bool:
    """
    Validate if a model name is in the list of available models.
    
    Args:
        model: Model name to validate
        available_models: List of available model names
        
    Returns:
        True if model is valid, False otherwise
    """
    return model in available_models


def format_response_chunk(chunk: Any, model: str, is_first_chunk: bool = False) -> str:
    """
    Format a response chunk for display.
    
    Args:
        chunk: Response chunk from the API
        model: Model name that generated the response
        is_first_chunk: Whether this is the first chunk
        
    Returns:
        Formatted string
    """
    if is_first_chunk:
        return f"\n--- Response from {model} ---\n{chunk.text}"
    return chunk.text


def calculate_retry_delay(attempt: int, initial_delay: float, multiplier: float, max_delay: float) -> float:
    """
    Calculate the next retry delay using exponential backoff.
    
    Args:
        attempt: Current attempt number (0-based)
        initial_delay: Initial delay in seconds
        multiplier: Backoff multiplier
        max_delay: Maximum delay in seconds
        
    Returns:
        Calculated delay in seconds
    """
    delay = initial_delay * (multiplier ** attempt)
    return min(delay, max_delay)


def create_error_context(error: Exception, model: str, attempt: int) -> Dict[str, Any]:
    """
    Create context information for error handling.
    
    Args:
        error: The exception that occurred
        model: Model name being used
        attempt: Current attempt number
        
    Returns:
        Dictionary with error context
    """
    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "model": model,
        "attempt": attempt,
        "timestamp": time.time()
    }
