# ABOUTME: Test suite for the ClaudeClient wrapper using Claude Code SDK
# ABOUTME: Verifies file operations, message processing, and error handling

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import tempfile
import os

from resume_customizer.core.claude_client import ClaudeClient
from resume_customizer.config import Settings
from claude_code_sdk import ClaudeCodeOptions


class TestClaudeClient:
    """Test suite for ClaudeClient class using Claude Code SDK."""
    
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
            resume_path.write_text("# John Doe\n\n## Experience\n- Software Engineer")
            
            # Create test job description file
            job_path = Path(tmpdir) / "test_job.md"
            job_path.write_text("# Senior Software Engineer\n\nRequired: Python, AWS")
            
            # Output path
            output_path = Path(tmpdir) / "customized_resume.md"
            
            yield {
                "resume": str(resume_path),
                "job": str(job_path),
                "output": str(output_path),
                "tmpdir": tmpdir
            }
    
    @pytest.fixture
    def mock_query(self):
        """Mock the claude_code_sdk.query function."""
        with patch('resume_customizer.core.claude_client.query') as mock:
            yield mock
    
    def test_initialization(self, settings):
        """Test client initialization with settings."""
        client = ClaudeClient(settings)
        
        assert client.settings == settings
        assert client.settings.claude_api_key is not None
        assert len(client.settings.claude_api_key) > 0
    
    def test_initialization_without_api_key(self):
        """Test initialization fails without API key."""
        mock_settings = Mock()
        mock_settings.claude_api_key = ""
        
        with pytest.raises(ValueError, match="Claude API key is required"):
            ClaudeClient(mock_settings)
    
    @pytest.mark.asyncio
    async def test_customize_resume_success(self, settings, temp_files, mock_query):
        """Test successful resume customization."""
        # Create mock messages that simulate Claude's file operations
        # Use simple mock objects since we're just testing message processing
        # Create content blocks with proper attributes
        text_block1 = Mock()
        text_block1.text = "I'll help you customize your resume. Let me read the files first."
        text_block1.name = None
        
        tool_block1 = Mock()
        tool_block1.name = "Read"
        tool_block1.text = None
        tool_block1.input = {"path": temp_files["resume"]}
        
        text_block2 = Mock()
        text_block2.text = "File read successfully"
        text_block2.name = None
        
        tool_block2 = Mock()
        tool_block2.name = "Read"
        tool_block2.text = None
        tool_block2.input = {"path": temp_files["job"]}
        
        text_block3 = Mock()
        text_block3.text = "File read successfully"
        text_block3.name = None
        
        text_block4 = Mock()
        text_block4.text = "Analyzing job requirements and customizing resume..."
        text_block4.name = None
        
        tool_block3 = Mock()
        tool_block3.name = "Write"
        tool_block3.text = None
        tool_block3.input = {
            "path": temp_files["output"],
            "content": "# John Doe\n\n## Experience\n- Senior Software Engineer with Python and AWS"
        }
        
        text_block5 = Mock()
        text_block5.text = "File written successfully"
        text_block5.name = None
        
        text_block6 = Mock()
        text_block6.text = "Resume customization completed successfully!"
        text_block6.name = None
        
        messages = [
            Mock(content=[text_block1]),
            Mock(content=[tool_block1]),
            Mock(content=[text_block2]),
            Mock(content=[tool_block2]),
            Mock(content=[text_block3]),
            Mock(content=[text_block4]),
            Mock(content=[tool_block3]),
            Mock(content=[text_block5]),
            Mock(content=[text_block6])
        ]
        
        # Mock query to return our messages
        async def mock_query_generator(*args, **kwargs):
            for msg in messages:
                yield msg
        
        mock_query.return_value = mock_query_generator()
        
        client = ClaudeClient(settings)
        
        # Track progress messages
        progress_messages = []
        def progress_callback(msg):
            progress_messages.append(msg)
        
        # Run customization
        await client.customize_resume(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"],
            progress_callback=progress_callback
        )
        
        # Verify query was called correctly
        mock_query.assert_called_once()
        call_args = mock_query.call_args
        
        # Check prompt contains file paths
        prompt = call_args[0][0]  # First positional argument
        assert temp_files["resume"] in prompt
        assert temp_files["job"] in prompt
        assert temp_files["output"] in prompt
        
        # Check ClaudeCodeOptions
        options = call_args[1]["options"]
        assert isinstance(options, ClaudeCodeOptions)
        assert "Read" in options.allowed_tools
        assert "Write" in options.allowed_tools
        assert options.max_turns == 1
        
        # Check progress messages
        assert len(progress_messages) > 0
        assert any("read" in msg.lower() for msg in progress_messages)
        assert any("write" in msg.lower() for msg in progress_messages)
    
    @pytest.mark.asyncio
    async def test_file_validation(self, settings, temp_files):
        """Test that file paths are validated before calling Claude."""
        client = ClaudeClient(settings)
        
        # Test with non-existent resume file
        with pytest.raises(FileNotFoundError, match="Resume file not found"):
            await client.customize_resume(
                resume_path="/nonexistent/resume.md",
                job_description_path=temp_files["job"],
                output_path=temp_files["output"]
            )
        
        # Test with non-existent job description file
        with pytest.raises(FileNotFoundError, match="Job description file not found"):
            await client.customize_resume(
                resume_path=temp_files["resume"],
                job_description_path="/nonexistent/job.md",
                output_path=temp_files["output"]
            )
    
    @pytest.mark.asyncio
    async def test_output_directory_creation(self, settings, temp_files, mock_query):
        """Test that output directory is created if it doesn't exist."""
        # Create a nested output path
        output_path = os.path.join(temp_files["tmpdir"], "nested", "dir", "output.md")
        
        # Mock successful execution
        async def mock_query_generator(*args, **kwargs):
            yield Mock(content=[Mock(text="Done")])
        
        mock_query.return_value = mock_query_generator()
        
        client = ClaudeClient(settings)
        
        await client.customize_resume(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=output_path
        )
        
        # Verify directory was created
        assert Path(output_path).parent.exists()
    
    @pytest.mark.asyncio
    async def test_tool_usage_tracking(self, settings, temp_files, mock_query):
        """Test that tool usage is tracked and reported."""
        # Create proper mock tool blocks
        tool1 = Mock()
        tool1.name = "Read"
        tool1.text = None
        tool1.input = {"path": "file1.md"}
        
        tool2 = Mock()
        tool2.name = "Read"
        tool2.text = None
        tool2.input = {"path": "file2.md"}
        
        tool3 = Mock()
        tool3.name = "Write"
        tool3.text = None
        tool3.input = {"path": "output.md", "content": "test"}
        
        messages = [
            Mock(content=[tool1]),
            Mock(content=[tool2]),
            Mock(content=[tool3])
        ]
        
        async def mock_query_generator(*args, **kwargs):
            for msg in messages:
                yield msg
        
        mock_query.return_value = mock_query_generator()
        
        client = ClaudeClient(settings)
        
        tool_usage = []
        def progress_callback(msg):
            if "Tool:" in msg:
                tool_usage.append(msg)
        
        await client.customize_resume(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"],
            progress_callback=progress_callback
        )
        
        # Should track 2 reads and 1 write
        assert len(tool_usage) == 3
        assert sum(1 for msg in tool_usage if "Read" in msg) == 2
        assert sum(1 for msg in tool_usage if "Write" in msg) == 1
    
    @pytest.mark.asyncio
    async def test_error_handling(self, settings, temp_files, mock_query):
        """Test error handling during Claude execution."""
        # Mock an error during execution
        async def mock_query_generator(*args, **kwargs):
            yield Mock(content=[Mock(text="Starting...")])
            raise Exception("Claude API error")
        
        mock_query.return_value = mock_query_generator()
        
        client = ClaudeClient(settings)
        
        with pytest.raises(Exception, match="Claude API error"):
            await client.customize_resume(
                resume_path=temp_files["resume"],
                job_description_path=temp_files["job"],
                output_path=temp_files["output"]
            )
    
    @pytest.mark.asyncio
    async def test_progress_callback_optional(self, settings, temp_files, mock_query):
        """Test that progress callback is optional."""
        async def mock_query_generator(*args, **kwargs):
            yield Mock(content=[Mock(text="Done")])
        
        mock_query.return_value = mock_query_generator()
        
        client = ClaudeClient(settings)
        
        # Should not raise error without progress callback
        await client.customize_resume(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"]
        )
    
    def test_build_orchestrator_prompt(self, settings, temp_files):
        """Test orchestrator prompt building."""
        client = ClaudeClient(settings)
        
        prompt = client._build_orchestrator_prompt(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"]
        )
        
        # Verify prompt contains necessary elements
        assert "orchestrator" in prompt.lower()
        assert "sub-agent" in prompt.lower()
        assert temp_files["resume"] in prompt
        assert temp_files["job"] in prompt
        assert temp_files["output"] in prompt
        assert "truthfulness" in prompt.lower()
        assert "ats" in prompt.lower()
        assert "iterate" in prompt.lower() or "iteration" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_output_verification(self, settings, temp_files, mock_query):
        """Test that output file creation is verified."""
        # Mock messages without writing the file
        messages = [
            Mock(content=[Mock(text="Processing...")]),
            Mock(content=[Mock(text="Done")])
        ]
        
        async def mock_query_generator(*args, **kwargs):
            for msg in messages:
                yield msg
        
        mock_query.return_value = mock_query_generator()
        
        client = ClaudeClient(settings)
        
        # Should warn if output file wasn't created
        warnings = []
        def progress_callback(msg):
            if "warning" in msg.lower():
                warnings.append(msg)
        
        await client.customize_resume(
            resume_path=temp_files["resume"],
            job_description_path=temp_files["job"],
            output_path=temp_files["output"],
            progress_callback=progress_callback
        )
        
        # Should have a warning about output file not created
        assert len(warnings) > 0