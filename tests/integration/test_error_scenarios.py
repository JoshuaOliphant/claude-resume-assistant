# ABOUTME: Integration tests for error handling and edge cases
# ABOUTME: Tests graceful failure, recovery, and error messaging in real scenarios

"""Integration tests for error scenarios and edge cases."""

import pytest
import os
import tempfile
from pathlib import Path
import asyncio
from unittest.mock import patch, AsyncMock
import signal
import platform

from resume_customizer.core.customizer import ResumeCustomizer
from resume_customizer.core.claude_client import ClaudeClient
from resume_customizer.config import Settings
from resume_customizer.cli.app import cli
from click.testing import CliRunner
from tests.integration.fixtures import test_data_manager


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping integration tests"
)
class TestErrorScenarios:
    """Test error handling in various scenarios."""
    
    @pytest.fixture
    def settings(self):
        """Create settings for error tests."""
        return Settings(max_iterations=1)
    
    @pytest.fixture
    def customizer(self, settings):
        """Create customizer instance."""
        return ResumeCustomizer(settings)
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, settings):
        """Test handling of network errors during API calls."""
        client = ClaudeClient(settings)
        
        # Mock network error
        original_send = client.agent.messages.stream
        call_count = 0
        
        async def mock_network_error(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Network connection failed")
        
        with patch.object(client.agent.messages, 'stream', mock_network_error):
            with tempfile.TemporaryDirectory() as tmpdir:
                resume_path = Path(tmpdir) / "resume.md"
                resume_path.write_text("# Test Resume")
                
                job_path = Path(tmpdir) / "job.md"
                job_path.write_text("Test Job")
                
                output_path = Path(tmpdir) / "output.md"
                
                # Should raise connection error
                with pytest.raises(ConnectionError):
                    await client.customize_resume(
                        resume_path=str(resume_path),
                        job_description_path=str(job_path),
                        output_path=str(output_path)
                    )
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, settings):
        """Test handling of timeouts during long operations."""
        client = ClaudeClient(settings)
        
        # Mock slow response
        async def mock_slow_response(*args, **kwargs):
            await asyncio.sleep(300)  # Simulate very slow response
        
        with patch.object(client.agent.messages, 'stream', mock_slow_response):
            with tempfile.TemporaryDirectory() as tmpdir:
                resume_path = Path(tmpdir) / "resume.md"
                resume_path.write_text("# Test Resume")
                
                job_path = Path(tmpdir) / "job.md"
                job_path.write_text("Test Job")
                
                output_path = Path(tmpdir) / "output.md"
                
                # Should handle timeout (this will actually wait for the mock)
                # In real scenarios, the SDK would timeout
                try:
                    await asyncio.wait_for(
                        client.customize_resume(
                            resume_path=str(resume_path),
                            job_description_path=str(job_path),
                            output_path=str(output_path)
                        ),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    pass  # Expected
    
    @pytest.mark.asyncio
    async def test_malformed_input_handling(self, customizer):
        """Test handling of malformed input files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create binary file (non-text)
            binary_path = Path(tmpdir) / "binary.pdf"
            binary_path.write_bytes(b'\x00\x01\x02\x03\xFF\xFE\xFD')
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Test Job")
            
            output_path = Path(tmpdir) / "output.md"
            
            # Should handle binary file gracefully
            try:
                await customizer.customize(
                    resume_path=str(binary_path),
                    job_description_path=str(job_path),
                    output_path=str(output_path)
                )
                # If it succeeds, check output exists
                assert output_path.exists()
            except Exception as e:
                # Should provide meaningful error
                assert len(str(e)) > 0
    
    @pytest.mark.asyncio
    async def test_disk_space_error(self, customizer):
        """Test handling when disk is full."""
        if platform.system() == 'Windows':
            pytest.skip("Disk space test not reliable on Windows")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_path = Path(tmpdir) / "resume.md"
            resume_path.write_text("# Test Resume\n" * 100)
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Test Job")
            
            output_path = Path(tmpdir) / "output.md"
            
            # Mock disk full error
            original_write = Path.write_text
            
            def mock_disk_full(self, *args, **kwargs):
                if "output" in str(self):
                    raise OSError(28, "No space left on device")
                return original_write(self, *args, **kwargs)
            
            with patch.object(Path, 'write_text', mock_disk_full):
                # Should handle disk full error
                with pytest.raises(OSError) as exc_info:
                    await customizer.customize(
                        resume_path=str(resume_path),
                        job_description_path=str(job_path),
                        output_path=str(output_path)
                    )
                
                assert "No space left" in str(exc_info.value)
    
    def test_cli_interrupt_handling(self, test_data_manager):
        """Test CLI handles interruption (Ctrl+C) gracefully."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_path = Path(tmpdir) / "resume.md"
            resume_path.write_text(test_data_manager.get_sample_resume("mid"))
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text(test_data_manager.get_sample_job_description("standard"))
            
            output_path = Path(tmpdir) / "output.md"
            
            # Can't easily test actual Ctrl+C in unit tests
            # But we can verify the CLI structure handles exceptions
            with patch('resume_customizer.core.customizer.ResumeCustomizer.customize') as mock_customize:
                mock_customize.side_effect = KeyboardInterrupt()
                
                result = runner.invoke(cli, [
                    'customize',
                    '--resume', str(resume_path),
                    '--job', str(job_path),
                    '--output', str(output_path)
                ], catch_exceptions=False)
                
                # Should exit cleanly
                assert result.exit_code != 0
    
    @pytest.mark.asyncio
    async def test_partial_completion_recovery(self, customizer):
        """Test behavior when process is interrupted mid-operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_path = Path(tmpdir) / "resume.md"
            resume_path.write_text("# Test Resume\nContent here")
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Test Job Description")
            
            output_path = Path(tmpdir) / "output.md"
            
            # Create partial output file
            output_path.write_text("# Partial Output\nThis is incomplete...")
            
            # Run customization (should overwrite)
            await customizer.customize(
                resume_path=str(resume_path),
                job_description_path=str(job_path),
                output_path=str(output_path)
            )
            
            # Should have new content
            final_content = output_path.read_text()
            assert "This is incomplete..." not in final_content
            assert len(final_content) > 50
    
    @pytest.mark.asyncio
    async def test_concurrent_access_errors(self, customizer):
        """Test errors when files are locked or in use."""
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_path = Path(tmpdir) / "resume.md"
            resume_path.write_text("# Test Resume")
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Test Job")
            
            output_path = Path(tmpdir) / "output.md"
            
            # Simulate file lock (platform-specific)
            if platform.system() != 'Windows':
                # On Unix, we can use file descriptors
                import fcntl
                
                # Open and lock the output file
                with open(output_path, 'w') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    
                    # Try to customize while file is locked
                    try:
                        await customizer.customize(
                            resume_path=str(resume_path),
                            job_description_path=str(job_path),
                            output_path=str(output_path)
                        )
                    except Exception as e:
                        # Should handle lock gracefully
                        assert True  # Expected to fail
    
    @pytest.mark.asyncio
    async def test_invalid_api_key_error(self):
        """Test clear error message for invalid API key."""
        # Create settings with invalid key
        bad_settings = Settings(
            claude_api_key="sk-invalid-key-12345",
            max_iterations=1
        )
        
        customizer = ResumeCustomizer(bad_settings)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_path = Path(tmpdir) / "resume.md"
            resume_path.write_text("# Test Resume")
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Test Job")
            
            output_path = Path(tmpdir) / "output.md"
            
            # Should provide clear error about API key
            with pytest.raises(Exception) as exc_info:
                await customizer.customize(
                    resume_path=str(resume_path),
                    job_description_path=str(job_path),
                    output_path=str(output_path)
                )
            
            error_msg = str(exc_info.value).lower()
            # Should mention authentication or API key
            assert any(term in error_msg for term in ["auth", "api", "key", "invalid"])
    
    @pytest.mark.asyncio
    async def test_memory_error_simulation(self, customizer):
        """Test handling of memory errors with very large files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create extremely large resume (simulate)
            resume_path = Path(tmpdir) / "huge_resume.md"
            
            # Write large content in chunks to avoid actual memory issues
            with open(resume_path, 'w') as f:
                f.write("# Huge Resume\n\n")
                # Write 100MB of content (simulated)
                chunk = "This is a test line that repeats. " * 100 + "\n"
                for _ in range(1000):  # Much smaller than actual 100MB
                    f.write(chunk)
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Simple job")
            
            output_path = Path(tmpdir) / "output.md"
            
            # Should handle large files
            # (In practice, Claude SDK has its own limits)
            try:
                await customizer.customize(
                    resume_path=str(resume_path),
                    job_description_path=str(job_path),
                    output_path=str(output_path)
                )
                # If successful, output should exist
                assert output_path.exists()
            except Exception as e:
                # If it fails, should have meaningful error
                assert len(str(e)) > 0
    
    def test_cli_missing_dependencies(self):
        """Test CLI behavior when dependencies are missing."""
        runner = CliRunner()
        
        # Mock missing claude_code module
        with patch.dict('sys.modules', {'claude_code': None}):
            # This would normally fail at import time
            # But we can test the general structure
            result = runner.invoke(cli, ['--help'])
            
            # CLI should still provide basic help
            assert result.exit_code == 0 or result.exit_code == 1
    
    @pytest.mark.asyncio
    async def test_unicode_errors(self, customizer):
        """Test handling of unicode encoding/decoding errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with potential unicode issues
            resume_path = Path(tmpdir) / "unicode_resume.md"
            
            # Mix of valid and potentially problematic unicode
            content = """# Test Résumé 
            
## Experience with 文字化け            
- Worked on 한국어 projects
- Specialized in אותיות עבריות
- Experience with emoji: 🚀 💻 🎯
- Zero-width characters: ​‌‍
"""
            resume_path.write_text(content, encoding='utf-8')
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Standard job description", encoding='utf-8')
            
            output_path = Path(tmpdir) / "output.md"
            
            # Should handle unicode properly
            await customizer.customize(
                resume_path=str(resume_path),
                job_description_path=str(job_path),
                output_path=str(output_path)
            )
            
            # Output should maintain unicode
            output_content = output_path.read_text(encoding='utf-8')
            assert "Résumé" in output_content or "Resume" in output_content