# ABOUTME: Unit tests for the configuration/settings module
# ABOUTME: Tests environment variable loading, defaults, and validation

import os
import pytest
from unittest.mock import patch
from pathlib import Path


class TestSettings:
    """Test suite for Settings configuration class."""
    
    @pytest.fixture
    def clean_env(self):
        """Ensure a clean environment for each test."""
        # Store original env vars
        original_env = {}
        env_vars = ['ANTHROPIC_API_KEY', 'RESUME_MAX_ITERATIONS', 
                   'RESUME_OUTPUT_FORMAT', 'RESUME_PRESERVE_FORMATTING']
        
        for var in env_vars:
            if var in os.environ:
                original_env[var] = os.environ[var]
                del os.environ[var]
        
        yield
        
        # Restore original env vars
        for var, value in original_env.items():
            os.environ[var] = value
    
    def test_settings_loads_api_key_from_env(self, clean_env):
        """Test that Settings loads ANTHROPIC_API_KEY from environment."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key-123'
        
        from resume_customizer.config import Settings
        settings = Settings()
        
        assert settings.claude_api_key == 'test-api-key-123'
    
    def test_settings_default_values(self, clean_env):
        """Test that Settings has correct default values."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key'
        
        from resume_customizer.config import Settings
        settings = Settings()
        
        assert settings.max_iterations == 3
        assert settings.output_format == "markdown"
        assert settings.preserve_formatting is True
    
    def test_settings_validates_empty_api_key(self, clean_env):
        """Test that Settings validates API key is not empty."""
        os.environ['ANTHROPIC_API_KEY'] = ''
        
        from resume_customizer.config import Settings
        with pytest.raises(ValueError, match="API key cannot be empty"):
            Settings()
    
    def test_settings_validates_missing_api_key(self, clean_env):
        """Test that Settings validates API key is provided."""
        from resume_customizer.config import Settings
        from pydantic import ValidationError
        
        # Ensure no API key is in environment
        if 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']
        
        # Should raise either Field required or custom validator error
        with pytest.raises((ValidationError, ValueError)) as exc_info:
            Settings()
        
        # Check that it's related to API key
        error_str = str(exc_info.value)
        assert 'api' in error_str.lower() or 'field required' in error_str.lower()
    
    def test_settings_loads_from_env_file(self, clean_env, tmp_path):
        """Test that Settings can load from .env file."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("""
ANTHROPIC_API_KEY=env-file-api-key
RESUME_MAX_ITERATIONS=5
RESUME_OUTPUT_FORMAT=html
RESUME_PRESERVE_FORMATTING=false
""")
        
        # Change to temp directory
        original_cwd = Path.cwd()
        os.chdir(tmp_path)
        
        try:
            from resume_customizer.config import Settings
            settings = Settings()
            
            assert settings.claude_api_key == 'env-file-api-key'
            assert settings.max_iterations == 5
            assert settings.output_format == 'html'
            assert settings.preserve_formatting is False
        finally:
            os.chdir(original_cwd)
    
    def test_settings_env_vars_override_env_file(self, clean_env, tmp_path):
        """Test that environment variables override .env file values."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("""
ANTHROPIC_API_KEY=env-file-api-key
RESUME_MAX_ITERATIONS=5
""")
        
        # Set environment variable
        os.environ['ANTHROPIC_API_KEY'] = 'env-var-api-key'
        os.environ['RESUME_MAX_ITERATIONS'] = '10'
        
        # Change to temp directory
        original_cwd = Path.cwd()
        os.chdir(tmp_path)
        
        try:
            from resume_customizer.config import Settings
            settings = Settings()
            
            assert settings.claude_api_key == 'env-var-api-key'
            assert settings.max_iterations == 10
        finally:
            os.chdir(original_cwd)
    
    def test_settings_uses_resume_prefix(self, clean_env):
        """Test that Settings uses RESUME_ prefix for non-API-key vars."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key'
        os.environ['RESUME_MAX_ITERATIONS'] = '7'
        os.environ['RESUME_OUTPUT_FORMAT'] = 'pdf'
        os.environ['RESUME_PRESERVE_FORMATTING'] = 'false'
        
        from resume_customizer.config import Settings
        settings = Settings()
        
        assert settings.max_iterations == 7
        assert settings.output_format == 'pdf'
        assert settings.preserve_formatting is False
    
    def test_settings_validates_max_iterations(self, clean_env):
        """Test that Settings validates max_iterations is positive."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key'
        os.environ['RESUME_MAX_ITERATIONS'] = '0'
        
        from resume_customizer.config import Settings
        with pytest.raises(ValueError, match="max_iterations must be greater than 0"):
            Settings()
    
    def test_settings_validates_output_format(self, clean_env):
        """Test that Settings validates output_format is valid."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key'
        os.environ['RESUME_OUTPUT_FORMAT'] = 'invalid'
        
        from resume_customizer.config import Settings
        from pydantic import ValidationError
        with pytest.raises(ValidationError, match="Input should be"):
            Settings()
    
    def test_get_settings_caches_instance(self, clean_env):
        """Test that get_settings() caches the Settings instance."""
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key'
        
        from resume_customizer.config import get_settings
        
        # Clear any existing cache first
        get_settings.cache_clear()
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2  # Same instance
    
    def test_get_settings_cache_can_be_cleared(self, clean_env):
        """Test that get_settings cache can be cleared."""
        from resume_customizer.config import get_settings
        
        # Clear any existing cache first
        get_settings.cache_clear()
        
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key-1'
        
        settings1 = get_settings()
        assert settings1.claude_api_key == 'test-api-key-1'
        
        # Clear cache
        get_settings.cache_clear()
        
        # Change environment
        os.environ['ANTHROPIC_API_KEY'] = 'test-api-key-2'
        
        settings2 = get_settings()
        assert settings2.claude_api_key == 'test-api-key-2'
        assert settings1 is not settings2  # Different instances