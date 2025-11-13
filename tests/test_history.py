"""Tests for the history module"""

import pytest
from pathlib import Path
from organize.history import (
    save_operation,
    load_last_operation,
    revert_operation,
    clear_history,
    HISTORY_FILE
)


@pytest.fixture
def clean_history():
    """Ensure clean history before and after test"""
    clear_history()
    yield
    clear_history()


@pytest.fixture
def temp_files(tmp_path):
    """Create temporary test files"""
    files = []
    for i in range(3):
        file_path = tmp_path / f"file_{i}.txt"
        file_path.write_text(f"Content {i}")
        files.append(file_path)
    return tmp_path, files


def test_save_operation(clean_history, temp_files):
    """Test saving operation to history"""
    directory, files = temp_files
    
    changes = [
        {
            'old_path': files[0],
            'new_path': directory / 'renamed_0.txt'
        }
    ]
    
    result = save_operation(str(directory), 'rename', changes)
    assert result is True
    assert HISTORY_FILE.exists()


def test_load_last_operation(clean_history, temp_files):
    """Test loading last operation from history"""
    directory, files = temp_files
    
    changes = [
        {
            'old_path': files[0],
            'new_path': directory / 'renamed_0.txt'
        }
    ]
    
    save_operation(str(directory), 'rename', changes)
    
    # Load operation
    operation = load_last_operation(str(directory))
    
    assert operation is not None
    assert operation['operation_type'] == 'rename'
    assert operation['directory'] == str(directory)
    assert len(operation['changes']) == 1


def test_load_nonexistent_operation(clean_history, tmp_path):
    """Test loading operation when none exists"""
    operation = load_last_operation(str(tmp_path))
    assert operation is None


def test_revert_operation(clean_history, temp_files):
    """Test reverting an operation"""
    directory, files = temp_files
    
    # Rename a file
    old_path = files[0]
    new_path = directory / 'renamed.txt'
    old_path.rename(new_path)
    
    # Save operation
    changes = [
        {
            'old_path': old_path,
            'new_path': new_path
        }
    ]
    save_operation(str(directory), 'rename', changes)
    
    # Load and revert
    operation = load_last_operation(str(directory))
    result = revert_operation(operation)
    
    assert result is True
    assert old_path.exists()
    assert not new_path.exists()


def test_revert_multiple_files(clean_history, temp_files):
    """Test reverting multiple file operations"""
    directory, files = temp_files
    
    changes = []
    new_paths = []
    
    # Rename all files
    for i, old_path in enumerate(files):
        new_path = directory / f'renamed_{i}.txt'
        old_path.rename(new_path)
        new_paths.append(new_path)
        changes.append({
            'old_path': old_path,
            'new_path': new_path
        })
    
    # Save operation
    save_operation(str(directory), 'rename', changes)
    
    # Revert
    operation = load_last_operation(str(directory))
    result = revert_operation(operation)
    
    assert result is True
    
    # Check all files are back to original names
    for original_file in files:
        assert original_file.exists()
    
    for new_file in new_paths:
        assert not new_file.exists()


def test_clear_history(clean_history, temp_files):
    """Test clearing history"""
    directory, files = temp_files
    
    changes = [
        {
            'old_path': files[0],
            'new_path': directory / 'renamed.txt'
        }
    ]
    
    save_operation(str(directory), 'rename', changes)
    assert HISTORY_FILE.exists()
    
    clear_history()
    assert not HISTORY_FILE.exists()


def test_multiple_directories(clean_history, tmp_path):
    """Test saving operations for multiple directories"""
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()
    
    # Create files in both directories
    file1 = dir1 / "file.txt"
    file2 = dir2 / "file.txt"
    file1.write_text("Content 1")
    file2.write_text("Content 2")
    
    # Save operations for both
    changes1 = [{'old_path': file1, 'new_path': dir1 / 'renamed.txt'}]
    changes2 = [{'old_path': file2, 'new_path': dir2 / 'renamed.txt'}]
    
    save_operation(str(dir1), 'rename', changes1)
    save_operation(str(dir2), 'rename', changes2)
    
    # Load operations
    op1 = load_last_operation(str(dir1))
    op2 = load_last_operation(str(dir2))
    
    assert op1 is not None
    assert op2 is not None
    assert op1['directory'] == str(dir1)
    assert op2['directory'] == str(dir2)



