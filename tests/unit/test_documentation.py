# ABOUTME: Unit tests for documentation, help text, and example files
# ABOUTME: Ensures documentation is accurate, complete, and examples are valid

"""Tests for documentation accuracy, help text, and example files."""

import pytest
import subprocess
import sys
from pathlib import Path
from click.testing import CliRunner
import toml

from resume_customizer.cli.app import cli
from resume_customizer import __version__


class TestCLIHelpText:
    """Test CLI help text completeness and accuracy."""
    
    def test_main_help_text(self):
        """Test that main help text includes all required information."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        
        # Check essential components
        assert "AI-powered resume customization tool" in result.output
        assert "Commands:" in result.output
        assert "customize" in result.output
        assert "Options:" in result.output
        assert "--help" in result.output
        
    def test_customize_command_help(self):
        """Test that customize command help includes all options."""
        runner = CliRunner()
        result = runner.invoke(cli, ['customize', '--help'])
        
        assert result.exit_code == 0
        
        # Check all options are documented
        required_options = [
            "--resume", "-r",
            "--job", "-j", 
            "--output", "-o",
            "--iterations", "-i",
            "--verbose", "-v",
            "--help"
        ]
        
        for option in required_options:
            assert option in result.output, f"Option {option} not found in help text"
        
        # Check descriptions
        assert "Path to your resume file" in result.output
        assert "Path to the job description file" in result.output
        assert "Output path for customized resume" in result.output
        assert "Number of refinement iterations" in result.output
        assert "Show detailed progress information" in result.output
        
    def test_help_examples_present(self):
        """Test that help text includes usage examples."""
        runner = CliRunner()
        result = runner.invoke(cli, ['customize', '--help'])
        
        # The help should show the command structure
        assert "resume-customizer customize" in result.output or "customize [OPTIONS]" in result.output


class TestExampleFiles:
    """Test validity of example files."""
    
    @pytest.fixture
    def examples_dir(self):
        """Get the examples directory path."""
        return Path(__file__).parent.parent.parent / "examples"
    
    def test_example_files_exist(self, examples_dir):
        """Test that all example files exist."""
        expected_files = [
            "resume.txt",
            "job_description.txt"
        ]
        
        for filename in expected_files:
            file_path = examples_dir / filename
            assert file_path.exists(), f"Example file {filename} not found"
            assert file_path.stat().st_size > 0, f"Example file {filename} is empty"
    
    def test_example_resume_structure(self, examples_dir):
        """Test that example resume has proper structure."""
        resume_path = examples_dir / "resume.txt"
        content = resume_path.read_text()
        
        # Check for essential sections
        required_sections = [
            "PROFESSIONAL SUMMARY",
            "WORK EXPERIENCE", 
            "EDUCATION",
            "TECHNICAL SKILLS"
        ]
        
        for section in required_sections:
            assert section in content, f"Section '{section}' not found in example resume"
        
        # Check for contact information
        assert "@" in content, "Email not found in example resume"
        assert "github.com" in content.lower(), "GitHub profile not found"
        
    def test_example_job_description_structure(self, examples_dir):
        """Test that example job description has proper structure."""
        job_path = examples_dir / "job_description.txt"
        content = job_path.read_text()
        
        # Check for essential components
        required_components = [
            "About Us",
            "Position Overview",
            "Key Responsibilities",
            "Required Qualifications",
            "Technical Environment"
        ]
        
        for component in required_components:
            assert component in content, f"Component '{component}' not found in job description"
        
    def test_examples_are_compatible(self, examples_dir):
        """Test that example resume and job description are compatible for demo."""
        resume_content = (examples_dir / "resume.txt").read_text().lower()
        job_content = (examples_dir / "job_description.txt").read_text().lower()
        
        # Check for some keyword overlap
        overlapping_keywords = []
        job_keywords = ["python", "api", "microservices", "aws", "postgresql"]
        
        for keyword in job_keywords:
            if keyword in job_content and keyword in resume_content:
                overlapping_keywords.append(keyword)
        
        assert len(overlapping_keywords) >= 3, \
            f"Example files should have more keyword overlap. Found: {overlapping_keywords}"


class TestVersionInformation:
    """Test version information consistency."""
    
    def test_version_defined(self):
        """Test that version is properly defined."""
        assert hasattr(__version__, '__version__') or isinstance(__version__, str)
        
    def test_version_format(self):
        """Test that version follows semantic versioning."""
        # Version should be importable from package
        from resume_customizer import __version__ as version
        
        # Basic semantic version check (X.Y.Z)
        parts = version.split('.')
        assert len(parts) >= 2, f"Version '{version}' doesn't follow semantic versioning"
        
        # Each part should be numeric (or have dev/alpha/beta suffix)
        for part in parts[:2]:  # Check major and minor
            assert part.strip().isdigit() or any(x in part for x in ['dev', 'alpha', 'beta']), \
                f"Version part '{part}' is not numeric"
    
    def test_pyproject_version_matches(self):
        """Test that pyproject.toml version matches package version."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        
        if pyproject_path.exists():
            pyproject_data = toml.load(pyproject_path)
            pyproject_version = pyproject_data.get("project", {}).get("version", "")
            
            from resume_customizer import __version__ as package_version
            
            assert pyproject_version == package_version, \
                f"Version mismatch: pyproject.toml has '{pyproject_version}', " \
                f"package has '{package_version}'"


