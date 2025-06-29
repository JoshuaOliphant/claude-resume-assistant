# ABOUTME: Integration tests for file I/O operations and edge cases
# ABOUTME: Tests file handling, encoding, permissions, and various file system scenarios

"""Integration tests for file I/O operations."""

import pytest
import os
import tempfile
from pathlib import Path
import platform
import stat
import shutil

from resume_customizer.core.customizer import ResumeCustomizer
from resume_customizer.config import Settings
from tests.integration.fixtures import test_data_manager, temp_test_environment


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping integration tests"
)
class TestFileOperations:
    """Test file handling in various scenarios."""
    
    @pytest.fixture
    def settings(self):
        """Create settings for testing."""
        return Settings(max_iterations=1)  # Single iteration for file tests
    
    @pytest.fixture
    def customizer(self, settings):
        """Create customizer instance."""
        return ResumeCustomizer(settings)
    
    @pytest.mark.asyncio
    async def test_utf8_encoding(self, customizer, temp_test_environment):
        """Test handling of UTF-8 encoded files with special characters."""
        # Create resume with special characters
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_path = Path(tmpdir) / "utf8_resume.md"
            resume_content = """# José García

## Resumen
Ingeniero de software con 5 años de experiencia en desarrollo web.

## Experiencia
### Desarrollador Senior - Compañía México (2020-Presente)
- Desarrollo de APIs RESTful con Python y José
- Implementación de CI/CD con integración continua
- Trabajo con caracteres especiales: ñ, á, é, í, ó, ú, €, £, ¥

## Habilidades
- Lenguajes: Python, JavaScript, C++
- Especialización en internacionalización (i18n)
- Idiomas: Español, Inglés, Français
"""
            resume_path.write_text(resume_content, encoding='utf-8')
            
            job_path = temp_test_environment["jobs"]["standard_swe.md"]
            output_path = Path(tmpdir) / "output_utf8.md"
            
            # Run customization
            await customizer.customize(
                resume_path=str(resume_path),
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            # Verify output maintains UTF-8 encoding
            output_content = output_path.read_text(encoding='utf-8')
            assert "José García" in output_content
            assert "Compañía México" in output_content
            
            # Check special characters preserved
            special_chars = ['ñ', 'á', 'é', 'í', 'ó', 'ú', '€', '£', '¥']
            for char in special_chars:
                if char in resume_content:
                    assert char in output_content, f"Special character {char} should be preserved"
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self, customizer):
        """Test handling of large resume files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a large resume (simulate detailed CV)
            resume_path = Path(tmpdir) / "large_resume.md"
            
            # Build large content
            content_parts = ["# Large Resume Test\n\n"]
            
            # Add many experiences
            for i in range(20):
                content_parts.append(f"""## Experience {i+1} - Company {i+1} (20{i:02d}-20{i+1:02d})
- Detailed description of role and responsibilities
- Managed team of {i+5} developers
- Implemented {i*10 + 50} features
- Reduced costs by ${i*1000 + 5000}

