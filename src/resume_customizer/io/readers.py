# ABOUTME: MarkdownReader implementation for parsing resume files
# ABOUTME: Handles encoding detection, validation, and metadata extraction

"""Readers for various resume file formats."""

import chardet
import yaml
import re
from pathlib import Path
from typing import Dict, Optional, Any


class MarkdownReader:
    """Reader for Markdown-formatted resume files."""
    
    def __init__(self):
        """Initialize the MarkdownReader."""
        self.supported_encodings = [
            'utf-8', 'utf-16', 'utf-16-le', 'utf-16-be',
            'latin-1', 'iso-8859-1', 'windows-1252',
            'ascii'
        ]
    
    def read(self, filepath: str) -> str:
        """
        Read a markdown file with automatic encoding detection.
        
        Args:
            filepath: Path to the markdown file
            
        Returns:
            The file contents as a string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file can't be read due to permissions
            UnicodeDecodeError: If the file encoding can't be determined
        """
        path = Path(filepath)
        
        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Read file as bytes first for encoding detection
        try:
            with open(path, 'rb') as f:
                raw_content = f.read()
        except PermissionError:
            raise PermissionError(f"Permission denied: {filepath}")
        
        # Handle empty files
        if not raw_content:
            return ""
        
        # Detect encoding
        encoding = self._detect_encoding(raw_content)
        
        # Remove BOM if present
        if raw_content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
            raw_content = raw_content[3:]
        elif raw_content.startswith(b'\xff\xfe'):  # UTF-16 LE BOM
            raw_content = raw_content[2:]
        elif raw_content.startswith(b'\xfe\xff'):  # UTF-16 BE BOM
            raw_content = raw_content[2:]
        
        # Try to decode with detected encoding
        try:
            content = raw_content.decode(encoding)
            return content
        except UnicodeDecodeError as e:
            # Try fallback encodings
            for enc in self.supported_encodings:
                if enc != encoding:
                    try:
                        return raw_content.decode(enc)
                    except UnicodeDecodeError:
                        continue
            
            # Last resort: try with error handling
            try:
                return raw_content.decode('utf-8', errors='replace')
            except:
                # If all else fails, raise the original error
                raise UnicodeDecodeError(
                    encoding,
                    raw_content,
                    e.start,
                    e.end,
                    f"Unable to decode file with any supported encoding: {filepath}"
                )
    
    def _detect_encoding(self, raw_content: bytes) -> str:
        """
        Detect the encoding of the file content.
        
        Args:
            raw_content: Raw bytes from the file
            
        Returns:
            Detected encoding name
        """
        # Use chardet for encoding detection
        detection = chardet.detect(raw_content)
        
        if detection['confidence'] > 0.7:
            encoding = detection['encoding']
            # Normalize encoding name
            if encoding:
                encoding = encoding.lower()
                if encoding in ['ascii', 'iso-8859-1']:
                    return 'utf-8'  # Prefer UTF-8 for ASCII-compatible files
                return encoding
        
        # Default to UTF-8
        return 'utf-8'
    
    def validate_structure(self, content: str) -> bool:
        """
        Validate that the content has valid markdown structure.
        
        Args:
            content: Markdown content to validate
            
        Returns:
            True if valid markdown structure, False otherwise
        """
        if not content.strip():
            return False
        
        # Check for at least one header
        header_pattern = r'^#+\s+.+$'
        if not re.search(header_pattern, content, re.MULTILINE):
            return False
        
        return True
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract YAML front matter metadata from markdown content.
        
        Args:
            content: Markdown content with potential YAML front matter
            
        Returns:
            Dictionary of metadata, empty dict if no metadata found
        """
        # Check for YAML front matter
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*$'
        match = re.match(yaml_pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            yaml_content = match.group(1)
            try:
                metadata = yaml.safe_load(yaml_content)
                return metadata if metadata else {}
            except yaml.YAMLError:
                return {}
        
        return {}
    
    def has_required_sections(self, content: str) -> bool:
        """
        Check if the resume has commonly required sections.
        
        Args:
            content: Markdown content to check
            
        Returns:
            True if all required sections are present
        """
        required_sections = ['experience', 'skills']
        content_lower = content.lower()
        
        for section in required_sections:
            # Look for section headers
            section_pattern = rf'^#+\s*{section}'
            if not re.search(section_pattern, content_lower, re.MULTILINE | re.IGNORECASE):
                return False
        
        return True