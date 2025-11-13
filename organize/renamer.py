
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from organize.utils import sanitize_filename, handle_name_collision


class FileRenamer:
    """Handle file renaming operations with various strategies"""
    
    def __init__(self, files: List[Path]):
        """
        Initialize file renamer.
        
        Args:
            files: List of file paths to rename
        """
        self.files = files
    
    def rename_numeric(self, start: int = 1, padding: int = 3, 
                      prefix: str = '', suffix: str = '') -> List[Dict]:
        """
        Rename files with numeric sequence.
        
        Args:
            start: Starting number
            padding: Number of digits for padding (e.g., 3 -> 001)
            prefix: Prefix to add before number
            suffix: Suffix to add after number (before extension)
            
        Returns:
            List of rename operations
        """
        changes = []
        
        for idx, file_path in enumerate(self.files):
            number = start + idx
            padded_number = str(number).zfill(padding)
            
            new_name = f"{prefix}{padded_number}{suffix}{file_path.suffix}"
            new_name = sanitize_filename(new_name)
            new_path = file_path.parent / new_name
            
            changes.append({
                'old_path': file_path,
                'new_path': new_path,
                'old_name': file_path.name,
                'new_name': new_name
            })
        
        return self._resolve_collisions(changes)
    
    def rename_alphabetical(self, reverse: bool = False, 
                          prefix: str = '', suffix: str = '') -> List[Dict]:
        """
        Rename files in alphabetical order.
        
        Args:
            reverse: Sort in reverse order
            prefix: Prefix to add to filename
            suffix: Suffix to add to filename (before extension)
            
        Returns:
            List of rename operations
        """
        sorted_files = sorted(self.files, key=lambda x: x.name.lower(), reverse=reverse)
        
        changes = []
        for file_path in sorted_files:
            stem = file_path.stem
            new_name = f"{prefix}{stem}{suffix}{file_path.suffix}"
            new_name = sanitize_filename(new_name)
            new_path = file_path.parent / new_name
            
            changes.append({
                'old_path': file_path,
                'new_path': new_path,
                'old_name': file_path.name,
                'new_name': new_name
            })
        
        return self._resolve_collisions(changes)
    
    def rename_by_creation_date(self, date_format: str = '%Y%m%d', 
                               prefix: str = '', suffix: str = '') -> List[Dict]:
        """
        Rename files based on creation date.
        
        Args:
            date_format: Date format string (e.g., '%Y%m%d')
            prefix: Prefix to add before date
            suffix: Suffix to add after date (before extension)
            
        Returns:
            List of rename operations
        """
        files_with_dates = []
        for file_path in self.files:
            try:
                ctime = file_path.stat().st_ctime
                files_with_dates.append((file_path, ctime))
            except (OSError, PermissionError):
                files_with_dates.append((file_path, 0))
        
        sorted_files = sorted(files_with_dates, key=lambda x: x[1])
        
        changes = []
        date_counter = {}
        
        for file_path, ctime in sorted_files:
            date_obj = datetime.fromtimestamp(ctime)
            date_str = date_obj.strftime(date_format)
            
            date_counter[date_str] = date_counter.get(date_str, 0) + 1
            if date_counter[date_str] > 1:
                counter_str = f"_{date_counter[date_str]}"
            else:
                counter_str = ""
            
            new_name = f"{prefix}{date_str}{counter_str}{suffix}{file_path.suffix}"
            new_name = sanitize_filename(new_name)
            new_path = file_path.parent / new_name
            
            changes.append({
                'old_path': file_path,
                'new_path': new_path,
                'old_name': file_path.name,
                'new_name': new_name
            })
        
        return self._resolve_collisions(changes)
    
    def rename_by_modification_date(self, date_format: str = '%Y%m%d',
                                   prefix: str = '', suffix: str = '') -> List[Dict]:
        """
        Rename files based on modification date.
        
        Args:
            date_format: Date format string (e.g., '%Y%m%d')
            prefix: Prefix to add before date
            suffix: Suffix to add after date (before extension)
            
        Returns:
            List of rename operations
        """
        files_with_dates = []
        for file_path in self.files:
            try:
                mtime = file_path.stat().st_mtime
                files_with_dates.append((file_path, mtime))
            except (OSError, PermissionError):
                files_with_dates.append((file_path, 0))
        
        sorted_files = sorted(files_with_dates, key=lambda x: x[1])
        
        changes = []
        date_counter = {}
        
        for file_path, mtime in sorted_files:
            date_obj = datetime.fromtimestamp(mtime)
            date_str = date_obj.strftime(date_format)
            
            date_counter[date_str] = date_counter.get(date_str, 0) + 1
            if date_counter[date_str] > 1:
                counter_str = f"_{date_counter[date_str]}"
            else:
                counter_str = ""
            
            new_name = f"{prefix}{date_str}{counter_str}{suffix}{file_path.suffix}"
            new_name = sanitize_filename(new_name)
            new_path = file_path.parent / new_name
            
            changes.append({
                'old_path': file_path,
                'new_path': new_path,
                'old_name': file_path.name,
                'new_name': new_name
            })
        
        return self._resolve_collisions(changes)
    
    def rename_by_size(self, ascending: bool = True, 
                      prefix: str = '', suffix: str = '') -> List[Dict]:
        """
        Rename files based on size.
        
        Args:
            ascending: Sort in ascending order (smallest first)
            prefix: Prefix to add to filename
            suffix: Suffix to add after size (before extension)
            
        Returns:
            List of rename operations
        """
        files_with_sizes = []
        for file_path in self.files:
            try:
                size = file_path.stat().st_size
                files_with_sizes.append((file_path, size))
            except (OSError, PermissionError):
                files_with_sizes.append((file_path, 0))
        
        sorted_files = sorted(files_with_sizes, key=lambda x: x[1], reverse=not ascending)
        
        changes = []
        for idx, (file_path, size) in enumerate(sorted_files, 1):
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f}KB"
            elif size < 1024 * 1024 * 1024:
                size_str = f"{size / (1024 * 1024):.1f}MB"
            else:
                size_str = f"{size / (1024 * 1024 * 1024):.1f}GB"
            
            new_name = f"{prefix}{idx:03d}_{size_str}{suffix}{file_path.suffix}"
            new_name = sanitize_filename(new_name)
            new_path = file_path.parent / new_name
            
            changes.append({
                'old_path': file_path,
                'new_path': new_path,
                'old_name': file_path.name,
                'new_name': new_name
            })
        
        return self._resolve_collisions(changes)
    
    def rename_by_extension(self, prefix: str = '', suffix: str = '',
                          keep_original: bool = True) -> List[Dict]:
        """
        Rename files grouped by extension.
        
        Args:
            prefix: Prefix to add to filename
            suffix: Suffix to add to filename (before extension)
            keep_original: Keep original filename
            
        Returns:
            List of rename operations
        """
        ext_groups = {}
        for file_path in self.files:
            ext = file_path.suffix.lower()
            if ext not in ext_groups:
                ext_groups[ext] = []
            ext_groups[ext].append(file_path)
        
        changes = []
        for ext, group_files in ext_groups.items():
            for idx, file_path in enumerate(group_files, 1):
                if keep_original:
                    stem = file_path.stem
                    new_name = f"{prefix}{stem}{suffix}{file_path.suffix}"
                else:
                    ext_name = ext[1:] if ext else 'no_ext'
                    new_name = f"{prefix}{ext_name}_{idx:03d}{suffix}{file_path.suffix}"
                
                new_name = sanitize_filename(new_name)
                new_path = file_path.parent / new_name
                
                changes.append({
                    'old_path': file_path,
                    'new_path': new_path,
                    'old_name': file_path.name,
                    'new_name': new_name
                })
        
        return self._resolve_collisions(changes)
    
    def apply_custom_prefix_suffix(self, prefix: str = '', 
                                   suffix: str = '') -> List[Dict]:
        """
        Apply custom prefix and/or suffix to filenames.
        
        Args:
            prefix: Prefix to add to filename
            suffix: Suffix to add to filename (before extension)
            
        Returns:
            List of rename operations
        """
        changes = []
        
        for file_path in self.files:
            stem = file_path.stem
            new_name = f"{prefix}{stem}{suffix}{file_path.suffix}"
            new_name = sanitize_filename(new_name)
            new_path = file_path.parent / new_name
            
            changes.append({
                'old_path': file_path,
                'new_path': new_path,
                'old_name': file_path.name,
                'new_name': new_name
            })
        
        return self._resolve_collisions(changes)
    
    def _resolve_collisions(self, changes: List[Dict]) -> List[Dict]:
        """
        Resolve naming collisions by checking for duplicates.
        
        Args:
            changes: List of proposed rename operations
            
        Returns:
            List of rename operations with collisions resolved
        """
        new_names = {}
        resolved_changes = []
        
        for change in changes:
            new_path = change['new_path']
            
            original_path = new_path
            counter = 1
            
            while (new_path.exists() and new_path != change['old_path']) or \
                  str(new_path) in new_names:
                stem = original_path.stem
                suffix = original_path.suffix
                new_name = f"{stem} ({counter}){suffix}"
                new_path = original_path.parent / new_name
                counter += 1
            
            change['new_path'] = new_path
            change['new_name'] = new_path.name
            new_names[str(new_path)] = True
            
            resolved_changes.append(change)
        
        return resolved_changes


