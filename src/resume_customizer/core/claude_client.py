# ABOUTME: ClaudeClient wrapper for the Claude Code SDK
# ABOUTME: Handles API communication, retries, and usage tracking

"""Claude Code SDK wrapper for resume customization."""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from anthropic import Anthropic, AsyncAnthropic
from resume_customizer.config import Settings


@dataclass
class ClaudeResponse:
    """Response from Claude API."""
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    timestamp: datetime = None
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ClaudeAPIError(Exception):
    """Base exception for Claude API errors."""
    pass


class ClaudeRateLimitError(ClaudeAPIError):
    """Rate limit error from Claude API."""
    pass


class ClaudeTimeoutError(ClaudeAPIError):
    """Timeout error when calling Claude API."""
    pass


class ClaudeClient:
    """Wrapper around Claude Code SDK for easier testing and usage tracking."""
    
    # Cost per million tokens (as of 2024)
    PRICING = {
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    }
    
    def __init__(self, settings: Settings):
        """
        Initialize Claude client with settings.
        
        Args:
            settings: Application settings with API key and model config
            
        Raises:
            ValueError: If API key is missing
        """
        if not settings.claude_api_key:
            raise ValueError("Claude API key is required")
        
        self.settings = settings
        self.client = AsyncAnthropic(api_key=settings.claude_api_key)
        self.sync_client = Anthropic(api_key=settings.claude_api_key)
        
        # Usage tracking
        self.total_tokens = 0
        self.total_cost = 0.0
    
    async def query(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> ClaudeResponse:
        """
        Send a query to Claude API with retry logic.
        
        Args:
            prompt: The user prompt to send
            system_prompt: Optional system prompt for context
            model: Optional model override
            max_tokens: Optional max tokens override
            temperature: Optional temperature override
            
        Returns:
            ClaudeResponse with the result
            
        Raises:
            ClaudeRateLimitError: If rate limit is hit after retries
            ClaudeTimeoutError: If request times out
            ClaudeAPIError: For other API errors
        """
        model = model or self.settings.model
        max_tokens = max_tokens or self.settings.max_tokens
        temperature = temperature if temperature is not None else self.settings.temperature
        
        # Build messages
        messages = [{"role": "user", "content": prompt}]
        
        # Prepare request kwargs
        request_kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system_prompt:
            request_kwargs["system"] = system_prompt
        
        # Retry logic
        last_error = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                # Make API call with timeout
                response = await asyncio.wait_for(
                    self.client.messages.create(**request_kwargs),
                    timeout=self.settings.timeout
                )
                
                # Parse response
                if response.content is None:
                    raise ClaudeAPIError("Malformed response from Claude API")
                    
                if not response.content:
                    raise ClaudeAPIError("Empty response from Claude API")
                
                if not isinstance(response.content, list) or len(response.content) == 0:
                    raise ClaudeAPIError("Empty response from Claude API")
                
                content = response.content[0].text
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                total_tokens = input_tokens + output_tokens
                
                # Update usage tracking
                self.total_tokens += total_tokens
                cost = self._calculate_cost(input_tokens, output_tokens, model)
                self.total_cost += cost
                
                return ClaudeResponse(
                    content=content,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    model=model
                )
                
            except asyncio.TimeoutError:
                raise ClaudeTimeoutError(
                    f"Request timed out after {self.settings.timeout} seconds"
                )
                
            except Exception as e:
                # Check if it's a rate limit error
                if hasattr(e, 'status_code') and e.status_code == 429:
                    last_error = e
                    if attempt < self.settings.max_retries:
                        # Exponential backoff
                        delay = self.settings.retry_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise ClaudeRateLimitError(
                            f"Rate limit exceeded after {self.settings.max_retries} retries"
                        ) from e
                
                # Other API errors
                if hasattr(e, 'status_code'):
                    raise ClaudeAPIError(
                        f"API error (status {e.status_code}): {str(e)}"
                    ) from e
                else:
                    raise ClaudeAPIError(f"Unexpected error: {str(e)}") from e
        
        # Should not reach here, but just in case
        raise ClaudeAPIError(
            f"Failed after {self.settings.max_retries + 1} attempts"
        )
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """
        Calculate cost based on token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens  
            model: Model name
            
        Returns:
            Cost in dollars
        """
        if model not in self.PRICING:
            # Default to Sonnet pricing if model not found
            model = "claude-3-sonnet-20240229"
        
        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1000) * (pricing["input"] / 1000)
        output_cost = (output_tokens / 1000) * (pricing["output"] / 1000)
        
        return input_cost + output_cost
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current usage statistics.
        
        Returns:
            Dictionary with usage stats
        """
        return {
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "model": self.settings.model,
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_usage_stats(self) -> None:
        """Reset usage statistics."""
        self.total_tokens = 0
        self.total_cost = 0.0