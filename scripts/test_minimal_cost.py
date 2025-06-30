#!/usr/bin/env python3
"""Minimal test to check Claude Code SDK cost tracking."""

import asyncio
import os
from pathlib import Path
import sys
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_code_sdk import query, ClaudeCodeOptions


async def test_minimal():
    """Test minimal Claude Code SDK usage to see cost fields."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set")
        return
    
    print("Testing Claude Code SDK cost tracking...")
    
    options = ClaudeCodeOptions(
        max_turns=1,
        allowed_tools=["Read"],
        model="claude-sonnet-4-0"
    )
    
    prompt = "Please just say 'Hello' and nothing else."
    
    async for message in query(prompt=prompt, options=options):
        print(f"\nMessage type: {type(message)}")
        print(f"Message attributes: {[attr for attr in dir(message) if not attr.startswith('_')]}")
        
        if hasattr(message, 'usage'):
            print(f"Has usage: {message.usage}")
            
        if hasattr(message, 'total_cost_usd'):
            print(f"Total cost USD: ${message.total_cost_usd}")
            
        if hasattr(message, 'content'):
            print(f"Content: {message.content[:100] if message.content else 'None'}")


if __name__ == "__main__":
    asyncio.run(test_minimal())