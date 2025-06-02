"""
Custom exceptions for the Gemini AI client.
"""


class GeminiClientError(Exception):
    """Base exception for Gemini client errors."""
    pass


class ConfigurationError(GeminiClientError):
    """Raised when there's a configuration error."""
    pass


class AuthenticationError(GeminiClientError):
    """Raised when there's an authentication error."""
    pass


class ModelNotAvailableError(GeminiClientError):
    """Raised when no models are available."""
    pass


class ResponseError(GeminiClientError):
    """Raised when there's an error in the response."""
    pass


class RetryExhaustedError(GeminiClientError):
    """Raised when all retry attempts have been exhausted."""
    pass
