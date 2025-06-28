# ABOUTME: OutputWriter implementation for saving customized resumes
# ABOUTME: Handles safe file writing, backups, and metadata preservation

"""Writers for saving customized resume files."""

import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, Union

from resume_customizer.models.result import CustomizationResult


class OutputWriter:
    """Writer for saving customized resume files with safety features."""
    
    def __init__(self):
        """Initialize the OutputWriter."""
        self.default_encoding = 'utf-8'
        self.backup_extension = '.backup'
    
    def write(
        self,
        content: str,
        filepath: str,
        encoding: Optional[str] = None,
        atomic: bool = False,
        max_backups: int = 5
    ) -> bool:
        """
        Write content to a file with safety checks.
        
        Args:
            content: The content to write
            filepath: Path to the output file
            encoding: File encoding (default: utf-8)
            atomic: Use atomic write (write to temp, then rename)
            max_backups: Maximum number of backups to keep
            
        Returns:
            True if successful, False otherwise
        """
        # Validate content
        if not self._validate_content(content):
            return False
        
        # Expand and resolve path
        path = Path(filepath).expanduser().resolve()
        
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            if path.exists():
                self._create_backup(path, max_backups)
            
            # Write the file
            if atomic:
                self._atomic_write(content, path, encoding or self.default_encoding)
            else:
                self._direct_write(content, path, encoding or self.default_encoding)
            
            return True
            
        except (OSError, IOError, PermissionError) as e:
            # Handle write errors gracefully
            return False
    
    def write_with_metadata(
        self,
        content: str,
        filepath: str,
        result: CustomizationResult,
        encoding: Optional[str] = None
    ) -> bool:
        """
        Write content with metadata comments.
        
        Args:
            content: The content to write
            filepath: Path to the output file
            result: CustomizationResult containing metadata
            encoding: File encoding
            
        Returns:
            True if successful, False otherwise
        """
        # Generate metadata comments
        metadata_lines = [
            "<!-- Resume customized by Claude Resume Assistant -->",
            f"<!-- Generated: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')} -->",
            f"<!-- Match Score: {result.match_score}% -->",
        ]
        
        if result.integrated_keywords:
            keywords_str = ", ".join(result.integrated_keywords)
            metadata_lines.append(f"<!-- Keywords: {keywords_str} -->")
        
        if result.changes:
            metadata_lines.append(f"<!-- Changes Applied: {len(result.changes)} -->")
        
        metadata_lines.append("<!-- ================================================ -->")
        metadata_lines.append("")  # Empty line after metadata
        
        # Prepend metadata to content
        full_content = "\n".join(metadata_lines) + content
        
        return self.write(full_content, filepath, encoding)
    
    def write_with_confirmation(
        self,
        content: str,
        filepath: str,
        encoding: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Write content and return detailed confirmation.
        
        Args:
            content: The content to write
            filepath: Path to the output file
            encoding: File encoding
            
        Returns:
            Dictionary with success status and details
        """
        path = Path(filepath).expanduser().resolve()
        
        success = self.write(content, filepath, encoding)
        
        result = {
            'success': success,
            'path': str(path),
            'timestamp': datetime.now().isoformat()
        }
        
        if success and path.exists():
            result['size'] = len(content)
            result['lines'] = content.count('\n') + 1
            
        return result
    
    def generate_safe_filename(self, title: str) -> str:
        """
        Generate a safe filename from a title.
        
        Args:
            title: The title to convert
            
        Returns:
            Safe filename string
        """
        # Replace unsafe characters
        safe_chars = re.sub(r'[<>:"/\\|?*]', '', title)
        # Replace apostrophes without adding underscore
        safe_chars = safe_chars.replace("'", "")
        # Replace spaces and special chars with underscores
        safe_chars = re.sub(r'[\s\-()]+', '_', safe_chars)
        # Remove leading/trailing underscores
        safe_chars = safe_chars.strip('_')
        
        return safe_chars or "resume"
    
    def _validate_content(self, content: Any) -> bool:
        """
        Validate content before writing.
        
        Args:
            content: Content to validate
            
        Returns:
            True if valid, False otherwise
        """
        if content is None:
            return False
        
        if isinstance(content, str) and len(content) == 0:
            return False
        
        return True
    
    def _create_backup(self, path: Path, max_backups: int) -> None:
        """
        Create a backup of existing file.
        
        Args:
            path: Path to the file to backup
            max_backups: Maximum number of backups to keep
        """
        if not path.exists():
            return
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = path.parent / f"{path.name}{self.backup_extension}.{timestamp}"
        
        # Copy file to backup
        shutil.copy2(path, backup_path)
        
        # Rotate old backups if needed
        self._rotate_backups(path, max_backups)
    
    def _rotate_backups(self, path: Path, max_backups: int) -> None:
        """
        Keep only the most recent backups.
        
        Args:
            path: Original file path
            max_backups: Maximum number of backups to keep
        """
        # Find all backup files
        backup_pattern = f"{path.name}{self.backup_extension}.*"
        backup_files = sorted(path.parent.glob(backup_pattern))
        
        # Remove oldest backups if exceeding limit
        while len(backup_files) > max_backups:
            oldest = backup_files.pop(0)
            oldest.unlink()
    
    def _direct_write(self, content: str, path: Path, encoding: str) -> None:
        """
        Write content directly to file.
        
        Args:
            content: Content to write
            path: File path
            encoding: File encoding
        """
        with open(path, 'w', encoding=encoding, newline='') as f:
            f.write(content)
    
    def _atomic_write(self, content: str, path: Path, encoding: str) -> None:
        """
        Write content atomically using temp file.
        
        Args:
            content: Content to write
            path: File path
            encoding: File encoding
        """
        # Write to temporary file in same directory
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding=encoding,
            dir=path.parent,
            delete=False,
            newline=''
        ) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()
            # Only fsync if we have a real file descriptor
            if hasattr(tmp_file, 'fileno') and callable(tmp_file.fileno):
                try:
                    os.fsync(tmp_file.fileno())
                except (TypeError, ValueError):
                    pass  # Mock object or invalid file descriptor
            tmp_path = tmp_file.name
        
        # Atomic rename
        Path(tmp_path).replace(path)