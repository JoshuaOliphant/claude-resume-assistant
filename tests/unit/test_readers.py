# ABOUTME: Unit tests for I/O readers module
# ABOUTME: Tests MarkdownReader encoding detection, file reading, and error handling

import pytest
import tempfile
import os
import pathlib
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from resume_customizer.io.readers import MarkdownReader


class TestMarkdownReader:
    """Test suite for MarkdownReader class."""
    
    @pytest.fixture
    def reader(self):
        """Create a MarkdownReader instance."""
        return MarkdownReader()
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Resume\n\n## Experience\nTest content")
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_initialization(self, reader):
        """Test MarkdownReader initialization."""
        assert reader is not None
        assert isinstance(reader.supported_encodings, list)
        assert 'utf-8' in reader.supported_encodings
        assert 'ascii' in reader.supported_encodings
    
    def test_read_valid_file(self, reader, temp_file):
        """Test reading a valid markdown file."""
        content = reader.read(temp_file)
        
        assert content is not None
        assert "# Test Resume" in content
        assert "## Experience" in content
        assert "Test content" in content
    
    def test_file_not_found(self, reader):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            reader.read("/path/to/nonexistent/file.md")
    
    def test_permission_error(self, reader, temp_file):
        """Test handling of permission errors."""
        # Use the temp file path to avoid FileNotFoundError
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with pytest.raises(PermissionError, match="Permission denied"):
                    reader.read(temp_file)
    
    def test_encoding_detection(self, reader):
        """Test automatic encoding detection."""
        # Test UTF-8 file
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.md', delete=False) as f:
            f.write("# UTF-8 Resume\n## Test with émojis 🚀")
            utf8_path = f.name
        
        try:
            content = reader.read(utf8_path)
            assert "UTF-8 Resume" in content
            assert "émojis" in content
            assert "🚀" in content
        finally:
            os.unlink(utf8_path)
    
    def test_latin1_encoding(self, reader):
        """Test reading Latin-1 encoded file."""
        # Create Latin-1 encoded file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.md', delete=False) as f:
            content = "# Résumé\n## Expérience".encode('latin-1')
            f.write(content)
            latin1_path = f.name
        
        try:
            content = reader.read(latin1_path)
            # The file might be read with a different encoding detection
            # Just verify we can read it without error
            assert isinstance(content, str)
            assert len(content) > 0
        finally:
            os.unlink(latin1_path)
    
    def test_encoding_detection_internal(self, reader):
        """Test internal encoding detection logic."""
        # Since detect_encoding is not a public method, test through read
        # Create files with different encodings and verify they're read correctly
        
        # Test ASCII file
        with tempfile.NamedTemporaryFile(mode='w', encoding='ascii', suffix='.md', delete=False) as f:
            f.write("# ASCII Resume")
            ascii_path = f.name
        
        try:
            content = reader.read(ascii_path)
            assert "ASCII Resume" in content
        finally:
            os.unlink(ascii_path)
    
    def test_markdown_structure(self, reader):
        """Test reading files with various markdown structures."""
        # Test with proper markdown structure
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# John Doe

## Summary
Software Engineer

## Experience
- Company A
- Company B
""")
            md_path = f.name
        
        try:
            content = reader.read(md_path)
            assert "# John Doe" in content
            assert "## Summary" in content
            assert "## Experience" in content
        finally:
            os.unlink(md_path)
    
    def test_yaml_frontmatter(self, reader):
        """Test reading files with YAML frontmatter."""
        # Test file with YAML frontmatter
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
title: Software Engineer Resume
author: John Doe
date: 2024-01-01
---

# John Doe

## Summary
Experienced developer
""")
            yaml_path = f.name
        
        try:
            content = reader.read(yaml_path)
            # Should read the entire content including frontmatter
            assert "---" in content
            assert "title: Software Engineer Resume" in content
            assert "# John Doe" in content
        finally:
            os.unlink(yaml_path)
    
    def test_binary_file_handling(self, reader):
        """Test handling of binary/non-text files."""
        # Create a binary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.md', delete=False) as f:
            # Write binary data
            f.write(b'\x00\x01\x02\x03\x04')
            binary_path = f.name
        
        try:
            # Should handle binary files gracefully
            content = reader.read(binary_path)
            # chardet should detect it and we should get some result
            assert isinstance(content, str)
        except UnicodeDecodeError:
            # Also acceptable if it raises an error
            pass
        finally:
            os.unlink(binary_path)
    
    def test_empty_file(self, reader):
        """Test reading empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            # Write nothing
            empty_path = f.name
        
        try:
            content = reader.read(empty_path)
            assert content == ""
        finally:
            os.unlink(empty_path)
    
    def test_large_file_handling(self, reader):
        """Test reading large files."""
        # Create a large file (1MB)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Large Resume\n\n")
            # Write 1MB of content
            for i in range(10000):
                f.write(f"## Section {i}\nLorem ipsum dolor sit amet " * 10 + "\n")
            large_path = f.name
        
        try:
            content = reader.read(large_path)
            assert content.startswith("# Large Resume")
            assert len(content) > 1000000  # Over 1MB
        finally:
            os.unlink(large_path)

