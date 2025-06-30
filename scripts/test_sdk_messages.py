#!/usr/bin/env python3
"""Test to capture all messages from Claude Code SDK."""

import asyncio
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_code_sdk import query, ClaudeCodeOptions
import json


async def test_sdk_messages():
    """Test to see all messages from SDK."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set")
        return
    
    print("Capturing all messages from Claude Code SDK...")
    
    # Create test files
    test_dir = Path("sdk_test")
    test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / "test.txt"
    test_file.write_text("Hello World")
    
    options = ClaudeCodeOptions(
        max_turns=2,
        allowed_tools=["Read"],
        model="claude-sonnet-4-0"
    )
    
    prompt = f"Please read the file at {test_file} and tell me what it says. Be brief."
    
    messages = []
    
    async for message in query(prompt=prompt, options=options):
        msg_info = {
            "type": type(message).__name__,
            "has_usage": hasattr(message, 'usage'),
            "has_total_cost": hasattr(message, 'total_cost_usd'),
            "has_subtype": hasattr(message, 'subtype'),
        }
        
        if hasattr(message, 'subtype'):
            msg_info['subtype'] = message.subtype
            
        if hasattr(message, 'usage'):
            msg_info['usage'] = message.usage
            
        if hasattr(message, 'total_cost_usd'):
            msg_info['total_cost_usd'] = message.total_cost_usd
            
        messages.append(msg_info)
        print(f"\nMessage {len(messages)}:")
        print(json.dumps(msg_info, indent=2))
    
    # Cleanup
    test_file.unlink()
    test_dir.rmdir()
    
    print(f"\nTotal messages received: {len(messages)}")
    
    # Check if any had cost info
    cost_messages = [m for m in messages if m.get('has_total_cost')]
    print(f"Messages with cost info: {len(cost_messages)}")
    
    if cost_messages:
        for i, msg in enumerate(cost_messages):
            print(f"\nCost message {i+1}:")
            print(f"  Type: {msg['type']}")
            print(f"  Cost: ${msg.get('total_cost_usd', 0):.6f}")
            if msg.get('usage'):
                print(f"  Usage: {msg['usage']}")


if __name__ == "__main__":
    asyncio.run(test_sdk_messages())