""")
            
            # Add many skills
            content_parts.append("## Skills\n")
            for category in ["Languages", "Frameworks", "Tools", "Databases", "Cloud"]:
                content_parts.append(f"### {category}\n")
                for j in range(10):
                    content_parts.append(f"- {category} skill {j+1}\n")
                content_parts.append("\n")
            
            large_content = "".join(content_parts)
            resume_path.write_text(large_content)
            
            # Create simple job
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Looking for experienced Python developer")
            
            output_path = Path(tmpdir) / "large_output.md"
            
            # Should handle large files
            await customizer.customize(
                resume_path=str(resume_path),
                job_description_path=str(job_path),
                output_path=str(output_path)
            )
            
            assert output_path.exists()
            output_size = output_path.stat().st_size
            assert output_size > 0, "Should produce output for large files"
    
    @pytest.mark.asyncio
    async def test_directory_creation(self, customizer, temp_test_environment):
        """Test automatic directory creation for output paths."""
        resume_path = temp_test_environment["resumes"]["minimal.md"]
        job_path = temp_test_environment["jobs"]["minimal_posting.md"]
        
        # Create nested output path
        nested_path = Path(temp_test_environment["output_dir"]) / "deep" / "nested" / "dir" / "output.md"
        
        # Directory should not exist yet
        assert not nested_path.parent.exists()
        
        # Run customization
        await customizer.customize(
            resume_path=resume_path,
            job_description_path=job_path,
            output_path=str(nested_path)
        )
        
        # Should create all directories
        assert nested_path.exists()
        assert nested_path.is_file()
    
    @pytest.mark.asyncio
    async def test_relative_paths(self, customizer):
        """Test handling of relative file paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Create files with relative paths
                Path("resume.md").write_text("# Test Resume\nDeveloper")
                Path("job.md").write_text("Python developer needed")
                
                # Use relative paths
                await customizer.customize(
                    resume_path="resume.md",
                    job_description_path="job.md",
                    output_path="output.md"
                )
                
                # Check file created with relative path
                assert Path("output.md").exists()
                
            finally:
                os.chdir(original_cwd)
    
    @pytest.mark.asyncio
    async def test_symlink_handling(self, customizer):
        """Test handling of symbolic links."""
        if platform.system() == 'Windows':
            pytest.skip("Symlink test requires Unix-like system")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            
            # Create real files
            real_resume = base_path / "real_resume.md"
            real_resume.write_text("# Real Resume\nContent here")
            
            real_job = base_path / "real_job.md"
            real_job.write_text("Job description")
            
            # Create symlinks
            link_resume = base_path / "link_resume.md"
            link_job = base_path / "link_job.md"
            
            link_resume.symlink_to(real_resume)
            link_job.symlink_to(real_job)
            
            output_path = base_path / "output.md"
            
            # Should work with symlinks
            await customizer.customize(
                resume_path=str(link_resume),
                job_description_path=str(link_job),
                output_path=str(output_path)
            )
            
            assert output_path.exists()
            assert "Real Resume" in output_path.read_text()
    
    @pytest.mark.asyncio
    async def test_file_permissions(self, customizer):
        """Test handling of files with restricted permissions."""
        if platform.system() == 'Windows':
            pytest.skip("Permission test requires Unix-like system")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files
            resume_path = Path(tmpdir) / "resume.md"
            resume_path.write_text("# Test Resume")
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Job description")
            
            # Make resume read-only
            os.chmod(resume_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            
            output_path = Path(tmpdir) / "output.md"
            
            # Should still work with read-only input
            await customizer.customize(
                resume_path=str(resume_path),
                job_description_path=str(job_path),
                output_path=str(output_path)
            )
            
            assert output_path.exists()
            
            # Restore permissions for cleanup
            os.chmod(resume_path, stat.S_IRUSR | stat.S_IWUSR)
    
    @pytest.mark.asyncio
    async def test_concurrent_file_access(self, customizer, temp_test_environment):
        """Test handling when files are accessed concurrently."""
        import asyncio
        
        resume_path = temp_test_environment["resumes"]["minimal.md"]
        job_path = temp_test_environment["jobs"]["minimal_posting.md"]
        
        # Run multiple customizations concurrently
        tasks = []
        for i in range(3):
            output_path = Path(temp_test_environment["output_dir"]) / f"concurrent_{i}.md"
            task = customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            tasks.append(task)
        
        # All should complete successfully
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check all succeeded
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Task {i} failed: {result}"
            output_path = Path(temp_test_environment["output_dir"]) / f"concurrent_{i}.md"
            assert output_path.exists()
    
    @pytest.mark.asyncio
    async def test_output_overwrite(self, customizer, temp_test_environment):
        """Test overwriting existing output files."""
        resume_path = temp_test_environment["resumes"]["minimal.md"]
        job_path = temp_test_environment["jobs"]["minimal_posting.md"]
        output_path = Path(temp_test_environment["output_dir"]) / "overwrite_test.md"
        
        # Create existing file
        output_path.write_text("Old content that should be replaced")
        old_size = output_path.stat().st_size
        
        # Run customization
        await customizer.customize(
            resume_path=resume_path,
            job_description_path=job_path,
            output_path=str(output_path)
        )
        
        # Check file was overwritten
        new_content = output_path.read_text()
        assert "Old content" not in new_content
        assert output_path.stat().st_size != old_size
    
    @pytest.mark.asyncio
    async def test_file_not_found_errors(self, customizer):
        """Test detailed error messages for missing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test missing resume
            with pytest.raises(FileNotFoundError) as exc_info:
                await customizer.customize(
                    resume_path="/nonexistent/path/resume.md",
                    job_description_path=Path(tmpdir) / "job.md",
                    output_path="output.md"
                )
            assert "Resume file not found" in str(exc_info.value)
            
            # Create job file for next test
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Job description")
            
            # Test missing job description
            resume_path = Path(tmpdir) / "resume.md"
            resume_path.write_text("Resume content")
            
            with pytest.raises(FileNotFoundError) as exc_info:
                await customizer.customize(
                    resume_path=str(resume_path),
                    job_description_path="/nonexistent/job.md",
                    output_path="output.md"
                )
            assert "Job description file not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_empty_file_handling(self, customizer):
        """Test handling of empty input files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty files
            resume_path = Path(tmpdir) / "empty_resume.md"
            resume_path.touch()  # Creates empty file
            
            job_path = Path(tmpdir) / "job.md"
            job_path.write_text("Looking for Python developer")
            
            output_path = Path(tmpdir) / "output.md"
            
            # Should handle empty resume gracefully
            await customizer.customize(
                resume_path=str(resume_path),
                job_description_path=str(job_path),
                output_path=str(output_path)
            )
            
            # Should create some output even with empty input
            assert output_path.exists()
            output_content = output_path.read_text()
            assert len(output_content) > 0
    
    @pytest.mark.asyncio
    async def test_file_extension_handling(self, customizer, temp_test_environment):
        """Test handling of different file extensions."""
        resume_path = temp_test_environment["resumes"]["minimal.md"]
        job_path = temp_test_environment["jobs"]["minimal_posting.md"]
        
        # Test various output extensions
        extensions = [".md", ".txt", ".markdown", ""]
        
        for ext in extensions:
            output_path = Path(temp_test_environment["output_dir"]) / f"output_test{ext}"
            
            await customizer.customize(
                resume_path=resume_path,
                job_description_path=job_path,
                output_path=str(output_path)
            )
            
            assert output_path.exists(), f"Should create file with extension '{ext}'"
    
    @pytest.mark.asyncio
    async def test_path_with_spaces(self, customizer):
        """Test handling of file paths with spaces."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory with spaces
            space_dir = Path(tmpdir) / "directory with spaces"
            space_dir.mkdir()
            
            # Create files with spaces in names
            resume_path = space_dir / "my resume file.md"
            resume_path.write_text("# Resume\nContent")
            
            job_path = space_dir / "job description file.md"
            job_path.write_text("Job content")
            
            output_path = space_dir / "customized resume output.md"
            
            # Should handle spaces correctly
            await customizer.customize(
                resume_path=str(resume_path),
                job_description_path=str(job_path),
                output_path=str(output_path)
            )
            
            assert output_path.exists()