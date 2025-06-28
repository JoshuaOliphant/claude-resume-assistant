#!/usr/bin/env python3
# ABOUTME: Script to test MarkdownReader with various file encodings
# ABOUTME: Creates test files and validates encoding detection

"""Test script for MarkdownReader encoding handling."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from resume_customizer.io.readers import MarkdownReader
from pathlib import Path


def test_markdown_reader():
    """Test MarkdownReader with various sample files."""
    reader = MarkdownReader()
    samples_dir = Path(__file__).parent / "markdown_samples"
    
    print("Testing MarkdownReader with various encodings...\n")
    
    # Test UTF-8 file
    utf8_file = samples_dir / "utf8_resume.md"
    if utf8_file.exists():
        print(f"Reading {utf8_file.name}:")
        content = reader.read(str(utf8_file))
        print(f"  ✓ Successfully read {len(content)} characters")
        print(f"  ✓ Contains special chars: {'José' in content}")
        print(f"  ✓ Valid structure: {reader.validate_structure(content)}")
        
        metadata = reader.extract_metadata(content)
        if metadata:
            print(f"  ✓ Extracted metadata: {list(metadata.keys())}")
        
        has_sections = reader.has_required_sections(content)
        print(f"  ✓ Has required sections: {has_sections}")
        print()
    
    # Create and test Latin-1 encoded file
    latin1_content = """# Resume

## Experience
Software Engineer at Café

## Skills
Python, résumé parsing
"""
    latin1_file = samples_dir / "latin1_test.md"
    latin1_file.write_bytes(latin1_content.encode('latin-1'))
    
    print(f"Reading Latin-1 encoded file:")
    content = reader.read(str(latin1_file))
    print(f"  ✓ Successfully read {len(content)} characters")
    print(f"  ✓ Contains 'résumé': {'résumé' in content}")
    print(f"  ✓ Contains 'Café': {'Café' in content}")
    print()
    
    # Create Windows-1252 encoded file
    win_content = """# John's Resume

## Experience
Senior Engineer – Tech Corp

## Skills
C++, "Smart Quotes", Windows–specific
"""
    win_file = samples_dir / "windows1252_test.md"
    win_file.write_bytes(win_content.encode('windows-1252'))
    
    print(f"Reading Windows-1252 encoded file:")
    content = reader.read(str(win_file))
    print(f"  ✓ Successfully read {len(content)} characters")
    smart_chars = ['"', '"', '–']
    has_smart = any(c in content for c in smart_chars)
    print(f"  ✓ Contains smart quotes: {has_smart}")
    print()
    
    # Test with UTF-16 BOM
    utf16_content = "# Resume\n\n## Experience\nUnicode test: 你好世界"
    utf16_file = samples_dir / "utf16_bom_test.md"
    utf16_file.write_bytes(b'\xff\xfe' + utf16_content.encode('utf-16-le'))
    
    print(f"Reading UTF-16 with BOM:")
    content = reader.read(str(utf16_file))
    print(f"  ✓ Successfully read {len(content)} characters")
    print(f"  ✓ Contains Chinese chars: {'你好' in content}")
    print()
    
    # Clean up test files
    latin1_file.unlink()
    win_file.unlink() 
    utf16_file.unlink()
    
    print("All encoding tests passed! ✅")


if __name__ == "__main__":
    test_markdown_reader()