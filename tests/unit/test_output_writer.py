# ABOUTME: Test suite for the OutputWriter class
# ABOUTME: Verifies safe file writing, backups, and metadata handling

import pytest
from pathlib import Path
import tempfile
import os
import time
from datetime import datetime
from unittest.mock import patch, Mock

from resume_customizer.io.writers import OutputWriter
from resume_customizer.models.result import CustomizationResult, Change, ChangeType


class TestOutputWriter:
    """Test suite for OutputWriter class."""
    
    @pytest.fixture
    def writer(self):
        """Create an OutputWriter instance for testing."""
        return OutputWriter()
    
    @pytest.fixture
    def sample_content(self):
        """Sample markdown content for testing."""
        return """# John Doe

## Summary
Experienced software engineer with 10+ years of experience.

## Experience

### Senior Software Engineer - Tech Corp
*January 2020 - Present*

- Led team of 5 engineers
- Implemented microservices architecture
- Improved system performance by 40%

## Skills
- Python, Java, JavaScript
- AWS, Docker, Kubernetes
- Agile, Scrum
"""
    
    @pytest.fixture
    def sample_result(self, sample_content):
        """Create a sample customization result."""
        return CustomizationResult(
            original_content="# Original Resume",
            customized_content=sample_content,
            match_score=85.5,
            changes=[
                Change(
                    type=ChangeType.CONTENT_REWRITE,
                    section="Experience",
                    description="Enhanced descriptions"
                )
            ],
            integrated_keywords=["Python", "AWS"],
            reordered_sections=[],
            timestamp=datetime(2024, 1, 1, 12, 0, 0)
        )
    
    def test_write_markdown_file(self, writer, tmp_path, sample_content):
        """Test basic markdown file writing."""
        output_file = tmp_path / "output.md"
        
        success = writer.write(sample_content, str(output_file))
        
        assert success is True
        assert output_file.exists()
        assert output_file.read_text() == sample_content
    
    def test_preserve_formatting(self, writer, tmp_path):
        """Test that formatting and whitespace are preserved exactly."""
        content_with_formatting = """# Resume

## Section 1
   Indented content
   Multiple    spaces    preserved

\tTab characters preserved
\t\tDouble tabs

Trailing spaces at end of line   
Empty lines below:


End of content"""
        
        output_file = tmp_path / "formatted.md"
        writer.write(content_with_formatting, str(output_file))
        
        # Read back and verify exact match
        written_content = output_file.read_text()
        assert written_content == content_with_formatting
    
    def test_create_backup_if_exists(self, writer, tmp_path, sample_content):
        """Test backup creation when overwriting existing file."""
        output_file = tmp_path / "resume.md"
        original_content = "# Original Resume\n\nOld content"
        
        # Create existing file
        output_file.write_text(original_content)
        original_mtime = output_file.stat().st_mtime
        
        # Wait a bit to ensure different timestamp
        time.sleep(0.1)
        
        # Write new content
        writer.write(sample_content, str(output_file))
        
        # Check backup was created
        backup_files = list(tmp_path.glob("resume.md.backup.*"))
        assert len(backup_files) == 1
        
        backup_file = backup_files[0]
        assert backup_file.read_text() == original_content
        assert ".backup." in backup_file.name
        
        # Verify new content was written
        assert output_file.read_text() == sample_content
    
    def test_no_backup_for_new_file(self, writer, tmp_path, sample_content):
        """Test that no backup is created for new files."""
        output_file = tmp_path / "new_resume.md"
        
        writer.write(sample_content, str(output_file))
        
        # Check no backup was created
        backup_files = list(tmp_path.glob("new_resume.md.backup.*"))
        assert len(backup_files) == 0
        assert output_file.exists()
    
    def test_handle_permission_error(self, writer, tmp_path, sample_content):
        """Test handling of permission errors."""
        if os.name == 'nt':  # Windows
            pytest.skip("Permission test not applicable on Windows")
        
        output_file = tmp_path / "readonly.md"
        output_file.touch()
        output_file.chmod(0o444)  # Read-only
        
        try:
            success = writer.write(sample_content, str(output_file))
            assert success is False
        finally:
            output_file.chmod(0o644)  # Restore permissions
    
    def test_create_parent_directories(self, writer, tmp_path, sample_content):
        """Test automatic creation of parent directories."""
        output_file = tmp_path / "nested" / "dirs" / "resume.md"
        
        success = writer.write(sample_content, str(output_file))
        
        assert success is True
        assert output_file.exists()
        assert output_file.parent.exists()
        assert output_file.read_text() == sample_content
    
    def test_add_metadata_comments(self, writer, tmp_path, sample_result):
        """Test adding metadata comments to output."""
        output_file = tmp_path / "with_metadata.md"
        
        writer.write_with_metadata(
            sample_result.customized_content,
            str(output_file),
            sample_result
        )
        
        content = output_file.read_text()
        
        # Check metadata comments are present
        assert "<!-- Resume customized by Claude Resume Assistant -->" in content
        assert "<!-- Match Score: 85.5% -->" in content
        assert "<!-- Keywords: Python, AWS -->" in content
        assert "<!-- Generated: 2024-01-01" in content
        assert sample_result.customized_content in content
    
    def test_validate_content_before_writing(self, writer, tmp_path):
        """Test content validation before writing."""
        # Empty content should fail validation
        output_file = tmp_path / "empty.md"
        success = writer.write("", str(output_file))
        assert success is False
        assert not output_file.exists()
        
        # None content should fail
        success = writer.write(None, str(output_file))
        assert success is False
        
        # Valid content should pass
        success = writer.write("# Resume", str(output_file))
        assert success is True
        assert output_file.exists()
    
    def test_atomic_write(self, writer, tmp_path, sample_content):
        """Test atomic write operation (write to temp, then rename)."""
        output_file = tmp_path / "atomic.md"
        
        # Mock to verify temp file is used
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_file = Mock()
            mock_temp.return_value.__enter__.return_value = mock_file
            mock_file.name = str(tmp_path / "temp_file")
            
            writer.write(sample_content, str(output_file), atomic=True)
            
            # Verify temp file was used
            mock_temp.assert_called_once()
            mock_file.write.assert_called()
    
    def test_success_confirmation(self, writer, tmp_path, sample_content):
        """Test success confirmation with details."""
        output_file = tmp_path / "confirmed.md"
        
        result = writer.write_with_confirmation(sample_content, str(output_file))
        
        assert result['success'] is True
        assert result['path'] == str(output_file)
        assert result['size'] == len(sample_content)
        assert 'timestamp' in result
        assert output_file.exists()
    
    def test_handle_disk_full_error(self, writer, tmp_path, sample_content):
        """Test handling of disk full errors."""
        output_file = tmp_path / "disk_full.md"
        
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            success = writer.write(sample_content, str(output_file))
            assert success is False
    
    def test_different_output_paths(self, writer, tmp_path, sample_content):
        """Test writing to different output path formats."""
        # Absolute path
        abs_path = tmp_path / "absolute.md"
        assert writer.write(sample_content, str(abs_path)) is True
        assert abs_path.exists()
        
        # Relative path (from tmp_path)
        os.chdir(tmp_path)
        rel_path = "relative.md"
        assert writer.write(sample_content, rel_path) is True
        assert Path(rel_path).exists()
        
        # Path with ~ expansion
        home_path = "~/test_resume.md"
        expanded_path = Path(home_path).expanduser()
        if expanded_path.parent.exists():  # Only test if home is accessible
            assert writer.write(sample_content, home_path) is True
            assert expanded_path.exists()
            expanded_path.unlink()  # Clean up
    
    def test_preserve_line_endings(self, writer, tmp_path):
        """Test preservation of different line ending styles."""
        # Unix line endings
        unix_content = "Line 1\nLine 2\nLine 3"
        unix_file = tmp_path / "unix.md"
        writer.write(unix_content, str(unix_file))
        assert unix_file.read_bytes() == unix_content.encode()
        
        # Windows line endings
        windows_content = "Line 1\r\nLine 2\r\nLine 3"
        windows_file = tmp_path / "windows.md"
        writer.write(windows_content, str(windows_file))
        assert windows_file.read_bytes() == windows_content.encode()
        
        # Mixed line endings (preserve as-is)
        mixed_content = "Line 1\nLine 2\r\nLine 3"
        mixed_file = tmp_path / "mixed.md"
        writer.write(mixed_content, str(mixed_file))
        assert mixed_file.read_bytes() == mixed_content.encode()
    
    def test_safe_filename_generation(self, writer, tmp_path):
        """Test generation of safe filenames from titles."""
        test_cases = [
            ("My Resume: 2024", "My_Resume_2024"),
            ("Software Engineer / DevOps", "Software_Engineer_DevOps"),
            ("John's Resume (Final)", "Johns_Resume_Final"),
            ("Resume<>:|?*", "Resume"),
        ]
        
        for title, expected in test_cases:
            safe_name = writer.generate_safe_filename(title)
            assert safe_name == expected
            
            # Test that file can be created
            output_file = tmp_path / f"{safe_name}.md"
            assert writer.write("# Test", str(output_file)) is True
    
    def test_backup_rotation(self, writer, tmp_path, sample_content):
        """Test that old backups are rotated/limited."""
        output_file = tmp_path / "resume.md"
        
        # Create multiple versions
        for i in range(5):
            output_file.write_text(f"Version {i}")
            time.sleep(0.1)  # Ensure different timestamps
            writer.write(sample_content, str(output_file), max_backups=3)
        
        # Check that only 3 backups are kept
        backup_files = sorted(tmp_path.glob("resume.md.backup.*"))
        assert len(backup_files) <= 3
        
        # Verify newest backups are kept
        if len(backup_files) == 3:
            # Read the newest backup
            newest_backup = backup_files[-1]
            content = newest_backup.read_text()
            assert "Version" in content
    
    def test_write_with_custom_encoding(self, writer, tmp_path):
        """Test writing with different encodings."""
        content_with_unicode = "# Résumé\n\nCafé experience: 10+ años"
        
        # UTF-8 (default)
        utf8_file = tmp_path / "utf8.md"
        writer.write(content_with_unicode, str(utf8_file))
        assert utf8_file.read_text(encoding='utf-8') == content_with_unicode
        
        # Latin-1
        latin1_file = tmp_path / "latin1.md"
        writer.write(content_with_unicode, str(latin1_file), encoding='latin-1')
        assert latin1_file.read_text(encoding='latin-1') == content_with_unicode
        
        # UTF-16
        utf16_file = tmp_path / "utf16.md"  
        writer.write(content_with_unicode, str(utf16_file), encoding='utf-16')
        assert utf16_file.read_text(encoding='utf-16') == content_with_unicode
    
    def test_concurrent_write_safety(self, writer, tmp_path, sample_content):
        """Test handling of concurrent write attempts."""
        output_file = tmp_path / "concurrent.md"
        
        # Simulate locked file
        with patch('builtins.open', side_effect=OSError("Resource temporarily unavailable")):
            success = writer.write(sample_content, str(output_file))
            assert success is False
        
        # Verify file wasn't partially written
        assert not output_file.exists()
    
    def test_symlink_handling(self, writer, tmp_path, sample_content):
        """Test writing through symlinks."""
        if os.name == 'nt':  # Windows
            pytest.skip("Symlink test not applicable on Windows")
        
        # Create target and symlink
        target_file = tmp_path / "target.md"
        symlink_file = tmp_path / "symlink.md"
        symlink_file.symlink_to(target_file)
        
        # Write through symlink
        success = writer.write(sample_content, str(symlink_file))
        assert success is True
        
        # Verify content written to target
        assert target_file.exists()
        assert target_file.read_text() == sample_content
        assert symlink_file.is_symlink()