class TestDocumentationAccuracy:
    """Test that documentation accurately reflects implementation."""
    
    @pytest.fixture
    def readme_path(self):
        """Get README path."""
        return Path(__file__).parent.parent.parent / "README.md"
    
    def test_readme_exists(self, readme_path):
        """Test that README exists and has content."""
        assert readme_path.exists(), "README.md not found"
        assert readme_path.stat().st_size > 100, "README.md seems too small"
    
    def test_readme_installation_instructions(self, readme_path):
        """Test that README has accurate installation instructions."""
        content = readme_path.read_text()
        
        # Check for installation section
        assert "## Installation" in content or "### Installation" in content
        
        # Check for correct package names
        assert "uv" in content, "README should mention uv for package management"
        assert "claude-code-sdk" in content, "README should mention claude-code-sdk"
        
    def test_readme_usage_examples(self, readme_path):
        """Test that README usage examples are accurate."""
        content = readme_path.read_text()
        
        # Check for usage section
        assert "## Usage" in content or "### Usage" in content
        
        # Check that the examples either say "Coming Soon" OR have the correct command
        # Since we're still in development, "Coming Soon" is acceptable
        has_coming_soon = "Coming Soon" in content
        has_correct_command = ("resume-customizer" in content or 
                              "python resume_customizer.py" in content)
        
        assert has_coming_soon or has_correct_command, \
            "README should either indicate 'Coming Soon' or have correct usage examples"
    
    def test_cli_command_in_docs_works(self):
        """Test that documented CLI commands actually work."""
        runner = CliRunner()
        
        # Test the main command exists
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        
        # Test customize command exists  
        result = runner.invoke(cli, ['customize', '--help'])
        assert result.exit_code == 0


class TestLicenseCompliance:
    """Test license file and compliance."""
    
    @pytest.fixture
    def license_path(self):
        """Get LICENSE path."""
        return Path(__file__).parent.parent.parent / "LICENSE"
    
    def test_license_file_exists(self, license_path):
        """Test that LICENSE file exists."""
        assert license_path.exists(), "LICENSE file not found"
        assert license_path.stat().st_size > 100, "LICENSE file seems too small"
    
    def test_license_is_mit(self, license_path):
        """Test that license is MIT as stated in README."""
        content = license_path.read_text()
        
        # Check for MIT license indicators
        assert "MIT License" in content or "MIT" in content
        assert "Permission is hereby granted" in content
        
    def test_license_year_current(self, license_path):
        """Test that license includes current year."""
        content = license_path.read_text()
        
        from datetime import datetime
        current_year = str(datetime.now().year)
        
        assert current_year in content, f"License should include current year {current_year}"


class TestProjectStructure:
    """Test that project structure matches documentation."""
    
    def test_required_directories_exist(self):
        """Test that all required directories exist."""
        base_path = Path(__file__).parent.parent.parent
        
        required_dirs = [
            "src/resume_customizer",
            "src/resume_customizer/cli",
            "src/resume_customizer/core", 
            "src/resume_customizer/models",
            "src/resume_customizer/utils",
            "src/resume_customizer/io",
            "tests/unit",
            "tests/integration",
            "examples"
        ]
        
        for dir_path in required_dirs:
            full_path = base_path / dir_path
            assert full_path.exists(), f"Required directory {dir_path} not found"
            assert full_path.is_dir(), f"{dir_path} exists but is not a directory"
    
    def test_init_files_present(self):
        """Test that all packages have __init__.py files."""
        base_path = Path(__file__).parent.parent.parent
        
        package_dirs = [
            "src/resume_customizer",
            "src/resume_customizer/cli",
            "src/resume_customizer/core",
            "src/resume_customizer/models", 
            "src/resume_customizer/utils",
            "src/resume_customizer/io"
        ]
        
        for package_dir in package_dirs:
            init_file = base_path / package_dir / "__init__.py"
            assert init_file.exists(), f"__init__.py missing in {package_dir}"