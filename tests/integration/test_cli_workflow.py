# ABOUTME: Integration tests for full CLI workflow from command line to output
# ABOUTME: Tests the complete user experience including all components working together

"""Integration tests for the complete CLI workflow."""

import pytest
import os
import subprocess
import sys
from pathlib import Path
from click.testing import CliRunner
import tempfile
import time
from unittest.mock import patch

from resume_customizer.cli.app import cli
from resume_customizer.config import Settings
from tests.integration.fixtures import test_data_manager, temp_test_environment, performance_tracker


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping integration tests"
)
class TestCLIWorkflow:
    """Test complete CLI workflows from start to finish."""
    
    def test_basic_cli_flow(self, temp_test_environment):
        """Test basic command-line flow with standard inputs."""
        runner = CliRunner()
        
        # Use test files
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["standard_swe.md"]
        output_path = os.path.join(temp_test_environment["output_dir"], "customized_output.md")
        
        # Run the CLI command
        result = runner.invoke(cli, [
            'customize',
            '--resume', resume_path,
            '--job', job_path,
            '--output', output_path,
            '--iterations', '2'
        ])
        
        # Check CLI execution
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert "Success!" in result.output
        assert output_path in result.output
        
        # Verify output file was created
        assert Path(output_path).exists()
        
        # Verify output content
        output_content = Path(output_path).read_text()
        assert len(output_content) > 100
        assert "Sarah Chen" in output_content  # Name should be preserved
        
    def test_cli_with_verbose_mode(self, temp_test_environment):
        """Test CLI in verbose mode to see detailed progress."""
        runner = CliRunner()
        
        resume_path = temp_test_environment["resumes"]["entry_level.md"]
        job_path = temp_test_environment["jobs"]["standard_swe.md"]
        output_path = os.path.join(temp_test_environment["output_dir"], "verbose_output.md")
        
        # Run with verbose flag
        result = runner.invoke(cli, [
            'customize',
            '-r', resume_path,
            '-j', job_path,
            '-o', output_path,
            '-v',
            '--iterations', '1'
        ])
        
        assert result.exit_code == 0
        
        # Verbose mode should show detailed messages
        assert "Validating input files" in result.output
        assert "Tool: Read" in result.output
        assert "Tool: Write" in result.output
        
    def test_cli_without_output_path(self, temp_test_environment):
        """Test CLI with auto-generated output path."""
        runner = CliRunner()
        
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["standard_swe.md"]
        
        # Run without specifying output
        result = runner.invoke(cli, [
            'customize',
            '--resume', resume_path,
            '--job', job_path,
            '--iterations', '1'
        ])
        
        assert result.exit_code == 0
        assert "Using default output path:" in result.output
        assert "customized_" in result.output
        
        # Extract output path from CLI output
        import re
        match = re.search(r'customized_\d{8}_\d{6}\.md', result.output)
        assert match is not None
        
        # Verify file was created
        output_filename = match.group(0)
        assert Path(output_filename).exists()
        
        # Cleanup
        Path(output_filename).unlink()
        
    def test_cli_with_multiple_iterations(self, temp_test_environment, performance_tracker):
        """Test CLI with multiple iterations and measure performance."""
        runner = CliRunner()
        performance_tracker.start()
        
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["senior_role.md"]
        output_path = os.path.join(temp_test_environment["output_dir"], "multi_iteration.md")
        
        # Run with 3 iterations
        result = runner.invoke(cli, [
            'customize',
            '--resume', resume_path,
            '--job', job_path,
            '--output', output_path,
            '--iterations', '3',
            '--verbose'
        ])
        
        performance_tracker.stop()
        
        assert result.exit_code == 0
        
        # Check output quality improved with iterations
        output_content = Path(output_path).read_text()
        
        # Should have integrated senior-level keywords
        senior_keywords = ["architect", "distributed systems", "technical lead", "mentoring"]
        keywords_found = sum(1 for kw in senior_keywords if kw.lower() in output_content.lower())
        assert keywords_found >= 2, "Should integrate senior-level keywords"
        
        # Print performance summary
        summary = performance_tracker.get_summary()
        print(f"\nPerformance Summary:")
        print(f"  Duration: {summary['duration_seconds']:.2f} seconds")
        print(f"  Iterations: 3")
        
    def test_cli_error_handling(self, temp_test_environment):
        """Test CLI error handling for various scenarios."""
        runner = CliRunner()
        
        # Test with non-existent resume file
        result = runner.invoke(cli, [
            'customize',
            '--resume', '/nonexistent/resume.md',
            '--job', temp_test_environment["jobs"]["standard_swe.md"],
            '--output', 'output.md'
        ])
        
        assert result.exit_code != 0
        assert "Resume file not found" in result.output
        
        # Test with non-existent job file
        result = runner.invoke(cli, [
            'customize',
            '--resume', temp_test_environment["resumes"]["mid_level.md"],
            '--job', '/nonexistent/job.md',
            '--output', 'output.md'
        ])
        
        assert result.exit_code != 0
        assert "Job description file not found" in result.output
        
    def test_cli_with_minimal_inputs(self, temp_test_environment):
        """Test CLI with minimal resume and job description."""
        runner = CliRunner()
        
        resume_path = temp_test_environment["resumes"]["minimal.md"]
        job_path = temp_test_environment["jobs"]["minimal_posting.md"]
        output_path = os.path.join(temp_test_environment["output_dir"], "minimal_output.md")
        
        result = runner.invoke(cli, [
            'customize',
            '--resume', resume_path,
            '--job', job_path,
            '--output', output_path,
            '--iterations', '2'
        ])
        
        assert result.exit_code == 0
        
        # Should still produce meaningful output
        output_content = Path(output_path).read_text()
        assert len(output_content) > len(Path(resume_path).read_text())
        assert "Jane Doe" in output_content
        
    def test_cli_with_environment_variable(self):
        """Test CLI picks up API key from environment."""
        runner = CliRunner()
        
        # Create minimal test files inline
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_path = Path(tmpdir) / "resume.md"
            resume_path.write_text("# Test User\nSoftware Developer")
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Looking for a Python developer")
            
            output_path = Path(tmpdir) / "output.md"
            
            # Ensure API key is set
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            assert api_key, "API key should be set for integration tests"
            
            # Run command
            result = runner.invoke(cli, [
                'customize',
                '--resume', str(resume_path),
                '--job', str(job_path),
                '--output', str(output_path),
                '--iterations', '1'
            ])
            
            assert result.exit_code == 0
            assert output_path.exists()
            
    def test_subprocess_invocation(self, temp_test_environment):
        """Test invoking the CLI through subprocess (real command-line experience)."""
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["standard_swe.md"]
        output_path = os.path.join(temp_test_environment["output_dir"], "subprocess_output.md")
        
        # Build command
        cmd = [
            sys.executable,
            "resume_customizer.py",
            "customize",
            "--resume", resume_path,
            "--job", job_path,
            "--output", output_path,
            "--iterations", "1"
        ]
        
        # Run from project root
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            env={**os.environ, "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", "")}
        )
        
        # Check execution
        assert result.returncode == 0, f"Subprocess failed: {result.stderr}"
        assert "Success!" in result.stdout
        assert Path(output_path).exists()
        
    def test_cli_progress_display(self, temp_test_environment):
        """Test that progress display works correctly."""
        runner = CliRunner()
        
        resume_path = temp_test_environment["resumes"]["mid_level.md"]
        job_path = temp_test_environment["jobs"]["standard_swe.md"]
        output_path = os.path.join(temp_test_environment["output_dir"], "progress_test.md")
        
        # Capture output in real-time
        result = runner.invoke(cli, [
            'customize',
            '--resume', resume_path,
            '--job', job_path,
            '--output', output_path,
            '--iterations', '1'
        ], catch_exceptions=False)
        
        assert result.exit_code == 0
        
        # Should show completion
        assert "✓" in result.output or "Completed" in result.output
        
    def test_cli_with_special_characters(self, temp_test_environment):
        """Test CLI handles file paths with special characters."""
        runner = CliRunner()
        
        # Create files with special characters in names
        special_dir = Path(temp_test_environment["base_path"]) / "special files & chars"
        special_dir.mkdir()
        
        resume_path = special_dir / "resume (copy).md"
        resume_path.write_text("# Test User\nDeveloper")
        
        job_path = special_dir / "job - posting.md"
        job_path.write_text("Python developer needed")
        
        output_path = special_dir / "output [final].md"
        
        result = runner.invoke(cli, [
            'customize',
            '--resume', str(resume_path),
            '--job', str(job_path),
            '--output', str(output_path),
            '--iterations', '1'
        ])
        
        assert result.exit_code == 0
        assert output_path.exists()
        
    @pytest.mark.slow
    def test_cli_performance_benchmark(self, temp_test_environment, performance_tracker):
        """Benchmark CLI performance with different input sizes."""
        runner = CliRunner()
        
        test_cases = [
            ("minimal", temp_test_environment["resumes"]["minimal.md"]),
            ("entry", temp_test_environment["resumes"]["entry_level.md"]),
            ("mid", temp_test_environment["resumes"]["mid_level.md"]),
            ("senior", temp_test_environment["resumes"]["senior_level.md"])
        ]
        
        job_path = temp_test_environment["jobs"]["standard_swe.md"]
        
        results = {}
        
        for label, resume_path in test_cases:
            output_path = os.path.join(
                temp_test_environment["output_dir"], 
                f"benchmark_{label}.md"
            )
            
            start_time = time.time()
            
            result = runner.invoke(cli, [
                'customize',
                '--resume', resume_path,
                '--job', job_path,
                '--output', output_path,
                '--iterations', '1'
            ])
            
            end_time = time.time()
            
            if result.exit_code == 0:
                duration = end_time - start_time
                input_size = len(Path(resume_path).read_text())
                output_size = len(Path(output_path).read_text())
                
                results[label] = {
                    "duration": duration,
                    "input_size": input_size,
                    "output_size": output_size,
                    "expansion_ratio": output_size / input_size
                }
        
        # Print benchmark results
        print("\n=== Performance Benchmark Results ===")
        for label, metrics in results.items():
            print(f"\n{label.upper()} Resume:")
            print(f"  Duration: {metrics['duration']:.2f}s")
            print(f"  Input size: {metrics['input_size']} chars")
            print(f"  Output size: {metrics['output_size']} chars")
            print(f"  Expansion ratio: {metrics['expansion_ratio']:.2f}x")
        
        # Verify reasonable performance
        for metrics in results.values():
            assert metrics['duration'] < 60, "Should complete within 60 seconds"
            assert metrics['expansion_ratio'] >= 0.8, "Should not lose content"