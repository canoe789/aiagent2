"""
Custom exceptions for Project HELIX v2.0
Implements error classification for retry logic
"""

from typing import Optional


class HELIXError(Exception):
    """Base exception for all HELIX errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RetryableError(HELIXError):
    """
    Errors that can be retried
    Examples: Network timeout, temporary resource unavailable
    """
    pass


class NonRetryableError(HELIXError):
    """
    Errors that should not be retried
    Examples: Validation errors, business logic violations
    """
    pass


# Specific error types
class AIModelError(RetryableError):
    """AI model invocation errors (timeout, rate limit, etc.)"""
    pass


class NetworkError(RetryableError):
    """Network-related errors"""
    pass


class ResourceUnavailableError(RetryableError):
    """Temporary resource unavailability"""
    pass


class ValidationError(NonRetryableError):
    """Data validation errors"""
    pass


class SchemaValidationError(NonRetryableError):
    """Schema validation errors"""
    pass


class BusinessLogicError(NonRetryableError):
    """Business logic violations"""
    pass


class AuthenticationError(NonRetryableError):
    """Authentication/Authorization errors"""
    pass


def classify_error(error: Exception) -> bool:
    """
    Classify if an error is retryable
    
    Args:
        error: The exception to classify
        
    Returns:
        bool: True if the error is retryable, False otherwise
    """
    # Direct classification
    if isinstance(error, RetryableError):
        return True
    if isinstance(error, NonRetryableError):
        return False
    
    # Heuristic classification based on error message
    error_msg = str(error).lower()
    
    retryable_keywords = [
        "timeout", "timed out",
        "connection", "network",
        "temporarily", "temporary",
        "rate limit", "too many requests",
        "service unavailable", "503",
        "gateway timeout", "504"
    ]
    
    non_retryable_keywords = [
        "validation", "invalid",
        "unauthorized", "forbidden",
        "not found", "404",
        "bad request", "400",
        "schema", "type error"
    ]
    
    # Check for retryable patterns
    for keyword in retryable_keywords:
        if keyword in error_msg:
            return True
    
    # Check for non-retryable patterns
    for keyword in non_retryable_keywords:
        if keyword in error_msg:
            return False
    
    # Default to retryable for unknown errors
    return True