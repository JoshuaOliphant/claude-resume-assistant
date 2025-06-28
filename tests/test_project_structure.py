# ABOUTME: Test to verify the project structure is set up correctly
# ABOUTME: Checks directories, files, and dependencies exist as expected

import os
import pytest
from pathlib import Path


class TestProjectStructure:
    """Test suite to verify project structure is correctly set up."""
    
    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        # Go up two levels from tests directory
        return Path(__file__).parent.parent
    
    def test_main_directories_exist(self, project_root):
        """Test that main project directories exist."""
        expected_dirs = [
            "src",
            "src/resume_customizer",
            "src/resume_customizer/models",
            "src/resume_customizer/io",
            "src/resume_customizer/core",
            "src/resume_customizer/cli",
            "tests",
            "tests/unit",
            "tests/integration",
            "examples",
            "docs"
        ]
        
        for dir_path in expected_dirs:
            full_path = project_root / dir_path
            assert full_path.exists(), f"Directory {dir_path} does not exist"
            assert full_path.is_dir(), f"{dir_path} is not a directory"
    
    def test_init_files_exist(self, project_root):
        """Test that __init__.py files exist in all packages."""
        package_dirs = [
            "src/resume_customizer",
            "src/resume_customizer/models",
            "src/resume_customizer/io",
            "src/resume_customizer/core",
            "src/resume_customizer/cli"
        ]
        
        for package_dir in package_dirs:
            init_file = project_root / package_dir / "__init__.py"
            assert init_file.exists(), f"__init__.py missing in {package_dir}"
            assert init_file.is_file(), f"__init__.py in {package_dir} is not a file"
    
    def test_configuration_files_exist(self, project_root):
        """Test that configuration files exist."""
        config_files = [
            "pyproject.toml",
            ".env.example",
            ".gitignore"
        ]
        
        for config_file in config_files:
            file_path = project_root / config_file
            assert file_path.exists(), f"Configuration file {config_file} does not exist"
            assert file_path.is_file(), f"{config_file} is not a file"
    
    def test_env_example_content(self, project_root):
        """Test that .env.example contains required placeholder."""
        env_example = project_root / ".env.example"
        content = env_example.read_text()
        assert "ANTHROPIC_API_KEY" in content, "ANTHROPIC_API_KEY not found in .env.example"
    
    def test_pyproject_toml_structure(self, project_root):
        """Test that pyproject.toml has correct structure."""
        import toml
        
        pyproject_path = project_root / "pyproject.toml"
        config = toml.load(pyproject_path)
        
        # Check project metadata
        assert "project" in config, "Project section missing in pyproject.toml"
        assert config["project"]["name"] == "resume-customizer", "Project name incorrect"
        
        # Check dependencies
        assert "dependencies" in config["project"], "Dependencies section missing"
        expected_deps = [
            "click",
            "pydantic",
            "pydantic-settings",
            "claude-code-sdk",
        ]
        
        dependencies = config["project"]["dependencies"]
        for dep in expected_deps:
            assert any(dep in d for d in dependencies), f"Dependency {dep} not found"
        
        # Check dev dependencies
        assert "dependency-groups" in config, "Dependency groups section missing"
        assert "dev" in config["dependency-groups"], "Dev dependencies missing"
        
        dev_deps = config["dependency-groups"]["dev"]
        expected_dev_deps = ["pytest", "pytest-asyncio", "pytest-cov"]
        
        for dep in expected_dev_deps:
            assert any(dep in d for d in dev_deps), f"Dev dependency {dep} not found"
        
        # Check pytest configuration
        assert "tool" in config, "Tool section missing"
        assert "pytest" in config["tool"], "Pytest configuration missing"
        assert "ini_options" in config["tool"]["pytest"], "Pytest ini_options missing"
    
    def test_pytest_configuration(self, project_root):
        """Test that pytest is properly configured."""
        import toml
        
        pyproject_path = project_root / "pyproject.toml"
        config = toml.load(pyproject_path)
        
        pytest_config = config["tool"]["pytest"]["ini_options"]
        
        # Check test paths
        assert "testpaths" in pytest_config, "testpaths not configured"
        assert "tests" in pytest_config["testpaths"], "tests directory not in testpaths"
        
        # Check Python path
        assert "pythonpath" in pytest_config, "pythonpath not configured"
        assert "src" in pytest_config["pythonpath"], "src directory not in pythonpath"
        
        # Check coverage settings
        assert "addopts" in pytest_config, "addopts not configured"
        assert "--cov=resume_customizer" in pytest_config["addopts"], "Coverage not configured for resume_customizer"
    
    def test_package_imports(self):
        """Test that the package can be imported."""
        try:
            import resume_customizer
        except ImportError:
            pytest.fail("Failed to import resume_customizer package")