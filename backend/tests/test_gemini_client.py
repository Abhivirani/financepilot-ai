"""
Unit tests for the GeminiClient integration.
Mocking google.genai so no real API calls are made during tests.
"""

import pytest
import sys
from unittest.mock import AsyncMock, patch, MagicMock

# Mock google.genai globally to avoid ModuleNotFoundError when importing or patching
mock_google_genai = MagicMock()
sys.modules['google.genai'] = mock_google_genai
sys.modules['google'] = MagicMock()
sys.modules['google'].genai = mock_google_genai

class MockAPIError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        
    def __str__(self):
        return self.message

mock_errors = MagicMock()
mock_errors.APIError = MockAPIError
sys.modules['google.genai.errors'] = mock_errors
mock_google_genai.errors = mock_errors
sys.modules['google.genai.types'] = MagicMock()
mock_google_genai.types = sys.modules['google.genai.types']

from backend.app.ai.llm_client import GeminiClient, LLMResponse
from backend.app.ai.exceptions import (
    LLMAuthenticationError,
    LLMQuotaExceededError,
    LLMRateLimitError,
    LLMNetworkError,
    LLMProviderError
)

class MockUsageMetadata:
    prompt_token_count = 10
    candidates_token_count = 20

class MockGenerateContentResponse:
    text = "OK, this is a mocked response."
    usage_metadata = MockUsageMetadata()

@pytest.fixture
def gemini_client():
    return GeminiClient(
        api_key="test-key",
        model="gemini-2.5-pro",
        default_max_tokens=1500,
        default_temperature=0.2,
        timeout=30
    )

@pytest.fixture
def mock_genai_client():
    mock_instance = MagicMock()
    mock_instance.aio.models.generate_content = AsyncMock()
    
    with patch("backend.app.ai.llm_client.GeminiClient._get_client", return_value=mock_instance):
        yield mock_instance

@pytest.mark.asyncio
async def test_gemini_generate_success(gemini_client, mock_genai_client):
    mock_genai_client.aio.models.generate_content.return_value = MockGenerateContentResponse()
    
    response = await gemini_client.generate(
        system="System",
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    assert isinstance(response, LLMResponse)
    assert response.content == "OK, this is a mocked response."
    assert response.input_tokens == 10
    assert response.output_tokens == 20
    assert response.stop_reason == "stop"

@pytest.mark.asyncio
async def test_gemini_missing_api_key():
    client = GeminiClient(
        api_key="",
        model="gemini-2.5-pro",
        default_max_tokens=1500,
        default_temperature=0.2,
        timeout=30
    )
    
    with pytest.raises(LLMAuthenticationError, match="not configured"):
        await client.generate(system="", messages=[])

@pytest.mark.asyncio
async def test_gemini_api_error_auth(gemini_client, mock_genai_client):
    from google.genai import errors
    mock_genai_client.aio.models.generate_content.side_effect = errors.APIError("403 Forbidden")
    
    with pytest.raises(LLMAuthenticationError):
        await gemini_client.generate(system="", messages=[{"role": "user", "content": "hi"}])

@pytest.mark.asyncio
async def test_gemini_api_error_rate_limit(gemini_client, mock_genai_client):
    from google.genai import errors
    mock_genai_client.aio.models.generate_content.side_effect = errors.APIError("429 Too Many Requests")
    
    with pytest.raises(LLMRateLimitError):
        await gemini_client.generate(system="", messages=[{"role": "user", "content": "hi"}])

@pytest.mark.asyncio
async def test_gemini_api_error_quota(gemini_client, mock_genai_client):
    from google.genai import errors
    mock_genai_client.aio.models.generate_content.side_effect = errors.APIError("429 Quota Exceeded")
    
    with pytest.raises(LLMQuotaExceededError):
        await gemini_client.generate(system="", messages=[{"role": "user", "content": "hi"}])

@pytest.mark.asyncio
async def test_gemini_test_connection_success(gemini_client, mock_genai_client):
    mock_genai_client.aio.models.generate_content.return_value = MockGenerateContentResponse()
    
    is_ok = await gemini_client.test_connection()
    assert is_ok is True

@pytest.mark.asyncio
async def test_gemini_test_connection_failure(gemini_client, mock_genai_client):
    from google.genai import errors
    mock_genai_client.aio.models.generate_content.side_effect = errors.APIError("500 Internal Server Error")
    
    is_ok = await gemini_client.test_connection()
    assert is_ok is False
