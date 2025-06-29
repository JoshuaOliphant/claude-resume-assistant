# ABOUTME: Test suite for the Click CLI application interface
# ABOUTME: Verifies command parsing, argument validation, and output formatting

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock, AsyncMock
from pathlib import Path
import tempfile

from resume_customizer.cli.app import cli, customize


class TestCLI:
    """Test suite for the Click CLI application."""
    
    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()
    
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
            
            # Output path (doesn't exist yet)
            output_path = Path(tmpdir) / "customized_resume.md"
            
            yield {
                "resume": str(resume_path),
                "job": str(job_path),
                "output": str(output_path),
                "tmpdir": tmpdir
            }
    
    def test_cli_exists(self):
        """Test that CLI command group exists."""
        assert cli is not None
        assert hasattr(cli, 'commands')
    
    def test_customize_command_exists(self, runner):
        """Test that customize command exists."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'customize' in result.output
    
    def test_customize_requires_arguments(self, runner):
        """Test that customize command requires arguments."""
        result = runner.invoke(cli, ['customize'])
        assert result.exit_code != 0
        assert 'Missing option' in result.output
    
    def test_customize_help(self, runner):
        """Test customize command help text."""
        result = runner.invoke(cli, ['customize', '--help'])
        assert result.exit_code == 0
        assert '--resume' in result.output
        assert '--job' in result.output
        assert '--output' in result.output
        assert '--verbose' in result.output
    
    def test_validate_missing_resume_file(self, runner, temp_files):
        """Test validation when resume file doesn't exist."""
        result = runner.invoke(cli, [
            'customize',
            '--resume', '/nonexistent/resume.md',
            '--job', temp_files['job'],
            '--output', temp_files['output']
        ])
        assert result.exit_code != 0
        assert 'Resume file not found' in result.output
    
    def test_validate_missing_job_file(self, runner, temp_files):
        """Test validation when job description file doesn't exist."""
        result = runner.invoke(cli, [
            'customize',
            '--resume', temp_files['resume'],
            '--job', '/nonexistent/job.md',
            '--output', temp_files['output']
        ])
        assert result.exit_code != 0
        assert 'Job description file not found' in result.output
    
    @patch('resume_customizer.cli.app.ResumeCustomizer')
    def test_successful_customization(self, mock_customizer_class, runner, temp_files):
        """Test successful resume customization."""
        # Mock the customizer
        mock_customizer = Mock()
        mock_customizer.customize = AsyncMock(return_value=temp_files['output'])
        mock_customizer_class.return_value = mock_customizer
        
        # Create output file to simulate success
        Path(temp_files['output']).write_text("# Customized Resume")
        
        result = runner.invoke(cli, [
            'customize',
            '--resume', temp_files['resume'],
            '--job', temp_files['job'],
            '--output', temp_files['output']
        ])
        
        assert result.exit_code == 0
        assert '✓' in result.output or 'Success' in result.output
        assert temp_files['output'] in result.output
    
    @patch('resume_customizer.cli.app.ResumeCustomizer')
    def test_verbose_mode(self, mock_customizer_class, runner, temp_files):
        """Test verbose mode shows detailed progress."""
        # Mock the customizer
        mock_customizer = Mock()
        
        # Capture progress callbacks
        progress_messages = []
        async def mock_customize(**kwargs):
            if 'progress_callback' in kwargs and kwargs['progress_callback']:
                kwargs['progress_callback']("Validating input files...")
                kwargs['progress_callback']("Starting customization...")
                kwargs['progress_callback']("Tool: Read - resume.md")
                kwargs['progress_callback']("Tool: Write - output.md")
            return temp_files['output']
        
        mock_customizer.customize = mock_customize
        mock_customizer_class.return_value = mock_customizer
        
        result = runner.invoke(cli, [
            'customize',
            '--resume', temp_files['resume'],
            '--job', temp_files['job'],
            '--output', temp_files['output'],
            '--verbose'
        ])
        
        assert result.exit_code == 0
        assert 'Validating input files' in result.output
        assert 'Starting customization' in result.output
        assert 'Tool: Read' in result.output
    
    @patch('resume_customizer.cli.app.ResumeCustomizer')
    def test_non_verbose_mode(self, mock_customizer_class, runner, temp_files):
        """Test non-verbose mode shows minimal output."""
        # Mock the customizer
        mock_customizer = Mock()
        mock_customizer.customize = AsyncMock(return_value=temp_files['output'])
        mock_customizer_class.return_value = mock_customizer
        
        result = runner.invoke(cli, [
            'customize',
            '--resume', temp_files['resume'],
            '--job', temp_files['job'],
            '--output', temp_files['output']
        ])
        
        assert result.exit_code == 0
        # Should not show detailed progress
        assert 'Tool: Read' not in result.output
        assert 'Validating input files' not in result.output
    
    @patch('resume_customizer.cli.app.ResumeCustomizer')
    def test_error_handling(self, mock_customizer_class, runner, temp_files):
        """Test error handling and display."""
        # Mock the customizer to raise an error
        mock_customizer = Mock()
        mock_customizer.customize = AsyncMock(side_effect=Exception("API error occurred"))
        mock_customizer_class.return_value = mock_customizer
        
        result = runner.invoke(cli, [
            'customize',
            '--resume', temp_files['resume'],
            '--job', temp_files['job'],
            '--output', temp_files['output']
        ])
        
        assert result.exit_code != 0
        assert 'Error' in result.output
        assert 'API error occurred' in result.output
    
    def test_short_options(self, runner, temp_files):
        """Test short option flags work."""
        with patch('resume_customizer.cli.app.ResumeCustomizer') as mock_class:
            mock_customizer = Mock()
            mock_customizer.customize = AsyncMock(return_value=temp_files['output'])
            mock_class.return_value = mock_customizer
            
            result = runner.invoke(cli, [
                'customize',
                '-r', temp_files['resume'],
                '-j', temp_files['job'],
                '-o', temp_files['output'],
                '-v'
            ])
            
            assert result.exit_code == 0
    
    def test_default_output_path(self, runner, temp_files):
        """Test default output path generation."""
        with patch('resume_customizer.cli.app.ResumeCustomizer') as mock_class:
            mock_customizer = Mock()
            
            # Capture the actual output path used
            actual_output_path = None
            async def capture_output(**kwargs):
                nonlocal actual_output_path
                actual_output_path = kwargs['output_path']
                return kwargs['output_path']
            
            mock_customizer.customize = capture_output
            mock_class.return_value = mock_customizer
            
            result = runner.invoke(cli, [
                'customize',
                '--resume', temp_files['resume'],
                '--job', temp_files['job']
            ])
            
            assert result.exit_code == 0
            assert actual_output_path is not None
            assert 'customized_' in actual_output_path
            assert actual_output_path.endswith('.md')
    
    def test_iterations_option(self, runner, temp_files):
        """Test iterations option is passed to settings."""
        with patch('resume_customizer.cli.app.Settings') as mock_settings_class:
            with patch('resume_customizer.cli.app.ResumeCustomizer') as mock_customizer_class:
                mock_customizer = Mock()
                mock_customizer.customize = AsyncMock(return_value=temp_files['output'])
                mock_customizer_class.return_value = mock_customizer
                
                result = runner.invoke(cli, [
                    'customize',
                    '--resume', temp_files['resume'],
                    '--job', temp_files['job'],
                    '--output', temp_files['output'],
                    '--iterations', '5'
                ])
                
                assert result.exit_code == 0
                # Check that Settings was called with max_iterations=5
                mock_settings_class.assert_called_once()
                assert mock_settings_class.call_args.kwargs['max_iterations'] == 5
    
    def test_invalid_iterations(self, runner, temp_files):
        """Test invalid iterations value."""
        result = runner.invoke(cli, [
            'customize',
            '--resume', temp_files['resume'],
            '--job', temp_files['job'],
            '--output', temp_files['output'],
            '--iterations', '0'
        ])
        
        assert result.exit_code != 0
        assert 'Invalid value' in result.output or 'Range' in result.output
    
    def test_progress_spinner(self, runner, temp_files):
        """Test that progress spinner is shown during customization."""
        with patch('resume_customizer.cli.app.ResumeCustomizer') as mock_class:
            mock_customizer = Mock()
            
            # Simulate a slow operation
            import asyncio
            async def slow_customize(**kwargs):
                await asyncio.sleep(0.1)
                return temp_files['output']
            
            mock_customizer.customize = slow_customize
            mock_class.return_value = mock_customizer
            
            result = runner.invoke(cli, [
                'customize',
                '--resume', temp_files['resume'],
                '--job', temp_files['job'],
                '--output', temp_files['output']
            ])
            
            assert result.exit_code == 0
            # Should show completion message
            assert '✓' in result.output or 'Completed' in result.output
    
    def test_api_key_from_env(self, runner, temp_files):
        """Test that API key is loaded from environment."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key-123'}):
            with patch('resume_customizer.cli.app.ResumeCustomizer') as mock_class:
                with patch('resume_customizer.cli.app.Settings') as mock_settings_class:
                    mock_customizer = Mock()
                    mock_customizer.customize = AsyncMock(return_value=temp_files['output'])
                    mock_class.return_value = mock_customizer
                    
                    result = runner.invoke(cli, [
                        'customize',
                        '--resume', temp_files['resume'],
                        '--job', temp_files['job'],
                        '--output', temp_files['output']
                    ])
                    
                    assert result.exit_code == 0
                    # Settings should be created with API key from env
                    mock_settings_class.assert_called_once()
    
    def test_missing_api_key(self, runner, temp_files):
        """Test error when API key is missing."""
        with patch.dict('os.environ', {}, clear=True):
            # Remove API key from environment
            import os
            os.environ.pop('ANTHROPIC_API_KEY', None)
            
            result = runner.invoke(cli, [
                'customize',
                '--resume', temp_files['resume'],
                '--job', temp_files['job'],
                '--output', temp_files['output']
            ])
            
            assert result.exit_code != 0
            assert 'API key' in result.output or 'ANTHROPIC_API_KEY' in result.output