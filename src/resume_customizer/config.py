# ABOUTME: Configuration management using Pydantic settings
# ABOUTME: Handles environment variables, defaults, and validation

"""Configuration management for the resume customizer application."""

import functools
from typing import Literal, Optional

from pydantic import Field, field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    # API Key - directly from ANTHROPIC_API_KEY
    claude_api_key: str = Field(
        ...,
        alias='ANTHROPIC_API_KEY',
        description="Anthropic API key for Claude"
    )
    
    # Settings with RESUME_ prefix
    max_iterations: int = Field(
        default=3,
        alias='RESUME_MAX_ITERATIONS',
        description="Maximum number of optimization iterations"
    )
    
    output_format: Literal["markdown", "html", "pdf"] = Field(
        default="markdown",
        alias='RESUME_OUTPUT_FORMAT',
        description="Output format for the customized resume"
    )
    
    preserve_formatting: bool = Field(
        default=True,
        alias='RESUME_PRESERVE_FORMATTING',
        description="Whether to preserve original formatting"
    )
    
    # Claude SDK settings
    model: str = Field(
        default="claude-3-5-sonnet-20241022",
        alias='RESUME_CLAUDE_MODEL',
        description="Claude model to use"
    )
    
    max_tokens: int = Field(
        default=4096,
        alias='RESUME_MAX_TOKENS',
        description="Maximum tokens for Claude response"
    )
    
    temperature: float = Field(
        default=0.7,
        alias='RESUME_TEMPERATURE',
        description="Temperature for Claude responses"
    )
    
    max_retries: int = Field(
        default=3,
        alias='RESUME_MAX_RETRIES',
        description="Maximum number of retries for API calls"
    )
    
    retry_delay: float = Field(
        default=1.0,
        alias='RESUME_RETRY_DELAY',
        description="Initial delay between retries in seconds"
    )
    
    timeout: int = Field(
        default=30,
        alias='RESUME_TIMEOUT',
        description="Timeout for API calls in seconds"
    )
    
    @field_validator('claude_api_key', mode='before')
    def validate_api_key(cls, v: Optional[str]) -> str:
        """Validate that API key is provided and not empty."""
        if v is None:
            raise ValueError("API key is required")
        
        if not isinstance(v, str):
            raise ValueError("API key must be a string")
        
        if not v.strip():
            raise ValueError("API key cannot be empty or whitespace-only")
        
        return v.strip()
    
    @field_validator('max_iterations')
    def validate_max_iterations(cls, v: int) -> int:
        """Validate that max_iterations is positive."""
        if v <= 0:
            raise ValueError("max_iterations must be greater than 0")
        return v
    
    @field_validator('output_format')
    def validate_output_format(cls, v: str) -> str:
        """Validate output format."""
        valid_formats = ["markdown", "html", "pdf"]
        if v not in valid_formats:
            raise ValueError(f"output_format must be one of {valid_formats}")
        return v
    
    @field_validator('temperature')
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is in valid range."""
        if not 0 <= v <= 1:
            raise ValueError("temperature must be between 0 and 1")
        return v
    
    @field_validator('max_tokens')
    def validate_max_tokens(cls, v: int) -> int:
        """Validate max_tokens is positive."""
        if v <= 0:
            raise ValueError("max_tokens must be greater than 0")
        return v
    
    @field_validator('timeout')
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("timeout must be greater than 0")
        return v
    
    @field_validator('retry_delay')
    def validate_retry_delay(cls, v: float) -> float:
        """Validate retry_delay is positive."""
        if v <= 0:
            raise ValueError("retry_delay must be greater than 0")
        return v


@functools.lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Cached settings instance
        
    Note:
        Use get_settings.cache_clear() to clear the cache if needed.
    """
    try:
        return Settings()
    except ValidationError as e:
        # Re-raise with custom message for specific validations
        for error in e.errors():
            if error['loc'] == ('ANTHROPIC_API_KEY',) and error['type'] == 'missing':
                raise ValueError("API key is required") from e
            elif error['loc'] == ('RESUME_OUTPUT_FORMAT',) and error['type'] == 'literal_error':
                raise ValueError("output_format must be one of ['markdown', 'html', 'pdf']") from e
        raise