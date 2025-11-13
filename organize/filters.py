"""File filtering logic for the organize tool"""

from pathlib import Path
from typing import List, Optional, Set
from organize.utils import is_hidden


class FileFilter:
    """Handle file filtering operations"""
    
    def __init__(self, directory: Path):
        """
        Initialize file filter.
        
        Args:
            directory: Directory to filter files from
        """
        self.directory = Path(directory)
    
    def get_all_files(self, recursive: bool = False, exclude_hidden: bool = True) -> List[Path]:
        """
        Get all files in directory.
        
        Args:
            recursive: Whether to search recursively
            exclude_hidden: Whether to exclude hidden files
            
        Returns:
            List of file paths
        """
        pattern = '**/*' if recursive else '*'
        files = []
        
        try:
            for item in self.directory.glob(pattern):
                if item.is_file():
                    if exclude_hidden and is_hidden(item):
                        continue
                    files.append(item)
        except PermissionError:
            pass
        
        return sorted(files)
    
    def filter_by_extensions(self, extensions: List[str], 
        recursive: bool = False, 
        exclude_hidden: bool = True) -> List[Path]:
        """
        Filter files by extensions.
        
        Args:
            extensions: List of extensions (e.g., ['.txt', '.pdf'])
            recursive: Whether to search recursively
            exclude_hidden: Whether to exclude hidden files
            
        Returns:
            List of filtered file paths
        """
        normalized_exts = set()
        for ext in extensions:
            ext = ext.strip().lower()
            if not ext.startswith('.'):
                ext = '.' + ext
            normalized_exts.add(ext)
        
        all_files = self.get_all_files(recursive, exclude_hidden)
        return [f for f in all_files if f.suffix.lower() in normalized_exts]
    
    def filter_by_size(self, min_size: Optional[int] = None, 
                      max_size: Optional[int] = None,
                      recursive: bool = False,
                      exclude_hidden: bool = True) -> List[Path]:
        """
        Filter files by size range.
        
        Args:
            min_size: Minimum size in bytes
            max_size: Maximum size in bytes
            recursive: Whether to search recursively
            exclude_hidden: Whether to exclude hidden files
            
        Returns:
            List of filtered file paths
        """
        all_files = self.get_all_files(recursive, exclude_hidden)
        filtered = []
        
        for file_path in all_files:
            try:
                size = file_path.stat().st_size
                if min_size is not None and size < min_size:
                    continue
                if max_size is not None and size > max_size:
                    continue
                filtered.append(file_path)
            except (OSError, PermissionError):
                continue
        
        return filtered
    
    def get_unique_extensions(self, recursive: bool = False, 
                            exclude_hidden: bool = True) -> Set[str]:
        """
        Get all unique file extensions in directory.
        
        Args:
            recursive: Whether to search recursively
            exclude_hidden: Whether to exclude hidden files
            
        Returns:
            Set of unique extensions
        """
        all_files = self.get_all_files(recursive, exclude_hidden)
        extensions = set()
        
        for file_path in all_files:
            ext = file_path.suffix.lower()
            if ext:
                extensions.add(ext)
        
        return extensions
    
    def get_extension_counts(self, recursive: bool = False,
                           exclude_hidden: bool = True) -> dict:
        """
        Get count of files for each extension.
        
        Args:
            recursive: Whether to search recursively
            exclude_hidden: Whether to exclude hidden files
            
        Returns:
            Dictionary mapping extensions to counts
        """
        all_files = self.get_all_files(recursive, exclude_hidden)
        counts = {}
        
        for file_path in all_files:
            ext = file_path.suffix.lower()
            if ext:
                counts[ext] = counts.get(ext, 0) + 1
            else:
                counts['(no extension)'] = counts.get('(no extension)', 0) + 1
        
        return counts


def parse_extensions_string(extensions_str: str) -> List[str]:
    """
    Parse comma-separated extensions string.
    
    Args:
        extensions_str: Comma-separated extensions (e.g., ".txt,.pdf,jpg")
        
    Returns:
        List of normalized extensions
    """
    if not extensions_str:
        return []
    
    extensions = []
    for ext in extensions_str.split(','):
        ext = ext.strip()
        if ext:
            extensions.append(ext)
    
    return extensions


