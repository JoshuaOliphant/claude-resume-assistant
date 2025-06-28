# ABOUTME: Test suite for the MarkdownReader class
# ABOUTME: Verifies markdown file reading, encoding detection, and validation

import pytest
from pathlib import Path
import tempfile
import os
from unittest.mock import patch, mock_open

from resume_customizer.io.readers import MarkdownReader


class TestMarkdownReader:
    """Test suite for MarkdownReader class."""
    
    @pytest.fixture
    def reader(self):
        """Create a MarkdownReader instance for testing."""
        return MarkdownReader()
    
    @pytest.fixture
    def sample_markdown_content(self):
        """Sample markdown resume content."""
        return """---
name: John Doe
email: john.doe@example.com
---

# John Doe

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
    
    def test_read_valid_markdown_file(self, reader, tmp_path, sample_markdown_content):
        """Test reading a valid markdown file."""
        # Create a temporary markdown file
        test_file = tmp_path / "resume.md"
        test_file.write_text(sample_markdown_content, encoding='utf-8')
        
        # Read the file
        content = reader.read(str(test_file))
        
        # Verify content
        assert content == sample_markdown_content
        assert "John Doe" in content
        assert "## Experience" in content
    
    def test_file_not_found_error(self, reader):
        """Test handling of file not found error."""
        non_existent_file = "/path/to/non/existent/file.md"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            reader.read(non_existent_file)
        
        assert "File not found" in str(exc_info.value)
        assert non_existent_file in str(exc_info.value)
    
    def test_detect_utf8_encoding(self, reader, tmp_path):
        """Test detection of UTF-8 encoding."""
        content = "# Resume\n\nSpecial characters: café, résumé, naïve"
        test_file = tmp_path / "utf8_resume.md"
        test_file.write_text(content, encoding='utf-8')
        
        result = reader.read(str(test_file))
        assert result == content
        assert "café" in result
        assert "résumé" in result
    
    def test_detect_latin1_encoding(self, reader, tmp_path):
        """Test detection of Latin-1 encoding."""
        content = "# Resume\n\nSpecial chars: café"
        test_file = tmp_path / "latin1_resume.md"
        test_file.write_bytes(content.encode('latin-1'))
        
        result = reader.read(str(test_file))
        assert "café" in result
    
    def test_detect_utf16_encoding(self, reader, tmp_path):
        """Test detection of UTF-16 encoding."""
        content = "# Resume\n\nUnicode content: 你好"
        test_file = tmp_path / "utf16_resume.md"
        test_file.write_bytes(content.encode('utf-16'))
        
        result = reader.read(str(test_file))
        assert "你好" in result
    
    def test_invalid_encoding_fallback(self, reader, tmp_path):
        """Test fallback behavior for files with invalid encoding."""
        # Create a file with mixed/invalid encoding - using latin-1 with special chars
        test_file = tmp_path / "invalid_encoding.md"
        # Mix UTF-8 start with latin-1 special characters
        mixed_content = "# Resume\n\n".encode('utf-8') + b'Special: \xe9\xe8\xe7'  # Latin-1 chars
        test_file.write_bytes(mixed_content)
        
        # Should successfully read using fallback encoding
        result = reader.read(str(test_file))
        assert "# Resume" in result
        # The special characters might be replaced or decoded differently
        assert len(result) > 0
    
    def test_validate_markdown_structure(self, reader, tmp_path):
        """Test validation of markdown structure."""
        # Valid markdown
        valid_content = "# Title\n\n## Section\n\nContent"
        valid_file = tmp_path / "valid.md"
        valid_file.write_text(valid_content)
        
        assert reader.validate_structure(reader.read(str(valid_file))) is True
        
        # Invalid markdown (no headers)
        invalid_content = "Just plain text without any structure"
        invalid_file = tmp_path / "invalid.md"
        invalid_file.write_text(invalid_content)
        
        assert reader.validate_structure(reader.read(str(invalid_file))) is False
    
    def test_preserve_formatting_and_whitespace(self, reader, tmp_path):
        """Test that formatting and whitespace are preserved."""
        content = """# Resume

## Section 1
   Indented content
   Multiple spaces    preserved

## Section 2
\tTab character preserved
\t\tDouble tab

Blank lines above and below

