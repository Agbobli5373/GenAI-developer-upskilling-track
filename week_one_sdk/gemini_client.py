"""
Production-ready Gemini AI client with comprehensive error handling and logging.
"""
import time
import logging
from typing import Dict, List, Optional, Generator, Any
from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError

from config import Config
from utils import (
    setup_logger, 
    sanitize_api_key, 
    validate_model_name, 
    format_response_chunk,
    calculate_retry_delay,
    create_error_context
)
from exceptions import (
    ConfigurationError,
    AuthenticationError,
    ModelNotAvailableError,
    ResponseError,
    RetryExhaustedError
)


class GeminiClient:
    """
    Production-ready Gemini AI client with retry logic, error handling, and logging.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        models: Optional[List[str]] = None,
        max_retries: Optional[int] = None,
        initial_retry_delay: Optional[float] = None,
        log_level: str = "INFO",
        log_file: Optional[str] = None
    ):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Gemini API key (uses config default if not provided)
            models: List of models to try (uses config default if not provided)
            max_retries: Maximum retry attempts (uses config default if not provided)
            initial_retry_delay: Initial retry delay (uses config default if not provided)
            log_level: Logging level
            log_file: Optional log file path
        """
        # Set up logging
        self.logger = setup_logger(
            name=self.__class__.__name__,
            level=log_level,
            log_file=log_file
        )
        
        # Initialize configuration
        self._init_config(api_key, models, max_retries, initial_retry_delay)
        
        # Initialize client
        self._init_client()
        
        self.logger.info("GeminiClient initialized successfully")
    
    def _init_config(
        self,
        api_key: Optional[str],
        models: Optional[List[str]],
        max_retries: Optional[int],
        initial_retry_delay: Optional[float]
    ) -> None:
        """Initialize configuration settings."""
        try:
            Config.validate()
        except ValueError as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")
        
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.models = models or Config.DEFAULT_MODELS
        self.max_retries = max_retries or Config.MAX_RETRIES
        self.initial_retry_delay = initial_retry_delay or Config.INITIAL_RETRY_DELAY
        
        if not self.api_key:
            raise AuthenticationError("API key is required")
        
        self.logger.info(f"Configuration loaded. API key: {sanitize_api_key(self.api_key)}")
        self.logger.info(f"Available models: {', '.join(self.models)}")
    
    def _init_client(self) -> None:
        """Initialize the Gemini client."""
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.logger.info("Gemini client initialized")
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Gemini client: {e}")
    
    def _create_content(self, prompt: str, role: str = "user") -> List[types.Content]:
        """
        Create content for the API request.
        
        Args:
            prompt: The prompt text
            role: The role (default: "user")
            
        Returns:
            List of Content objects
        """
        return [
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=prompt)]
            )
        ]
    
    def _create_generation_config(
        self,
        response_mime_type: str = Config.DEFAULT_RESPONSE_MIME_TYPE,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> types.GenerateContentConfig:
        """
        Create generation configuration.
        
        Args:
            response_mime_type: MIME type for response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            GenerateContentConfig object
        """
        config_params = {"response_mime_type": response_mime_type}
        
        if temperature is not None:
            config_params["temperature"] = temperature
        
        if max_tokens is not None:
            config_params["max_output_tokens"] = max_tokens
        
        return types.GenerateContentConfig(**config_params)
    
    def _try_model_with_retry(
        self,
        model: str,
        contents: List[types.Content],
        config: types.GenerateContentConfig
    ) -> Generator[str, None, None]:
        """
        Try a specific model with retry logic.
        
        Args:
            model: Model name to try
            contents: Content for the request
            config: Generation configuration
            
        Yields:
            Response chunks as strings
            
        Raises:
            RetryExhaustedError: If all retries are exhausted
        """
        retry_delay = self.initial_retry_delay
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Attempting {model} (attempt {attempt + 1}/{self.max_retries})")
                
                response_stream = self.client.models.generate_content_stream(
                    model=model,
                    contents=contents,
                    config=config
                )
                
                first_chunk = True
                for chunk in response_stream:
                    if first_chunk:
                        self.logger.info(f"Successfully connected to {model}")
                        yield format_response_chunk(chunk, model, is_first_chunk=True)
                        first_chunk = False
                    else:
                        yield chunk.text
                
                self.logger.info(f"Successfully completed request with {model}")
                return  # Success, exit retry loop
                
            except ServerError as e:
                error_context = create_error_context(e, model, attempt + 1)
                
                if e.status_code == 503 and attempt < self.max_retries - 1:
                    self.logger.warning(
                        f"Server overloaded for {model} (attempt {attempt + 1}). "
                        f"Retrying in {retry_delay:.1f} seconds..."
                    )
                    time.sleep(retry_delay)
                    retry_delay = calculate_retry_delay(
                        attempt + 1, 
                        self.initial_retry_delay, 
                        Config.BACKOFF_MULTIPLIER, 
                        Config.MAX_RETRY_DELAY
                    )
                else:
                    self.logger.error(f"Failed with {model}: {error_context}")
                    raise RetryExhaustedError(
                        f"Model {model} failed after {self.max_retries} attempts: {e}"
                    )
                    
            except Exception as e:
                error_context = create_error_context(e, model, attempt + 1)
                self.logger.error(f"Unexpected error with {model}: {error_context}")
                raise ResponseError(f"Unexpected error with model {model}: {e}")
    
    def generate_response(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_mime_type: str = Config.DEFAULT_RESPONSE_MIME_TYPE
    ) -> str:
        """
        Generate a response using the specified prompt.
        
        Args:
            prompt: The input prompt
            models: List of models to try (uses instance default if not provided)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_mime_type: MIME type for response
            
        Returns:
            Generated response as string
            
        Raises:
            ModelNotAvailableError: If no models are available
            ResponseError: If response generation fails
        """
        models_to_try = models or self.models
        
        if not models_to_try:
            raise ModelNotAvailableError("No models available")
        
        self.logger.info(f"Generating response for prompt: {prompt[:100]}...")
        
        contents = self._create_content(prompt)
        config = self._create_generation_config(
            response_mime_type=response_mime_type,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        for model in models_to_try:
            if not validate_model_name(model, self.models):
                self.logger.warning(f"Skipping invalid model: {model}")
                continue
            
            try:
                response_parts = []
                for chunk in self._try_model_with_retry(model, contents, config):
                    response_parts.append(chunk)
                    print(chunk, end="", flush=True)
                
                response = "".join(response_parts)
                self.logger.info(f"Successfully generated response using {model}")
                return response
                
            except (RetryExhaustedError, ResponseError) as e:
                self.logger.warning(f"Model {model} failed: {e}")
                continue
        
        raise ModelNotAvailableError("All models failed or are unavailable")
    
    def generate_response_stream(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_mime_type: str = Config.DEFAULT_RESPONSE_MIME_TYPE
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response using the specified prompt.
        
        Args:
            prompt: The input prompt
            models: List of models to try (uses instance default if not provided)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_mime_type: MIME type for response
            
        Yields:
            Response chunks as strings
            
        Raises:
            ModelNotAvailableError: If no models are available
            ResponseError: If response generation fails
        """
        models_to_try = models or self.models
        
        if not models_to_try:
            raise ModelNotAvailableError("No models available")
        
        self.logger.info(f"Generating streaming response for prompt: {prompt[:100]}...")
        
        contents = self._create_content(prompt)
        config = self._create_generation_config(
            response_mime_type=response_mime_type,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        for model in models_to_try:
            if not validate_model_name(model, self.models):
                self.logger.warning(f"Skipping invalid model: {model}")
                continue
            
            try:
                for chunk in self._try_model_with_retry(model, contents, config):
                    yield chunk
                
                self.logger.info(f"Successfully completed streaming response using {model}")
                return
                
            except (RetryExhaustedError, ResponseError) as e:
                self.logger.warning(f"Model {model} failed: {e}")
                continue
        
        raise ModelNotAvailableError("All models failed or are unavailable")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the client and API connectivity.
        
        Returns:
            Dictionary with health check results
        """
        health_status = {
            "client_initialized": bool(self.client),
            "api_key_configured": bool(self.api_key),
            "models_available": len(self.models),
            "models": self.models,
            "timestamp": time.time()
        }
        
        # Try a simple API call
        try:
            test_response = self.generate_response(
                prompt="Hello", 
                models=[self.models[0]] if self.models else []
            )
            health_status["api_connectivity"] = True
            health_status["test_response_length"] = len(test_response)
        except Exception as e:
            health_status["api_connectivity"] = False
            health_status["api_error"] = str(e)
        
        self.logger.info(f"Health check completed: {health_status}")
        return health_status
