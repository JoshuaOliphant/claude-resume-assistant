# ABOUTME: Test suite for the ClaudeClient wrapper class
# ABOUTME: Verifies SDK initialization, API calls, and error handling

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import time

from resume_customizer.core.claude_client import (
    ClaudeClient, ClaudeAPIError, ClaudeRateLimitError,
    ClaudeTimeoutError, ClaudeResponse
)
from resume_customizer.config import Settings


class TestClaudeClient:
    """Test suite for ClaudeClient class."""
    
    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings(
            claude_api_key="test-api-key-123",
            max_retries=3,
            retry_delay=0.1,
            timeout=30
        )
    
    @pytest.fixture
    def mock_anthropic(self):
        """Mock the Anthropic SDK."""
        with patch('resume_customizer.core.claude_client.AsyncAnthropic') as mock_async:
            with patch('resume_customizer.core.claude_client.Anthropic') as mock_sync:
                yield mock_async, mock_sync
    
    def test_initialization_with_api_key(self, settings, mock_anthropic):
        """Test client initialization with API key."""
        mock_async, mock_sync = mock_anthropic
        client = ClaudeClient(settings)
        
        # Verify SDK was initialized with correct API key
        mock_async.assert_called_once_with(api_key=settings.claude_api_key)
        mock_sync.assert_called_once_with(api_key=settings.claude_api_key)
        assert client.settings == settings
        assert client.total_tokens == 0
        assert client.total_cost == 0.0
    
    def test_initialization_without_api_key(self, mock_anthropic):
        """Test initialization fails without API key."""
        # Create a mock settings object with empty API key
        mock_settings = Mock()
        mock_settings.claude_api_key = ""
        
        with pytest.raises(ValueError, match="Claude API key is required"):
            ClaudeClient(mock_settings)
    
    @pytest.mark.asyncio
    async def test_query_success(self, settings, mock_anthropic):
        """Test successful API query."""
        mock_async, mock_sync = mock_anthropic
        
        # Setup mock response
        mock_response = Mock()
        mock_response.content = [Mock(text="This is the customized resume.")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make query
        response = await client.query("Test prompt")
        
        # Verify response
        assert response.content == "This is the customized resume."
        assert response.input_tokens == 100
        assert response.output_tokens == 50
        assert response.total_tokens == 150
        assert client.total_tokens == 150
        
        # Verify API call
        mock_client_instance.messages.create.assert_called_once_with(
            model=settings.model,
            messages=[{"role": "user", "content": "Test prompt"}],
            max_tokens=settings.max_tokens,
            temperature=settings.temperature
        )
    
    @pytest.mark.asyncio
    async def test_query_with_system_prompt(self, settings, mock_anthropic):
        """Test query with system prompt."""
        mock_async, mock_sync = mock_anthropic
        
        mock_response = Mock()
        mock_response.content = [Mock(text="Response with system context.")]
        mock_response.usage = Mock(input_tokens=120, output_tokens=60)
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make query with system prompt
        response = await client.query(
            "User prompt",
            system_prompt="You are a helpful assistant."
        )
        
        # Verify API call includes system prompt
        mock_client_instance.messages.create.assert_called_once_with(
            model=settings.model,
            messages=[{"role": "user", "content": "User prompt"}],
            system="You are a helpful assistant.",
            max_tokens=settings.max_tokens,
            temperature=settings.temperature
        )
    
    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self, settings, mock_anthropic):
        """Test retry logic on rate limit errors."""
        mock_async, mock_sync = mock_anthropic
        
        # Setup mock to fail twice then succeed
        mock_response = Mock()
        mock_response.content = [Mock(text="Success after retries.")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        
        # Create a side effect that fails twice then succeeds
        rate_limit_error = Exception("Rate limit exceeded")
        rate_limit_error.status_code = 429
        
        mock_client_instance.messages.create = AsyncMock(
            side_effect=[rate_limit_error, rate_limit_error, mock_response]
        )
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make query - should retry and eventually succeed
        start_time = time.time()
        response = await client.query("Test prompt")
        elapsed_time = time.time() - start_time
        
        # Verify response
        assert response.content == "Success after retries."
        assert mock_client_instance.messages.create.call_count == 3
        # Verify delays were applied (should be at least 0.2s for two retries)
        assert elapsed_time >= 0.2
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, settings, mock_anthropic):
        """Test that max retries limit is respected."""
        mock_async, mock_sync = mock_anthropic
        
        # Setup mock to always fail
        rate_limit_error = Exception("Rate limit exceeded")
        rate_limit_error.status_code = 429
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(side_effect=rate_limit_error)
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make query - should fail after max retries
        with pytest.raises(ClaudeRateLimitError):
            await client.query("Test prompt")
        
        # Verify retry count
        assert mock_client_instance.messages.create.call_count == settings.max_retries + 1
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, settings, mock_anthropic):
        """Test timeout handling."""
        mock_async, mock_sync = mock_anthropic
        
        # Setup mock to timeout
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(
            side_effect=asyncio.TimeoutError()
        )
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make query - should raise timeout error
        with pytest.raises(ClaudeTimeoutError):
            await client.query("Test prompt")
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, settings, mock_anthropic):
        """Test handling of general API errors."""
        mock_async, mock_sync = mock_anthropic
        
        # Setup mock to raise API error
        api_error = Exception("Invalid request")
        api_error.status_code = 400
        api_error.message = "Invalid request format"
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(side_effect=api_error)
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make query - should raise API error
        with pytest.raises(ClaudeAPIError) as exc_info:
            await client.query("Test prompt")
        
        assert "Invalid request" in str(exc_info.value)
    
    def test_cost_calculation(self, settings, mock_anthropic):
        """Test token cost calculation."""
        mock_async, mock_sync = mock_anthropic
        client = ClaudeClient(settings)
        
        # Test cost calculation for different models
        cost = client._calculate_cost(1000, 500, "claude-3-opus-20240229")
        assert cost == pytest.approx(0.0525)  # $15/$75 per million tokens
        
        cost = client._calculate_cost(1000, 500, "claude-3-sonnet-20240229")
        assert cost == pytest.approx(0.0105)  # $3/$15 per million tokens
        
        cost = client._calculate_cost(1000, 500, "claude-3-haiku-20240307")
        assert cost == pytest.approx(0.000875)  # $0.25/$1.25 per million tokens
    
    @pytest.mark.asyncio
    async def test_token_and_cost_tracking(self, settings, mock_anthropic):
        """Test cumulative token and cost tracking."""
        mock_async, mock_sync = mock_anthropic
        
        # Setup mock responses
        mock_response1 = Mock()
        mock_response1.content = [Mock(text="First response.")]
        mock_response1.usage = Mock(input_tokens=100, output_tokens=50)
        
        mock_response2 = Mock()
        mock_response2.content = [Mock(text="Second response.")]
        mock_response2.usage = Mock(input_tokens=150, output_tokens=75)
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(
            side_effect=[mock_response1, mock_response2]
        )
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make first query
        await client.query("First prompt")
        assert client.total_tokens == 150
        assert client.total_cost > 0
        
        # Make second query
        await client.query("Second prompt")
        assert client.total_tokens == 375  # 150 + 225
        assert client.total_cost > 0
    
    def test_get_usage_stats(self, settings, mock_anthropic):
        """Test usage statistics retrieval."""
        mock_async, mock_sync = mock_anthropic
        client = ClaudeClient(settings)
        client.total_tokens = 1000
        client.total_cost = 0.015
        
        stats = client.get_usage_stats()
        
        assert stats["total_tokens"] == 1000
        assert stats["total_cost"] == 0.015
        assert stats["model"] == settings.model
        assert "timestamp" in stats
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self, settings, mock_anthropic):
        """Test handling of empty responses."""
        mock_async, mock_sync = mock_anthropic
        
        # Setup mock with empty response
        mock_response = Mock()
        mock_response.content = []
        mock_response.usage = Mock(input_tokens=100, output_tokens=0)
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make query - should handle empty response
        with pytest.raises(ClaudeAPIError, match="Empty response"):
            await client.query("Test prompt")
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, settings, mock_anthropic):
        """Test handling of malformed responses."""
        mock_async, mock_sync = mock_anthropic
        
        # Setup mock with malformed response
        mock_response = Mock()
        mock_response.content = None
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make query - should handle malformed response
        with pytest.raises(ClaudeAPIError, match="Malformed response"):
            await client.query("Test prompt")
    
    @pytest.mark.asyncio
    async def test_concurrent_queries(self, settings, mock_anthropic):
        """Test handling of concurrent queries."""
        mock_async, mock_sync = mock_anthropic
        
        # Setup mock responses
        mock_response = Mock()
        mock_response.content = [Mock(text="Concurrent response.")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Make concurrent queries
        tasks = [client.query(f"Prompt {i}") for i in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # Verify all queries completed
        assert len(responses) == 5
        assert all(r.content == "Concurrent response." for r in responses)
        assert client.total_tokens == 750  # 150 tokens * 5 queries
    
    def test_reset_usage_stats(self, settings, mock_anthropic):
        """Test resetting usage statistics."""
        mock_async, mock_sync = mock_anthropic
        client = ClaudeClient(settings)
        client.total_tokens = 1000
        client.total_cost = 0.015
        
        client.reset_usage_stats()
        
        assert client.total_tokens == 0
        assert client.total_cost == 0.0
    
    @pytest.mark.asyncio
    async def test_custom_model_override(self, settings, mock_anthropic):
        """Test using a custom model for specific queries."""
        mock_async, mock_sync = mock_anthropic
        
        mock_response = Mock()
        mock_response.content = [Mock(text="Custom model response.")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        
        mock_client_instance = Mock()
        mock_client_instance.messages = Mock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_async.return_value = mock_client_instance
        
        client = ClaudeClient(settings)
        
        # Query with custom model
        response = await client.query(
            "Test prompt",
            model="claude-3-haiku-20240307"
        )
        
        # Verify custom model was used
        mock_client_instance.messages.create.assert_called_once()
        call_kwargs = mock_client_instance.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-3-haiku-20240307"