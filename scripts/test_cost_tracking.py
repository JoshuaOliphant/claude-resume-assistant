#!/usr/bin/env python3
"""Quick script to test cost tracking functionality."""

import asyncio
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resume_customizer.core.customizer import ResumeCustomizer
from resume_customizer.config import Settings


async def test_cost_tracking():
    """Test the cost tracking functionality."""
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set")
        return
    
    # Initialize customizer with only 1 iteration for faster testing
    settings = Settings(max_iterations=1)
    customizer = ResumeCustomizer(settings)
    
    # Create test files
    test_dir = Path("test_cost_output")
    test_dir.mkdir(exist_ok=True)
    
    # Simple resume
    resume_path = test_dir / "test_resume.md"
    resume_path.write_text("""# John Doe
Software Engineer

## Experience
- 5 years Python development
- Cloud architecture experience
- Team leadership

## Skills
Python, AWS, Docker, Kubernetes
""")
    
    # Simple job description
    job_path = test_dir / "test_job.md"
    job_path.write_text("""# Senior Software Engineer

Looking for experienced Python developer with cloud experience.

## Requirements
- Python expertise
- AWS knowledge
- Leadership skills
""")
    
    output_path = test_dir / "customized_resume.md"
    
    print("Starting resume customization...")
    print(f"Model: claude-sonnet-4-0")
    print(f"Iterations: {settings.max_iterations}")
    print()
    
    try:
        # Customize resume
        await customizer.customize(
            resume_path=str(resume_path),
            job_description_path=str(job_path),
            output_path=str(output_path)
        )
        
        # Get usage stats
        stats = customizer.claude_client.get_usage_stats()
        
        print("\n=== Cost Tracking Results ===")
        print(f"Total requests: {len(stats['requests'])}")
        print(f"Total input tokens: {stats['total_input_tokens']:,}")
        print(f"Total output tokens: {stats['total_output_tokens']:,}")
        print(f"Total tokens: {stats['total_input_tokens'] + stats['total_output_tokens']:,}")
        print(f"Total cost: ${stats['total_cost']:.4f}")
        
        if stats['requests']:
            avg_cost = customizer.claude_client.get_average_cost_per_resume()
            print(f"Average cost per resume: ${avg_cost:.4f}")
            
            print("\nPer-request breakdown:")
            for i, req in enumerate(stats['requests'], 1):
                print(f"  Request {i}:")
                print(f"    Input tokens: {req['input_tokens']:,}")
                print(f"    Output tokens: {req['output_tokens']:,}")
                print(f"    Cost: ${req['cost']:.4f}")
        
        # Check output
        if output_path.exists():
            print(f"\nOutput file created: {output_path}")
            print(f"Output size: {len(output_path.read_text())} characters")
        else:
            print("\nWarning: Output file was not created")
            
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Cleanup
        print("\nCleaning up test files...")
        for file in [resume_path, job_path, output_path]:
            if file.exists():
                file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


if __name__ == "__main__":
    asyncio.run(test_cost_tracking())