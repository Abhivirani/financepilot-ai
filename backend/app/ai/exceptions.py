class AIError(Exception):
    """Base exception for all AI module errors."""
    pass

class LLMProviderError(AIError):
    """Base exception for LLM provider errors."""
    pass

class LLMAuthenticationError(LLMProviderError):
    """Raised when the API key is invalid or missing."""
    pass

class LLMQuotaExceededError(LLMProviderError):
    """Raised when the provider quota is exceeded."""
    pass

class LLMRateLimitError(LLMProviderError):
    """Raised when the provider rate limits requests."""
    pass

class LLMNetworkError(LLMProviderError):
    """Raised when there is a network timeout or connection error."""
    pass
