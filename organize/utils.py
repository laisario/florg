"""Utility functions for file operations and path handling"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, Optional


def sanitize_filename(name: str) -> str:
    """
    Remove invalid characters from filename.
    
    Args:
        name: The filename to sanitize
        
    Returns:
        Sanitized filename safe for filesystem
    """
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, '_', name)
    
    sanitized = sanitized.strip('. ')
    
    if not sanitized:
        sanitized = 'unnamed'
    
    if len(sanitized) > 255:
        name_parts = sanitized.rsplit('.', 1)
        if len(name_parts) == 2:
            name_part, ext = name_parts
            max_name_len = 255 - len(ext) - 1
            sanitized = name_part[:max_name_len] + '.' + ext
        else:
            sanitized = sanitized[:255]
    
    return sanitized


def handle_name_collision(path: Path) -> Path:
    """
    Handle filename collision by appending number.
    
    Args:
        path: The target path that might collide
        
    Returns:
        Path with number appended if collision exists
    """
    if not path.exists():
        return path
    
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def format_file_size(bytes_size: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            if unit == 'B':
                return f"{bytes_size} {unit}"
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def get_file_stats(path: Path) -> Dict:
    """
    Get comprehensive file statistics.
    
    Args:
        path: Path to the file
        
    Returns:
        Dictionary with file statistics
    """
    try:
        stat = path.stat()
        return {
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'is_symlink': path.is_symlink(),
            'extension': path.suffix.lower(),
            'name': path.name,
            'stem': path.stem,
        }
    except (OSError, PermissionError) as e:
        return {
            'error': str(e),
            'name': path.name,
        }


def safe_move(old_path: Path, new_path: Path, overwrite: bool = False) -> bool:
    """
    Safely move/rename a file with error handling.
    
    Args:
        old_path: Source path
        new_path: Destination path
        overwrite: Whether to overwrite existing files
        
    Returns:
        True if successful, False otherwise
    """
    try:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        if new_path.exists() and not overwrite:
            new_path = handle_name_collision(new_path)
        
        shutil.move(str(old_path), str(new_path))
        return True
        
    except (OSError, PermissionError, shutil.Error) as e:
        print(f"Error moving {old_path} to {new_path}: {e}")
        return False


def get_size_category(size_bytes: int) -> str:
    """
    Categorize file size into predefined ranges.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Size category name
    """
    kb = 1024
    mb = kb * 1024
    gb = mb * 1024
    
    if size_bytes < 10 * kb:
        return "Tiny (< 10 KB)"
    elif size_bytes < 1 * mb:
        return "Small (10 KB - 1 MB)"
    elif size_bytes < 10 * mb:
        return "Medium (1 MB - 10 MB)"
    elif size_bytes < 100 * mb:
        return "Large (10 MB - 100 MB)"
    else:
        return "Huge (> 100 MB)"


def is_hidden(path: Path) -> bool:
    """
    Check if a file or directory is hidden.
    
    Args:
        path: Path to check
        
    Returns:
        True if hidden, False otherwise
    """
    if path.name.startswith('.'):
        return True
    
    if os.name == 'nt':
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            return attrs != -1 and attrs & 2
        except:
            pass
    
    return False


