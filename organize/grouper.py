"""File grouping logic for organizing files into folders"""

from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from organize.utils import get_size_category, sanitize_filename


class FileGrouper:
    """Handle file grouping operations"""
    
    def __init__(self, files: List[Path]):
        """
        Initialize file grouper.
        
        Args:
            files: List of file paths to group
        """
        self.files = files
    
    def group_by_creation_date(self, date_format: str = '%Y-%m-%d') -> List[Dict]:
        """
        Group files by creation date into folders.
        
        Args:
            date_format: Date format for folder names (e.g., '%Y-%m-%d')
            
        Returns:
            List of grouping operations
        """
        groups = {}
        
        for file_path in self.files:
            try:
                ctime = file_path.stat().st_ctime
                date_obj = datetime.fromtimestamp(ctime)
                date_str = date_obj.strftime(date_format)
            except (OSError, PermissionError):
                date_str = 'unknown_date'
            
            if date_str not in groups:
                groups[date_str] = []
            groups[date_str].append(file_path)
        
        return self._create_group_operations(groups)
    
    def group_by_modification_date(self, date_format: str = '%Y-%m-%d') -> List[Dict]:
        """
        Group files by modification date into folders.
        
        Args:
            date_format: Date format for folder names (e.g., '%Y-%m-%d')
            
        Returns:
            List of grouping operations
        """
        groups = {}
        
        for file_path in self.files:
            try:
                mtime = file_path.stat().st_mtime
                date_obj = datetime.fromtimestamp(mtime)
                date_str = date_obj.strftime(date_format)
            except (OSError, PermissionError):
                date_str = 'unknown_date'
            
            if date_str not in groups:
                groups[date_str] = []
            groups[date_str].append(file_path)
        
        return self._create_group_operations(groups)
    
    def group_by_size_range(self) -> List[Dict]:
        """
        Group files by size ranges into folders.
        
        Returns:
            List of grouping operations
        """
        groups = {
            'Tiny (< 10 KB)': [],
            'Small (10 KB - 1 MB)': [],
            'Medium (1 MB - 10 MB)': [],
            'Large (10 MB - 100 MB)': [],
            'Huge (> 100 MB)': []
        }
        
        for file_path in self.files:
            try:
                size = file_path.stat().st_size
                category = get_size_category(size)
                groups[category].append(file_path)
            except (OSError, PermissionError):
                pass
        
        groups = {k: v for k, v in groups.items() if v}
        
        return self._create_group_operations(groups)
    
    def group_by_extension(self) -> List[Dict]:
        """
        Group files by file extension into folders.
        
        Returns:
            List of grouping operations
        """
        groups = {}
        
        for file_path in self.files:
            ext = file_path.suffix.lower()
            
            if ext:
                folder_name = ext[1:]
            else:
                folder_name = 'no_extension'
            
            if folder_name not in groups:
                groups[folder_name] = []
            groups[folder_name].append(file_path)
        
        return self._create_group_operations(groups)
    
    def _create_group_operations(self, groups: Dict[str, List[Path]]) -> List[Dict]:
        """
        Create grouping operations from grouped files.
        
        Args:
            groups: Dictionary mapping folder names to file lists
            
        Returns:
            List of grouping operations
        """
        operations = []
        
        for folder_name, files in groups.items():
            if not files:
                continue
            
            folder_name = sanitize_filename(folder_name)
            
            moves = []
            for file_path in files:
                new_path = file_path.parent / folder_name / file_path.name
                moves.append({
                    'old_path': file_path,
                    'new_path': new_path,
                    'old_name': file_path.name,
                    'new_name': file_path.name
                })
            
            operations.append({
                'folder': folder_name,
                'files': files,
                'moves': moves
            })
        
        return operations


def apply_renaming_to_groups(groups: List[Dict], rename_changes: List[Dict]) -> List[Dict]:
    """
    Apply renaming changes to grouped files.
    
    This combines grouping and renaming operations, applying the new names
    to files before they are moved into groups.
    
    Args:
        groups: List of grouping operations
        rename_changes: List of renaming operations
        
    Returns:
        Updated list of grouping operations with renamed files
    """
    rename_map = {}
    for change in rename_changes:
        old_path = change['old_path']
        new_name = change['new_name']
        rename_map[str(old_path)] = new_name
    
    updated_groups = []
    for group in groups:
        updated_moves = []
        for move in group['moves']:
            old_path = move['old_path']
            
            if str(old_path) in rename_map:
                new_name = rename_map[str(old_path)]
            else:
                new_name = move['new_name']
            
            new_path = move['new_path'].parent / new_name
            
            updated_moves.append({
                'old_path': old_path,
                'new_path': new_path,
                'old_name': move['old_name'],
                'new_name': new_name
            })
        
        updated_groups.append({
            'folder': group['folder'],
            'files': group['files'],
            'moves': updated_moves
        })
    
    return updated_groups


