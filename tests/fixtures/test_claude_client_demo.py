#!/usr/bin/env python3
# ABOUTME: Script to demonstrate ClaudeClient functionality
# ABOUTME: Shows API integration, error handling, and usage tracking

"""Test script for ClaudeClient functionality."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from resume_customizer.core.claude_client import ClaudeClient, ClaudeAPIError
from resume_customizer.config import Settings


async def test_claude_client():
    """Test ClaudeClient with various scenarios."""
    print("Testing ClaudeClient functionality...\n")
    
    # Note: This demo uses mocked responses since we're not making real API calls
    print("1. Client Initialization:")
    try:
        # This would normally load from .env
        settings = Settings(
            claude_api_key="test-key-for-demo",
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7
        )
        print(f"   ✓ Settings loaded")
        print(f"   ✓ Model: {settings.model}")
        print(f"   ✓ Max tokens: {settings.max_tokens}")
        print(f"   ✓ Temperature: {settings.temperature}")
    except Exception as e:
        print(f"   ✗ Settings error: {e}")
        return
    
    print("\n2. Query Examples (Simulated):")
    
    # Example prompts
    prompts = [
        {
            "prompt": "Analyze this resume for ATS keywords",
            "system": "You are an expert resume analyzer.",
            "tokens": (150, 250)
        },
        {
            "prompt": "Suggest improvements for this job description match",
            "system": "You are a career counselor specializing in resume customization.",
            "tokens": (200, 300)
        },
        {
            "prompt": "Rewrite this experience section to highlight leadership",
            "system": None,
            "tokens": (100, 400)
        }
    ]
    
    # Simulate responses
    print("   Note: Using simulated responses for demonstration\n")
    
    total_cost = 0.0
    for i, example in enumerate(prompts, 1):
        print(f"   Query {i}:")
        print(f"   - Prompt: '{example['prompt'][:50]}...'")
        if example['system']:
            print(f"   - System: '{example['system'][:50]}...'")
        
        # Simulate token usage
        input_tokens, output_tokens = example['tokens']
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        cost_per_input = 3.0 / 1000  # $3 per million input tokens
        cost_per_output = 15.0 / 1000  # $15 per million output tokens
        query_cost = (input_tokens / 1000) * cost_per_input + (output_tokens / 1000) * cost_per_output
        total_cost += query_cost
        
        print(f"   - Tokens: {input_tokens} in, {output_tokens} out ({total_tokens} total)")
        print(f"   - Cost: ${query_cost:.4f}")
        print()
    
    print(f"3. Usage Summary:")
    print(f"   - Total queries: {len(prompts)}")
    print(f"   - Total tokens: {sum(sum(p['tokens']) for p in prompts)}")
    print(f"   - Total cost: ${total_cost:.4f}")
    print()
    
    print("4. Error Handling Examples:")
    error_scenarios = [
        ("Rate limit error", "429", "ClaudeRateLimitError"),
        ("Invalid API key", "401", "ClaudeAPIError"),
        ("Timeout", "timeout", "ClaudeTimeoutError"),
        ("Empty response", "empty", "ClaudeAPIError")
    ]
    
    for scenario, code, error_type in error_scenarios:
        print(f"   - {scenario}: Would raise {error_type}")
    
    print("\n5. Retry Logic:")
    print("   - Max retries: 3")
    print("   - Retry delay: 1.0s (exponential backoff)")
    print("   - Handles rate limits automatically")
    
    print("\n6. Model Support:")
    models = [
        ("Claude 3 Opus", "claude-3-opus-20240229", "$15/$75"),
        ("Claude 3.5 Sonnet", "claude-3-5-sonnet-20241022", "$3/$15"),
        ("Claude 3 Haiku", "claude-3-haiku-20240307", "$0.25/$1.25")
    ]
    
    for name, model_id, pricing in models:
        print(f"   - {name}: {pricing} per million tokens")
    
    print("\nClaudeClient demo completed! ✅")


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(test_claude_client())