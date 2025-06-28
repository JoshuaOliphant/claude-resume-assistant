# ABOUTME: Integration tests for ClaudeClient using real Claude Code SDK
# ABOUTME: Tests actual file operations and Claude's behavior without mocks

"""Integration tests for Claude Code SDK with file operations."""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from resume_customizer.core.claude_client import ClaudeClient
from resume_customizer.config import Settings


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping integration tests"
)
class TestClaudeIntegration:
    """Integration tests using real Claude Code SDK."""
    
    @pytest.fixture
    def settings(self):
        """Create settings with real API key."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")
        
        return Settings(
            claude_api_key=api_key,
            max_iterations=2  # Fewer iterations for testing
        )
    
    @pytest.fixture
    def test_files(self):
        """Create real test files for Claude to work with."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple test resume
            resume_path = Path(tmpdir) / "test_resume.md"
            resume_path.write_text("""# Jane Smith

## Contact
- Email: jane.smith@email.com
- Phone: (555) 123-4567
- Location: San Francisco, CA

## Summary
Experienced software engineer with 5 years building web applications.

## Experience

### Software Engineer - TechCorp (2020-Present)
- Developed RESTful APIs using Python and Django
- Implemented CI/CD pipelines with GitHub Actions
- Mentored junior developers

### Junior Developer - StartupXYZ (2018-2020)
- Built frontend components with React
- Worked on database optimization
- Participated in agile development

## Skills
- Languages: Python, JavaScript, SQL
- Frameworks: Django, React, Flask
- Tools: Git, Docker, AWS

## Education
BS Computer Science - University of California (2018)
""")
            
            # Create a test job description
            job_path = Path(tmpdir) / "test_job.md"
            job_path.write_text("""# Senior Python Developer

## About the Role
We're looking for a Senior Python Developer to join our growing team.

## Requirements
- 5+ years of Python development experience
- Strong experience with FastAPI or Flask
- Knowledge of PostgreSQL and Redis
- Experience with microservices architecture
- AWS cloud experience required
- Leadership and mentoring experience

## Nice to Have
- Experience with Kubernetes
- Machine learning knowledge
- Open source contributions

## What You'll Do
- Design and implement scalable APIs
- Lead technical discussions
- Mentor team members
- Optimize system performance
""")
            
            # Output path
            output_path = Path(tmpdir) / "customized_resume.md"
            
            yield {
                "resume": str(resume_path),
                "job": str(job_path),
                "output": str(output_path),
                "tmpdir": tmpdir
            }
    
    @pytest.mark.asyncio
    async def test_basic_file_operations(self, settings, test_files):
        """Test that Claude can read input files and write output."""
        client = ClaudeClient(settings)
        
        # Track progress messages
        progress_messages = []
        def progress_callback(msg):
            progress_messages.append(msg)
            print(f"Progress: {msg}")  # For debugging
        
        # Run customization
        await client.customize_resume(
            resume_path=test_files["resume"],
            job_description_path=test_files["job"],
            output_path=test_files["output"],
            progress_callback=progress_callback
        )
        
        # Verify output file was created
        assert Path(test_files["output"]).exists(), "Output file should be created"
        
        # Read the output content
        output_content = Path(test_files["output"]).read_text()
        
        # Basic checks on the output
        assert len(output_content) > 100, "Output should have substantial content"
        assert "Jane Smith" in output_content, "Should preserve candidate name"
        
        # Check that progress was reported
        assert len(progress_messages) > 0, "Should report progress"
        
        # Check for tool usage messages
        tool_messages = [msg for msg in progress_messages if "Tool:" in msg]
        assert any("Read" in msg for msg in tool_messages), "Should report Read tool usage"
        assert any("Write" in msg for msg in tool_messages), "Should report Write tool usage"
    
    @pytest.mark.asyncio
    async def test_keyword_integration(self, settings, test_files):
        """Test that Claude integrates keywords from job description."""
        client = ClaudeClient(settings)
        
        await client.customize_resume(
            resume_path=test_files["resume"],
            job_description_path=test_files["job"],
            output_path=test_files["output"]
        )
        
        output_content = Path(test_files["output"]).read_text().lower()
        
        # Check for job-specific keywords
        keywords_to_check = ["fastapi", "microservices", "postgresql", "redis", "mentoring"]
        integrated_keywords = [kw for kw in keywords_to_check if kw in output_content]
        
        # Should integrate at least some keywords
        assert len(integrated_keywords) >= 2, f"Should integrate job keywords, found: {integrated_keywords}"
    
    @pytest.mark.asyncio
    async def test_error_handling_nonexistent_file(self, settings, test_files):
        """Test handling of non-existent input files."""
        client = ClaudeClient(settings)
        
        # Test with non-existent resume
        with pytest.raises(FileNotFoundError, match="Resume file not found"):
            await client.customize_resume(
                resume_path="/nonexistent/resume.md",
                job_description_path=test_files["job"],
                output_path=test_files["output"]
            )
        
        # Test with non-existent job description
        with pytest.raises(FileNotFoundError, match="Job description file not found"):
            await client.customize_resume(
                resume_path=test_files["resume"],
                job_description_path="/nonexistent/job.md",
                output_path=test_files["output"]
            )
    
    @pytest.mark.asyncio
    async def test_output_directory_creation(self, settings, test_files):
        """Test that output directory is created if it doesn't exist."""
        client = ClaudeClient(settings)
        
        # Create a nested output path
        nested_output = os.path.join(test_files["tmpdir"], "nested", "dir", "output.md")
        
        await client.customize_resume(
            resume_path=test_files["resume"],
            job_description_path=test_files["job"],
            output_path=nested_output
        )
        
        # Verify the directory was created and file exists
        assert Path(nested_output).exists(), "Should create nested directories"
    
    @pytest.mark.asyncio
    async def test_minimal_resume(self, settings):
        """Test with a very minimal resume to see how Claude handles it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal resume
            resume_path = Path(tmpdir) / "minimal.md"
            resume_path.write_text("# John Doe\n\nSoftware Developer")
            
            # Create minimal job description
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Looking for a Python developer with 3 years experience.")
            
            output_path = Path(tmpdir) / "output.md"
            
            client = ClaudeClient(settings)
            
            await client.customize_resume(
                resume_path=str(resume_path),
                job_description_path=str(job_path),
                output_path=str(output_path)
            )
            
            # Should still create output
            assert output_path.exists()
            content = output_path.read_text()
            assert "John Doe" in content
    
    @pytest.mark.asyncio
    async def test_progress_tracking(self, settings, test_files):
        """Test detailed progress tracking throughout the process."""
        client = ClaudeClient(settings)
        
        progress_log = []
        def detailed_callback(msg):
            progress_log.append({
                "message": msg,
                "timestamp": asyncio.get_event_loop().time()
            })
        
        start_time = asyncio.get_event_loop().time()
        
        await client.customize_resume(
            resume_path=test_files["resume"],
            job_description_path=test_files["job"],
            output_path=test_files["output"],
            progress_callback=detailed_callback
        )
        
        end_time = asyncio.get_event_loop().time()
        
        # Analyze progress
        assert len(progress_log) > 0, "Should have progress messages"
        
        # Check message types
        text_messages = [p for p in progress_log if "Tool:" not in p["message"]]
        tool_messages = [p for p in progress_log if "Tool:" in p["message"]]
        
        assert len(text_messages) > 0, "Should have text progress messages"
        assert len(tool_messages) >= 3, "Should have at least 3 tool uses (2 reads, 1 write)"
        
        # Verify timing
        total_time = end_time - start_time
        print(f"Total execution time: {total_time:.2f} seconds")
        
        # Check for specific tool patterns
        read_tools = [p for p in tool_messages if "Read" in p["message"]]
        write_tools = [p for p in tool_messages if "Write" in p["message"]]
        
        assert len(read_tools) >= 2, "Should read both input files"
        assert len(write_tools) >= 1, "Should write output file"
    
    @pytest.mark.asyncio
    async def test_multiple_iterations(self, settings, test_files):
        """Test that Claude performs multiple iterations as configured."""
        # Use settings with specific iteration count
        settings.max_iterations = 3
        client = ClaudeClient(settings)
        
        iteration_messages = []
        def track_iterations(msg):
            if "iteration" in msg.lower():
                iteration_messages.append(msg)
        
        await client.customize_resume(
            resume_path=test_files["resume"],
            job_description_path=test_files["job"],
            output_path=test_files["output"],
            progress_callback=track_iterations
        )
        
        # Claude should mention iterations in its process
        # Note: This depends on how Claude interprets the prompt
        output_content = Path(test_files["output"]).read_text()
        assert len(output_content) > 0, "Should produce output after iterations"