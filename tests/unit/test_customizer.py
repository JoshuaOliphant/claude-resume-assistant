# ABOUTME: Test suite for the simplified ResumeCustomizer orchestration class
# ABOUTME: Verifies input validation, ClaudeClient integration, and error handling

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import os

from resume_customizer.core.customizer import ResumeCustomizer
from resume_customizer.config import Settings


class TestResumeCustomizer:
    """Test suite for the simplified ResumeCustomizer class."""
    
    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings(
            claude_api_key="test-api-key-123",
            max_iterations=3
        )
    
    @pytest.fixture
    def temp_files(self):
        """Create temporary test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test resume file
            resume_path = Path(tmpdir) / "test_resume.md"
            resume_path.write_text("# John Doe\n\n## Experience\n- Software Engineer at TechCorp")
            
            # Create test job description file
            job_path = Path(tmpdir) / "test_job.md"
            job_path.write_text("# Senior Software Engineer\n\nRequired: Python, AWS, Leadership")
            
            # Output path (file doesn't exist yet)
            output_path = Path(tmpdir) / "output" / "customized_resume.md"
            
            yield {
                "resume": str(resume_path),
                "job": str(job_path),
                "output": str(output_path),
                "tmpdir": tmpdir
            }
    
    @pytest.fixture
    def mock_claude_client(self):
        """Mock the ClaudeClient class."""
        with patch('resume_customizer.core.customizer.ClaudeClient') as mock_class:
            mock_instance = Mock()
            mock_instance.customize_resume = AsyncMock()
            mock_class.return_value = mock_instance
            yield mock_instance
    
    def test_initialization(self, settings):
        """Test ResumeCustomizer initialization."""
        customizer = ResumeCustomizer(settings)
        
        assert customizer.settings == settings
        assert hasattr(customizer, 'customize')
    
    @pytest.mark.asyncio
    async def test_validates_resume_file_exists(self, settings):
        """Test that resume file existence is validated."""
        customizer = ResumeCustomizer(settings)
        
        with pytest.raises(FileNotFoundError, match="Resume file not found"):
            await customizer.customize(
                resume_path="/nonexistent/resume.md",
                job_description_path="job.md",
                output_path="output.md"
            )
    
    @pytest.mark.asyncio
    async def test_validates_job_file_exists(self, settings, temp_files):
        """Test that job description file existence is validated."""
        customizer = ResumeCustomizer(settings)
        
        with pytest.raises(FileNotFoundError, match="Job description file not found"):
            await customizer.customize(
                resume_path=temp_files["resume"],
                job_description_path="/nonexistent/job.md",
                output_path=temp_files["output"]
            )
    
    @pytest.mark.asyncio
    async def test_calls_claude_client(self, settings, temp_files, mock_claude_client):
        """Test that ClaudeClient is called with correct parameters."""
        customizer = ResumeCustomizer(settings)
        
        # Mock progress callback
        progress_callback = Mock()
        
        await customizer.customize(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"],
            progress_callback=progress_callback
        )
        
        # Verify ClaudeClient was called
        mock_claude_client.customize_resume.assert_called_once()
        
        # Check the arguments (paths might be resolved differently)
        call_args = mock_claude_client.customize_resume.call_args
        assert Path(call_args.kwargs['resume_path']).samefile(temp_files["resume"])
        assert Path(call_args.kwargs['job_description_path']).samefile(temp_files["job"])
        # Output path might not exist yet, so just check the name matches
        assert Path(call_args.kwargs['output_path']).name == Path(temp_files["output"]).name
        assert call_args.kwargs['progress_callback'] == progress_callback
    
    @pytest.mark.asyncio
    async def test_reports_progress(self, settings, temp_files, mock_claude_client):
        """Test that progress is reported during customization."""
        customizer = ResumeCustomizer(settings)
        
        progress_messages = []
        def capture_progress(msg):
            progress_messages.append(msg)
        
        await customizer.customize(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"],
            progress_callback=capture_progress
        )
        
        # Should report validation and completion
        assert any("Validating" in msg for msg in progress_messages)
        assert any("Starting" in msg for msg in progress_messages)
    
    @pytest.mark.asyncio
    async def test_verifies_output_creation(self, settings, temp_files, mock_claude_client):
        """Test that output file creation is verified."""
        customizer = ResumeCustomizer(settings)
        
        # Create output file to simulate successful generation
        output_path = Path(temp_files["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("# Customized Resume")
        
        progress_messages = []
        def capture_progress(msg):
            progress_messages.append(msg)
        
        await customizer.customize(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"],
            progress_callback=capture_progress
        )
        
        # Should report success
        assert any("successfully" in msg.lower() for msg in progress_messages)
    
    @pytest.mark.asyncio
    async def test_reports_output_not_created(self, settings, temp_files, mock_claude_client):
        """Test warning when output file is not created."""
        customizer = ResumeCustomizer(settings)
        
        # Don't create output file to simulate failure
        progress_messages = []
        def capture_progress(msg):
            progress_messages.append(msg)
        
        await customizer.customize(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"],
            progress_callback=capture_progress
        )
        
        # Should report warning
        assert any("warning" in msg.lower() for msg in progress_messages)
    
    @pytest.mark.asyncio
    async def test_handles_claude_errors(self, settings, temp_files, mock_claude_client):
        """Test graceful handling of Claude API errors."""
        customizer = ResumeCustomizer(settings)
        
        # Make Claude client raise an error
        mock_claude_client.customize_resume.side_effect = Exception("Claude API error")
        
        with pytest.raises(Exception, match="Claude API error"):
            await customizer.customize(
                resume_path=temp_files["resume"],
                job_description_path=temp_files["job"],
                output_path=temp_files["output"]
            )
    
    @pytest.mark.asyncio
    async def test_progress_callback_optional(self, settings, temp_files, mock_claude_client):
        """Test that progress callback is optional."""
        customizer = ResumeCustomizer(settings)
        
        # Should not raise error without progress callback
        await customizer.customize(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"]
        )
        
        # Verify ClaudeClient was still called
        assert mock_claude_client.customize_resume.called
    
    @pytest.mark.asyncio
    async def test_creates_output_directory(self, settings, temp_files, mock_claude_client):
        """Test that output directory is created if it doesn't exist."""
        customizer = ResumeCustomizer(settings)
        
        # Use nested output path
        nested_output = str(Path(temp_files["tmpdir"]) / "nested" / "dir" / "output.md")
        
        await customizer.customize(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=nested_output
        )
        
        # Verify directory was created
        assert Path(nested_output).parent.exists()
    
    @pytest.mark.asyncio
    async def test_absolute_path_conversion(self, settings, mock_claude_client):
        """Test that relative paths are converted to absolute."""
        customizer = ResumeCustomizer(settings)
        
        # Create files in a temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files
            resume_file = Path(tmpdir) / "resume.md"
            resume_file.write_text("Resume content")
            
            job_file = Path(tmpdir) / "job.md"
            job_file.write_text("Job content")
            
            # Change to temp directory
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                await customizer.customize(
                    resume_path="resume.md",  # Relative path
                    job_description_path="job.md",  # Relative path
                    output_path="output.md"  # Relative path
                )
                
                # Verify absolute paths were used
                call_args = mock_claude_client.customize_resume.call_args
                assert Path(call_args.kwargs['resume_path']).is_absolute()
                assert Path(call_args.kwargs['job_description_path']).is_absolute()
                assert Path(call_args.kwargs['output_path']).is_absolute()
            finally:
                # Restore working directory
                os.chdir(old_cwd)
    
    @pytest.mark.asyncio
    async def test_customize_returns_output_path(self, settings, temp_files, mock_claude_client):
        """Test that customize returns the output path."""
        customizer = ResumeCustomizer(settings)
        
        result = await customizer.customize(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"]
        )
        
        # The result should be the resolved absolute path
        assert Path(result).name == Path(temp_files["output"]).name
        assert Path(result).is_absolute()
    
    @pytest.mark.asyncio
    async def test_logs_operations(self, settings, temp_files, mock_claude_client):
        """Test that operations are properly logged."""
        with patch('resume_customizer.core.customizer.logger') as mock_logger:
            customizer = ResumeCustomizer(settings)
            
            await customizer.customize(
                resume_path=temp_files["resume"],
                job_description_path=temp_files["job"],
                output_path=temp_files["output"]
            )
            
            # Verify logging calls
            assert mock_logger.info.called
            assert any("Starting resume customization" in str(call) for call in mock_logger.info.call_args_list)
            assert any("Validating input files" in str(call) for call in mock_logger.info.call_args_list)