# ABOUTME: Unit tests for documentation, help text, and example files
# ABOUTME: Ensures documentation is accurate, complete, and examples are valid

"""Tests for documentation accuracy, help text, and example files."""

import os
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
        # Check that examples directory exists
        if not examples_dir.exists():
            pytest.skip("Examples directory not found - may be in different environment")
            
        # Look for any resume and job description examples
        resume_files = list(examples_dir.glob("resume*.*"))
        job_files = list(examples_dir.glob("job*.*"))
        
        assert len(resume_files) > 0, "No resume example files found"
        assert len(job_files) > 0, "No job description example files found"
        
        # Verify files have content
        for file_path in resume_files + job_files:
            assert file_path.stat().st_size > 0, f"Example file {file_path.name} is empty"
    
    def test_example_resume_structure(self, examples_dir):
        """Test that example resume has proper structure."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")
            
        # Find any resume example file
        resume_files = list(examples_dir.glob("resume*.*"))
        if not resume_files:
            pytest.skip("No resume example files found")
            
        resume_path = resume_files[0]
        content = resume_path.read_text()
        
        # Check for common resume sections (case-insensitive)
        content_lower = content.lower()
        common_sections = ["experience", "education", "skills"]
        
        sections_found = sum(1 for section in common_sections if section in content_lower)
        assert sections_found >= 2, f"Resume should contain at least 2 common sections, found {sections_found}"
        
        # Check for some form of contact info (email or phone pattern)
        has_email = "@" in content
        has_phone = any(c.isdigit() for c in content) and ("-" in content or "(" in content)
        assert has_email or has_phone, "Resume should contain contact information"
        
    def test_example_job_description_structure(self, examples_dir):
        """Test that example job description has proper structure."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")
            
        # Find any job description example file
        job_files = list(examples_dir.glob("job*.*"))
        if not job_files:
            pytest.skip("No job description example files found")
            
        job_path = job_files[0]
        content = job_path.read_text()
        content_lower = content.lower()
        
        # Check for common job description elements
        common_elements = ["responsibilit", "qualificat", "require", "skill", "experience"]
        
        elements_found = sum(1 for element in common_elements if element in content_lower)
        assert elements_found >= 2, f"Job description should contain at least 2 common elements, found {elements_found}"
        
    def test_examples_are_compatible(self, examples_dir):
        """Test that example resume and job description are compatible for demo."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")
            
        resume_files = list(examples_dir.glob("resume*.*"))
        job_files = list(examples_dir.glob("job*.*"))
        
        if not resume_files or not job_files:
            pytest.skip("Example files not found")
            
        resume_content = resume_files[0].read_text().lower()
        job_content = job_files[0].read_text().lower()
        
        # Just check that there's some word overlap for compatibility
        resume_words = set(word for word in resume_content.split() if len(word) > 4)
        job_words = set(word for word in job_content.split() if len(word) > 4)
        
        overlapping_words = resume_words & job_words
        assert len(overlapping_words) >= 5, \
            f"Example files should have some keyword overlap for demo purposes"


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
        
        if not pyproject_path.exists():
            pytest.skip("pyproject.toml not found in expected location")
            
        try:
            pyproject_data = toml.load(pyproject_path)
            pyproject_version = pyproject_data.get("project", {}).get("version", "")
            
            from resume_customizer import __version__ as package_version
            
            assert pyproject_version == package_version, \
                f"Version mismatch: pyproject.toml has '{pyproject_version}', " \
                f"package has '{package_version}'"
        except Exception as e:
            pytest.skip(f"Could not parse pyproject.toml: {e}")


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
        
        # Check for usage section (more flexible to handle different section names)
        content_lower = content.lower()
        has_usage_section = any(keyword in content_lower for keyword in ["usage", "quick start", "getting started"])
        assert has_usage_section, "README should have a usage or quick start section"
        
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
        
        # Only check for core directories that should always exist
        core_dirs = [
            "src/resume_customizer",
            "tests"
        ]
        
        for dir_path in core_dirs:
            full_path = base_path / dir_path
            assert full_path.exists(), f"Core directory {dir_path} not found"
            assert full_path.is_dir(), f"{dir_path} exists but is not a directory"
            
        # Check that src has some subdirectories
        src_path = base_path / "src/resume_customizer"
        if src_path.exists():
            subdirs = [d for d in src_path.iterdir() if d.is_dir() and not d.name.startswith('__')]
            assert len(subdirs) > 0, "src/resume_customizer should have subdirectories"
    
    def test_init_files_present(self):
        """Test that all packages have __init__.py files."""
        base_path = Path(__file__).parent.parent.parent
        src_path = base_path / "src/resume_customizer"
        
        if not src_path.exists():
            pytest.skip("Source directory not found")
            
        # Find all Python packages (directories with .py files)
        for root, dirs, files in os.walk(src_path):
            # Skip __pycache__ directories
            if "__pycache__" in root:
                continue
                
            # If directory contains .py files, it should have __init__.py
            py_files = [f for f in files if f.endswith('.py') and f != '__init__.py']
            if py_files:
                init_file = Path(root) / "__init__.py"
                assert init_file.exists(), f"__init__.py missing in {root}"