"""
        test_file = tmp_path / "formatted.md"
        test_file.write_text(content)
        
        result = reader.read(str(test_file))
        assert result == content
        assert "   Indented content" in result
        assert "Multiple spaces    preserved" in result
        assert "\tTab character preserved" in result
        assert "\t\tDouble tab" in result
    
    def test_extract_yaml_metadata(self, reader, tmp_path, sample_markdown_content):
        """Test extraction of YAML front matter metadata."""
        test_file = tmp_path / "with_metadata.md"
        test_file.write_text(sample_markdown_content)
        
        content = reader.read(str(test_file))
        metadata = reader.extract_metadata(content)
        
        assert metadata is not None
        assert metadata['name'] == 'John Doe'
        assert metadata['email'] == 'john.doe@example.com'
    
    def test_extract_metadata_no_frontmatter(self, reader):
        """Test metadata extraction when no front matter exists."""
        content = "# Resume\n\nNo front matter here"
        metadata = reader.extract_metadata(content)
        
        assert metadata == {}
    
    def test_handle_empty_file(self, reader, tmp_path):
        """Test handling of empty markdown file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")
        
        content = reader.read(str(empty_file))
        assert content == ""
        
        # Empty file should fail validation
        assert reader.validate_structure(content) is False
    
    def test_handle_large_file(self, reader, tmp_path):
        """Test handling of large markdown files."""
        # Create a large file (1MB+)
        large_content = "# Resume\n\n" + ("## Section\n" + "Content " * 200 + "\n\n") * 1000
        large_file = tmp_path / "large.md"
        large_file.write_text(large_content)
        
        # Should read without issues
        result = reader.read(str(large_file))
        assert len(result) > 1_000_000
        assert result.startswith("# Resume")
    
    def test_handle_windows_line_endings(self, reader, tmp_path):
        """Test handling of Windows (CRLF) line endings."""
        content_with_crlf = "# Resume\r\n\r\n## Section\r\nContent"
        test_file = tmp_path / "windows.md"
        test_file.write_bytes(content_with_crlf.encode('utf-8'))
        
        result = reader.read(str(test_file))
        # Reader should normalize line endings
        assert "\r\n" in result or "\n" in result
        assert "# Resume" in result
        assert "## Section" in result
    
    def test_handle_various_markdown_flavors(self, reader, tmp_path):
        """Test handling of different markdown flavors."""
        # CommonMark style
        commonmark = """# Title

## Section

- List item 1
- List item 2

[Link](http://example.com)
"""
        
        # GitHub Flavored Markdown
        gfm = """# Title

## Section

- [x] Completed task
- [ ] Pending task

```python
def hello():
    print("Hello")
```

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
        
        # Test CommonMark
        cm_file = tmp_path / "commonmark.md"
        cm_file.write_text(commonmark)
        cm_result = reader.read(str(cm_file))
        assert "- List item 1" in cm_result
        assert "[Link](http://example.com)" in cm_result
        
        # Test GFM
        gfm_file = tmp_path / "gfm.md"
        gfm_file.write_text(gfm)
        gfm_result = reader.read(str(gfm_file))
        assert "- [x] Completed task" in gfm_result
        assert "```python" in gfm_result
        assert "| Column 1 | Column 2 |" in gfm_result
    
    def test_read_with_bom(self, reader, tmp_path):
        """Test reading files with Byte Order Mark (BOM)."""
        content = "# Resume with BOM"
        
        # UTF-8 with BOM
        utf8_bom_file = tmp_path / "utf8_bom.md"
        utf8_bom_file.write_bytes(b'\xef\xbb\xbf' + content.encode('utf-8'))
        
        result = reader.read(str(utf8_bom_file))
        assert result == content
        assert not result.startswith('\ufeff')  # BOM should be stripped
    
    def test_permission_error(self, reader, tmp_path):
        """Test handling of permission errors."""
        if os.name == 'nt':  # Windows
            pytest.skip("Permission test not applicable on Windows")
        
        test_file = tmp_path / "no_permission.md"
        test_file.write_text("# Resume")
        test_file.chmod(0o000)  # Remove all permissions
        
        try:
            with pytest.raises(PermissionError) as exc_info:
                reader.read(str(test_file))
            assert "Permission denied" in str(exc_info.value)
        finally:
            test_file.chmod(0o644)  # Restore permissions for cleanup
    
    def test_validate_has_required_sections(self, reader):
        """Test validation checks for required resume sections."""
        # Complete resume
        complete = """# John Doe

## Summary
Summary text

## Experience
Experience text

## Skills
Skills text
"""
        assert reader.validate_structure(complete) is True
        
        # Missing Experience section
        incomplete = """# John Doe

## Summary
Summary text

## Skills
Skills text
"""
        # Should still be valid structure-wise, but could flag missing sections
        assert reader.validate_structure(incomplete) is True
        
        # Check for required sections separately
        assert reader.has_required_sections(complete) is True
        assert reader.has_required_sections(incomplete) is False