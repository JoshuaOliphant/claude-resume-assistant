# ABOUTME: Integration tests for Claude API behavior and edge cases
# ABOUTME: Tests API responses, error handling, rate limiting, and SDK behavior

"""Integration tests for Claude API behavior."""

import pytest
import asyncio
import os
from pathlib import Path
import tempfile
from unittest.mock import patch, AsyncMock
import time

from resume_customizer.core.claude_client import ClaudeClient
from resume_customizer.config import Settings
from tests.integration.fixtures import test_data_manager, temp_test_environment


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping integration tests"
)
class TestAPIIntegration:
    """Test Claude API integration scenarios."""
    
    @pytest.fixture
    def settings(self):
        """Create settings for API tests."""
        return Settings(
            claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
            max_iterations=2
        )
    
    @pytest.mark.asyncio
    async def test_api_response_structure(self, settings, temp_test_environment):
        """Test that API responses have expected structure."""
        client = ClaudeClient(settings)
        
        # Track all messages from Claude
        messages = []
        tool_uses = []
        
        def track_progress(msg):
            messages.append(msg)
            if "Tool:" in msg:
                tool_uses.append(msg)
        
        await client.customize_resume(
            resume_path=temp_test_environment["resumes"]["minimal.md"],
            job_description_path=temp_test_environment["jobs"]["minimal_posting.md"],
            output_path=temp_test_environment["output_dir"] + "/api_test.md",
            progress_callback=track_progress
        )
        
        # Verify we got messages
        assert len(messages) > 0, "Should receive progress messages"
        assert len(tool_uses) >= 3, "Should use tools (Read x2, Write x1 minimum)"
        
        # Check tool use patterns
        read_count = sum(1 for msg in tool_uses if "Read" in msg)
        write_count = sum(1 for msg in tool_uses if "Write" in msg)
        
        assert read_count >= 2, "Should read both input files"
        assert write_count >= 1, "Should write output file"
    
    @pytest.mark.asyncio
    async def test_api_with_complex_prompt(self, settings, temp_test_environment):
        """Test API with complex, multi-instruction prompt."""
        client = ClaudeClient(settings)
        
        # Use senior resume with complex job description
        await client.customize_resume(
            resume_path=temp_test_environment["resumes"]["senior_level.md"],
            job_description_path=temp_test_environment["jobs"]["ai_ml"],
            output_path=temp_test_environment["output_dir"] + "/complex_prompt.md"
        )
        
        # Read output to verify complexity handled
        output_content = Path(temp_test_environment["output_dir"] + "/complex_prompt.md").read_text()
        
        # Should integrate ML-specific content
        ml_keywords = ["machine learning", "neural network", "tensorflow", "pytorch"]
        keywords_found = sum(1 for kw in ml_keywords if kw.lower() in output_content.lower())
        assert keywords_found >= 2, "Should integrate ML-specific keywords"
    
    @pytest.mark.asyncio
    async def test_api_retry_behavior(self, settings):
        """Test API retry behavior on transient errors."""
        client = ClaudeClient(settings)
        
        # Track retry attempts
        call_count = 0
        original_send = client.agent.messages.stream
        
        async def mock_send(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            # Simulate transient error on first call
            if call_count == 1:
                raise Exception("Transient API error")
            
            # Call original on subsequent attempts
            return await original_send(*args, **kwargs)
        
        # Temporarily mock the send method
        with patch.object(client.agent.messages, 'stream', mock_send):
            # Create minimal test case
            with tempfile.TemporaryDirectory() as tmpdir:
                resume_path = Path(tmpdir) / "resume.md"
                resume_path.write_text("# Test\nDeveloper")
                
                job_path = Path(tmpdir) / "job.md"
                job_path.write_text("Python developer")
                
                output_path = Path(tmpdir) / "output.md"
                
                try:
                    await client.customize_resume(
                        resume_path=str(resume_path),
                        job_description_path=str(job_path),
                        output_path=str(output_path)
                    )
                except Exception:
                    pass  # Expected to fail after retries
                
                # Should have attempted multiple times
                assert call_count > 1, "Should retry on transient errors"
    
    @pytest.mark.asyncio
    async def test_api_with_long_content(self, settings):
        """Test API handling of long content that might approach token limits."""
        client = ClaudeClient(settings)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a very detailed resume
            resume_parts = ["# Detailed Professional History\n\n"]
            
            # Add many detailed experiences
            for i in range(15):
                resume_parts.append(f"""## Position {i+1} - Company {i+1} (20{i:02d}-20{i+2:02d})
### Key Achievements:
- Led cross-functional team of {10+i} engineers across {3+i//5} time zones
- Architected and implemented microservices handling {1000*(i+1)} requests/second
- Reduced operational costs by ${50000 + i*10000} through optimization
- Mentored {5+i//3} junior developers and conducted {20+i*2} technical interviews
- Published {2+i//5} technical articles and presented at {1+i//4} conferences
- Implemented CI/CD pipeline reducing deployment time from {60-i*2} to {10-i//2} minutes

### Technical Responsibilities:
- Designed distributed systems using event-driven architecture
- Implemented machine learning models for predictive analytics
- Optimized database queries improving performance by {40+i*5}%
- Built real-time data processing pipelines handling {i+1}TB daily
- Established coding standards and best practices for team
- Conducted architecture reviews and made technical decisions

### Technologies Used:
Python, Go, Java, Kubernetes, Docker, AWS, GCP, Terraform, Kafka, Redis, PostgreSQL, 
MongoDB, Elasticsearch, Prometheus, Grafana, Jenkins, GitHub Actions, React, Node.js

""")
            
            long_resume = "".join(resume_parts)
            resume_path = Path(tmpdir) / "long_resume.md"
            resume_path.write_text(long_resume)
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Looking for senior technical architect")
            
            output_path = Path(tmpdir) / "long_output.md"
            
            # Should handle long content
            await client.customize_resume(
                resume_path=str(resume_path),
                job_description_path=str(job_path),
                output_path=str(output_path)
            )
            
            # Verify output created
            assert output_path.exists()
            output_content = output_path.read_text()
            assert len(output_content) > 100
    
    @pytest.mark.asyncio
    async def test_api_parallel_requests(self, settings, temp_test_environment):
        """Test making parallel API requests."""
        # Create multiple clients
        clients = [ClaudeClient(settings) for _ in range(3)]
        
        # Define different customization tasks
        tasks = []
        for i, client in enumerate(clients):
            output_path = f"{temp_test_environment['output_dir']}/parallel_{i}.md"
            
            task = client.customize_resume(
                resume_path=temp_test_environment["resumes"]["minimal.md"],
                job_description_path=temp_test_environment["jobs"]["minimal_posting.md"],
                output_path=output_path
            )
            tasks.append((i, task))
        
        # Run in parallel
        start_time = time.time()
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        end_time = time.time()
        
        # All should succeed
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Task {i} failed: {result}"
            output_path = f"{temp_test_environment['output_dir']}/parallel_{i}.md"
            assert Path(output_path).exists()
        
        print(f"Parallel execution time: {end_time - start_time:.2f}s for {len(tasks)} tasks")
    
    @pytest.mark.asyncio
    async def test_api_with_special_instructions(self, settings):
        """Test API behavior with special instructions in prompt."""
        client = ClaudeClient(settings)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create resume with specific formatting
            resume_path = Path(tmpdir) / "formatted_resume.md"
            resume_path.write_text("""# Jane Developer

## PROFESSIONAL_SUMMARY
Expert software engineer specializing in distributed systems.

## WORK_EXPERIENCE
### SENIOR_ENGINEER | TechCorp | 2020-Present
- Built scalable microservices
- Led technical initiatives

## TECHNICAL_SKILLS
- Programming: Python, Go, Java
- Cloud: AWS, GCP, Azure
""")
            
            # Job with specific requirements
            job_path = Path(tmpdir) / "specific_job.md"
            job_path.write_text("""# Cloud Architect Position

MUST HAVE:
- 5+ years AWS experience
- Kubernetes expertise
- Python proficiency

NICE TO HAVE:
- Go programming
- Terraform experience
- Security certifications
""")
            
            output_path = Path(tmpdir) / "formatted_output.md"
            
            await client.customize_resume(
                resume_path=str(resume_path),
                job_description_path=str(job_path),
                output_path=str(output_path)
            )
            
            output_content = output_path.read_text()
            
            # Should handle special formatting and requirements
            assert "AWS" in output_content
            assert "Kubernetes" in output_content
    
    @pytest.mark.asyncio
    async def test_api_error_messages(self, settings):
        """Test that API errors provide meaningful messages."""
        # Test with invalid API key
        bad_settings = Settings(
            claude_api_key="invalid-key-format",
            max_iterations=1
        )
        
        client = ClaudeClient(bad_settings)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_path = Path(tmpdir) / "resume.md"
            resume_path.write_text("# Test Resume")
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Test Job")
            
            output_path = Path(tmpdir) / "output.md"
            
            # Should raise meaningful error
            with pytest.raises(Exception) as exc_info:
                await client.customize_resume(
                    resume_path=str(resume_path),
                    job_description_path=str(job_path),
                    output_path=str(output_path)
                )
            
            # Error should be informative
            error_msg = str(exc_info.value)
            assert len(error_msg) > 0
    
    @pytest.mark.asyncio
    async def test_api_progress_callback_frequency(self, settings, temp_test_environment):
        """Test frequency and timing of progress callbacks."""
        client = ClaudeClient(settings)
        
        # Track callback timing
        callback_times = []
        
        def track_timing(msg):
            callback_times.append({
                "time": time.time(),
                "message": msg
            })
        
        start_time = time.time()
        
        await client.customize_resume(
            resume_path=temp_test_environment["resumes"]["mid_level.md"],
            job_description_path=temp_test_environment["jobs"]["standard_swe.md"],
            output_path=temp_test_environment["output_dir"] + "/timing_test.md",
            progress_callback=track_timing
        )
        
        # Analyze callback patterns
        assert len(callback_times) > 0, "Should have progress callbacks"
        
        # Calculate intervals
        if len(callback_times) > 1:
            intervals = []
            for i in range(1, len(callback_times)):
                interval = callback_times[i]["time"] - callback_times[i-1]["time"]
                intervals.append(interval)
            
            avg_interval = sum(intervals) / len(intervals)
            print(f"Average callback interval: {avg_interval:.2f}s")
            print(f"Total callbacks: {len(callback_times)}")
    
    @pytest.mark.asyncio
    async def test_api_with_rate_limiting(self, settings, temp_test_environment):
        """Test behavior when approaching rate limits."""
        # Make multiple rapid requests
        client = ClaudeClient(settings)
        
        results = []
        for i in range(3):
            try:
                output_path = f"{temp_test_environment['output_dir']}/rate_limit_{i}.md"
                
                await client.customize_resume(
                    resume_path=temp_test_environment["resumes"]["minimal.md"],
                    job_description_path=temp_test_environment["jobs"]["minimal_posting.md"],
                    output_path=output_path
                )
                
                results.append({"success": True, "index": i})
                
                # Small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                results.append({"success": False, "index": i, "error": str(e)})
        
        # Should handle rate limiting gracefully
        successful = sum(1 for r in results if r["success"])
        assert successful >= 1, "At least some requests should succeed"
        
        print(f"Rate limit test: {successful}/{len(results)} requests succeeded")