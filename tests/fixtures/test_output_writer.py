#!/usr/bin/env python3
# ABOUTME: Script to test OutputWriter functionality
# ABOUTME: Demonstrates safe file writing, backups, and metadata

"""Test script for OutputWriter functionality."""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from resume_customizer.io.writers import OutputWriter
from resume_customizer.models.result import (
    CustomizationResult, Change, ChangeType, SectionChange
)


def test_output_writer():
    """Test OutputWriter with various scenarios."""
    writer = OutputWriter()
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    print("Testing OutputWriter functionality...\n")
    
    # Test 1: Basic write
    print("1. Basic file writing:")
    content = """# John Doe

## Summary
Experienced software engineer with 10+ years of experience.

## Experience
- Senior Software Engineer at Tech Corp (2020-Present)
- Software Engineer at StartupCo (2015-2020)

## Skills
- Python, Java, JavaScript
- AWS, Docker, Kubernetes
- Agile, Scrum
"""
    
    output_file = test_dir / "basic_resume.md"
    success = writer.write(content, str(output_file))
    print(f"   ✓ Written to {output_file}: {success}")
    print(f"   ✓ File size: {output_file.stat().st_size} bytes")
    print()
    
    # Test 2: Write with backup
    print("2. Writing with backup creation:")
    updated_content = content.replace("10+ years", "12+ years")
    success = writer.write(updated_content, str(output_file))
    backups = list(test_dir.glob("basic_resume.md.backup.*"))
    print(f"   ✓ Updated file: {success}")
    print(f"   ✓ Backup created: {len(backups)} backup(s)")
    if backups:
        print(f"   ✓ Backup name: {backups[0].name}")
    print()
    
    # Test 3: Write with metadata
    print("3. Writing with metadata:")
    result = CustomizationResult(
        original_content=content,
        customized_content=updated_content,
        match_score=92.5,
        changes=[
            Change(
                type=ChangeType.CONTENT_REWRITE,
                section="Summary",
                description="Updated years of experience"
            ),
            Change(
                type=ChangeType.KEYWORD_ADDITION,
                section="Skills",
                description="Added cloud technologies"
            )
        ],
        integrated_keywords=["Python", "AWS", "Docker", "Kubernetes"],
        reordered_sections=[
            SectionChange(
                original_position=3,
                new_position=2,
                section_name="Skills"
            )
        ],
        timestamp=datetime.now()
    )
    
    metadata_file = test_dir / "resume_with_metadata.md"
    success = writer.write_with_metadata(
        updated_content,
        str(metadata_file),
        result
    )
    print(f"   ✓ Written with metadata: {success}")
    
    # Show first few lines with metadata
    if metadata_file.exists():
        lines = metadata_file.read_text().split('\n')[:10]
        print("   ✓ First 10 lines:")
        for line in lines:
            print(f"     {line}")
    print()
    
    # Test 4: Safe filename generation
    print("4. Safe filename generation:")
    test_titles = [
        "John's Resume: 2024",
        "Software Engineer / DevOps",
        "Resume (Final Version)",
        "My Resume<>:|?*.txt"
    ]
    
    for title in test_titles:
        safe_name = writer.generate_safe_filename(title)
        print(f"   '{title}' → '{safe_name}'")
    print()
    
    # Test 5: Atomic write
    print("5. Atomic write operation:")
    atomic_file = test_dir / "atomic_resume.md"
    success = writer.write(content, str(atomic_file), atomic=True)
    print(f"   ✓ Atomic write: {success}")
    print(f"   ✓ File exists: {atomic_file.exists()}")
    print()
    
    # Test 6: Write with confirmation
    print("6. Write with detailed confirmation:")
    confirm_file = test_dir / "confirmed_resume.md"
    result = writer.write_with_confirmation(content, str(confirm_file))
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✓ Path: {result['path']}")
    print(f"   ✓ Size: {result.get('size', 0)} bytes")
    print(f"   ✓ Lines: {result.get('lines', 0)}")
    print(f"   ✓ Timestamp: {result['timestamp']}")
    print()
    
    # Test 7: Different encodings
    print("7. Writing with different encodings:")
    unicode_content = """# José García

## Résumé
Software Engineer at Café Tech with 10+ años of experience.
"""
    
    # UTF-8
    utf8_file = test_dir / "utf8_resume.md"
    writer.write(unicode_content, str(utf8_file), encoding='utf-8')
    print(f"   ✓ UTF-8 file created: {utf8_file.exists()}")
    
    # Latin-1
    latin1_file = test_dir / "latin1_resume.md"
    writer.write(unicode_content, str(latin1_file), encoding='latin-1')
    print(f"   ✓ Latin-1 file created: {latin1_file.exists()}")
    
    print("\nAll OutputWriter tests completed! ✅")
    
    # Cleanup
    print("\nCleaning up test files...")
    import shutil
    shutil.rmtree(test_dir)
    print("Test directory removed.")


if __name__ == "__main__":
    test_output_writer()