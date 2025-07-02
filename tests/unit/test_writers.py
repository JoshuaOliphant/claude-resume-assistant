# ABOUTME: Unit tests for I/O writers module  
# ABOUTME: Tests OutputWriter file operations, backups, and error handling

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

from resume_customizer.io.writers import OutputWriter
from resume_customizer.models.result import CustomizationResult, Change, ChangeType


class TestOutputWriter:
    """Test suite for OutputWriter class."""
    
    @pytest.fixture
    def writer(self):
        """Create an OutputWriter instance."""
        return OutputWriter()
    
    @pytest.fixture 
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # Cleanup
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def sample_result(self):
        """Create a sample CustomizationResult for testing."""
        return CustomizationResult(
            original_content="# Original Resume",
            customized_content="# Customized Resume\n\n## Experience\nUpdated content",
            match_score=0.85,
            changes=[
                Change(
                    type=ChangeType.CONTENT_REWRITE,
                    section="Experience",
                    description="Updated experience section"
                )
            ],
            integrated_keywords=["Python", "AWS", "Docker"],
            reordered_sections=[]
        )
    
    def test_initialization(self, writer):
        """Test OutputWriter initialization."""
        assert writer is not None
        assert writer.default_encoding == 'utf-8'
        assert writer.backup_extension == '.backup'
    
    def test_write_basic(self, writer, temp_dir):
        """Test basic file writing."""
        filepath = os.path.join(temp_dir, "test_output.md")
        content = "# Test Resume\n\n## Experience\nTest content"
        
        success = writer.write(content, filepath)
        
        assert success is True
        assert os.path.exists(filepath)
        
        # Verify content was written correctly
        with open(filepath, 'r') as f:
            written_content = f.read()
        assert written_content == content
    
    def test_write_with_encoding(self, writer, temp_dir):
        """Test writing with specific encoding."""
        filepath = os.path.join(temp_dir, "test_latin1.md")
        content = "# Résumé\n\n## Expérience"
        
        success = writer.write(content, filepath, encoding='latin-1')
        
        assert success is True
        
        # Verify content with correct encoding
        with open(filepath, 'r', encoding='latin-1') as f:
            written_content = f.read()
        assert written_content == content
    
    def test_atomic_write(self, writer, temp_dir):
        """Test atomic write operation."""
        filepath = os.path.join(temp_dir, "atomic_test.md")
        content = "# Atomic Write Test"
        
        # Write initial content
        with open(filepath, 'w') as f:
            f.write("Initial content")
        
        # Atomic write should replace content safely
        success = writer.write(content, filepath, atomic=True)
        
        assert success is True
        with open(filepath, 'r') as f:
            assert f.read() == content
    
    def test_create_backup(self, writer, temp_dir):
        """Test backup creation."""
        filepath = os.path.join(temp_dir, "backup_test.md")
        original_content = "# Original Content"
        new_content = "# New Content"
        
        # Write original file
        with open(filepath, 'w') as f:
            f.write(original_content)
        
        # Create backup
        writer._create_backup(Path(filepath), 5)
        
        # Find the backup file
        backup_files = list(Path(temp_dir).glob("backup_test.md.backup*"))
        assert len(backup_files) > 0
        backup_path = str(backup_files[0])
        
        assert backup_path is not None
        assert os.path.exists(backup_path)
        assert '.backup' in backup_path
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            assert f.read() == original_content
    
    def test_max_backups_limit(self, writer, temp_dir):
        """Test that backup limit is respected."""
        filepath = os.path.join(temp_dir, "backup_limit.md")
        
        # Create initial file
        with open(filepath, 'w') as f:
            f.write("Version 0")
        
        # Create multiple backups
        for i in range(10):
            with open(filepath, 'w') as f:
                f.write(f"Version {i+1}")
            writer._create_backup(Path(filepath), 5)
        
        # Check number of backups
        backup_files = list(Path(temp_dir).glob("backup_limit.md.backup*"))
        assert len(backup_files) <= 5  # max_backups default
    
    def test_validate_content(self, writer):
        """Test content validation."""
        # Valid content
        assert writer._validate_content("# Valid Resume") is True
        assert writer._validate_content("Any non-empty string") is True
        
        # Invalid content 
        assert writer._validate_content(None) is False
        assert writer._validate_content("") is False  # Empty string is invalid
    
    def test_write_result_object(self, writer, temp_dir, sample_result):
        """Test writing a CustomizationResult object."""
        filepath = os.path.join(temp_dir, "result_output.md")
        
        # Write the customized content from the result
        success = writer.write(sample_result.customized_content, filepath)
        
        assert success is True
        assert os.path.exists(filepath)
        
        # Verify customized content was written
        with open(filepath, 'r') as f:
            content = f.read()
        assert content == sample_result.customized_content
    
    def test_write_with_metadata(self, writer, temp_dir, sample_result):
        """Test writing with metadata from CustomizationResult."""
        filepath = os.path.join(temp_dir, "metadata_test.md")
        content = "# Resume Content"
        
        success = writer.write_with_metadata(content, filepath, sample_result)
        
        assert success is True
        
        # Read and verify metadata was included
        with open(filepath, 'r') as f:
            written = f.read()
        
        # Check for metadata comments
        assert "<!-- Resume customized by Claude Resume Assistant -->" in written
        assert "<!-- Match Score:" in written
        assert "<!-- Keywords:" in written
        assert "Python, AWS, Docker" in written
        assert "<!-- Changes Applied: 1 -->" in written
    
    def test_directory_creation(self, writer, temp_dir):
        """Test that directories are created if they don't exist."""
        nested_path = os.path.join(temp_dir, "nested", "dirs", "output.md")
        content = "# Test"
        
        success = writer.write(content, nested_path)
        
        assert success is True
        assert os.path.exists(nested_path)
    
    def test_write_permission_error(self, writer):
        """Test handling of permission errors."""
        # Mock open to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("No permission")):
            success = writer.write("content", "/readonly/path.md")
            assert success is False
    
    def test_write_disk_full_error(self, writer):
        """Test handling of disk full errors."""
        # Mock open to raise OSError (disk full)
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            success = writer.write("content", "/tmp/test.md")
            assert success is False
    
    def test_write_with_confirmation(self, writer, temp_dir):
        """Test write_with_confirmation method."""
        filepath = os.path.join(temp_dir, "confirm_write.md")
        content = "# Resume Content"
        
        # This method doesn't actually ask for confirmation, it just writes and returns details
        result = writer.write_with_confirmation(content, filepath)
        
        assert result['success'] is True
        assert result['path'] == str(Path(filepath).resolve())
        assert 'timestamp' in result
        assert 'size' in result
        assert result['size'] == len(content)
        assert result['lines'] == 1
        assert os.path.exists(filepath)
    
    def test_write_empty_content(self, writer, temp_dir):
        """Test writing empty content."""
        filepath = os.path.join(temp_dir, "empty.md")
        
        # Empty string is invalid according to _validate_content
        success = writer.write("", filepath)
        
        assert success is False  # Should fail validation
        assert not os.path.exists(filepath)  # File should not be created
    
    def test_overwrite_existing_file(self, writer, temp_dir):
        """Test overwriting an existing file."""
        filepath = os.path.join(temp_dir, "existing.md")
        
        # Write initial content
        with open(filepath, 'w') as f:
            f.write("Old content")
        
        # Overwrite with new content
        new_content = "New content"
        success = writer.write(new_content, filepath)
        
        assert success is True
        with open(filepath, 'r') as f:
            assert f.read() == new_content
    
    def test_special_characters_in_path(self, writer, temp_dir):
        """Test handling special characters in file paths."""
        # Test with spaces
        filepath = os.path.join(temp_dir, "file with spaces.md")
        success = writer.write("Content", filepath)
        assert success is True
        assert os.path.exists(filepath)
        
        # Test with unicode characters
        unicode_path = os.path.join(temp_dir, "résumé_file.md")
        success = writer.write("Content", unicode_path)
        assert success is True
        assert os.path.exists(unicode_path)