"""History tracking and undo functionality"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from organize.utils import safe_move


HISTORY_FILE = Path.home() / '.florg_history.json'


def save_operation(directory: str, operation_type: str, changes: List[Dict]) -> bool:
    """
    Save an operation to history for undo capability.
    
    Args:
        directory: Directory where operation was performed
        operation_type: Type of operation ('rename' or 'group')
        changes: List of changes made (old/new paths)
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        history = _load_history()
        
        operation = {
            'timestamp': datetime.now().isoformat(),
            'directory': str(directory),
            'operation_type': operation_type,
            'changes': [
                {
                    'old': str(change['old_path']),
                    'new': str(change['new_path'])
                }
                for change in changes
            ]
        }
        
        dir_key = str(Path(directory).resolve())
        history[dir_key] = operation
        
        _save_history(history)
        return True
        
    except Exception as e:
        print(f"Error saving operation to history: {e}")
        return False


def load_last_operation(directory: Optional[str] = None) -> Optional[Dict]:
    """
    Load the last operation for a directory.
    
    Args:
        directory: Directory to load operation for (optional)
        
    Returns:
        Operation dictionary or None if not found
    """
    try:
        history = _load_history()
        
        if not history:
            return None
        
        if directory:
            dir_key = str(Path(directory).resolve())
            return history.get(dir_key)
        else:
            latest = None
            latest_time = None
            
            for operation in history.values():
                op_time = datetime.fromisoformat(operation['timestamp'])
                if latest_time is None or op_time > latest_time:
                    latest = operation
                    latest_time = op_time
            
            return latest
        
    except Exception as e:
        print(f"Error loading operation from history: {e}")
        return None


def revert_operation(operation: Dict) -> bool:
    """
    Revert an operation by moving files back to original locations.
    
    Args:
        operation: Operation dictionary to revert
        
    Returns:
        True if successful, False otherwise
    """
    if not operation:
        return False
    
    changes = operation.get('changes', [])
    if not changes:
        return False
    
    successful = []
    failed = []
    
    for change in reversed(changes):
        old_path = Path(change['old'])
        new_path = Path(change['new'])
        
        if not new_path.exists():
            if old_path.exists():
                successful.append(change)
                continue
            else:
                failed.append({
                    'change': change,
                    'reason': 'File not found at new location'
                })
                continue
        
        try:
            old_path.parent.mkdir(parents=True, exist_ok=True)
            
            if safe_move(new_path, old_path, overwrite=False):
                successful.append(change)
            else:
                failed.append({
                    'change': change,
                    'reason': 'Failed to move file'
                })
        except Exception as e:
            failed.append({
                'change': change,
                'reason': str(e)
            })
    
    if operation.get('operation_type') == 'group':
        _cleanup_empty_directories(operation)
    
    if failed:
        print(f"\nWarning: {len(failed)} file(s) could not be reverted:")
        for item in failed[:5]:
            print(f"  - {Path(item['change']['new']).name}: {item['reason']}")
        if len(failed) > 5:
            print(f"  ... and {len(failed) - 5} more")
    
    if not failed:
        _remove_operation_from_history(operation)
    
    return len(successful) > 0


def clear_history() -> bool:
    """
    Clear all operation history.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
        return True
    except Exception as e:
        print(f"Error clearing history: {e}")
        return False


def _load_history() -> Dict:
    """
    Load history from file.
    
    Returns:
        History dictionary
    """
    if not HISTORY_FILE.exists():
        return {}
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_history(history: Dict) -> None:
    """
    Save history to file.
    
    Args:
        history: History dictionary to save
    """
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except IOError as e:
        print(f"Error saving history file: {e}")


def _remove_operation_from_history(operation: Dict) -> None:
    """
    Remove an operation from history after successful undo.
    
    Args:
        operation: Operation to remove
    """
    try:
        history = _load_history()
        
        dir_key = str(Path(operation['directory']).resolve())
        if dir_key in history:
            if history[dir_key]['timestamp'] == operation['timestamp']:
                del history[dir_key]
                _save_history(history)
    except Exception as e:
        print(f"Error removing operation from history: {e}")


def _cleanup_empty_directories(operation: Dict) -> None:
    """
    Remove empty directories created during grouping operation.
    
    Args:
        operation: Operation that created directories
    """
    try:
        directory = Path(operation['directory'])
        
        folders = set()
        for change in operation.get('changes', []):
            new_path = Path(change['new'])
            if new_path.parent != directory:
                folders.add(new_path.parent)
        
        for folder in folders:
            try:
                if folder.exists() and folder.is_dir():
                    if not any(folder.iterdir()):
                        folder.rmdir()
            except (OSError, PermissionError):
                pass
                
    except Exception:
        pass


def get_history_summary() -> List[Dict]:
    """
    Get summary of all operations in history.
    
    Returns:
        List of operation summaries
    """
    try:
        history = _load_history()
        
        summaries = []
        for operation in history.values():
            summaries.append({
                'directory': operation['directory'],
                'operation_type': operation['operation_type'],
                'timestamp': operation['timestamp'],
                'file_count': len(operation.get('changes', []))
            })
        
        summaries.sort(key=lambda x: x['timestamp'], reverse=True)
        return summaries
        
    except Exception:
        return []


