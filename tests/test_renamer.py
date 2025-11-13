"""Tests for the renamer module"""

import pytest
from pathlib import Path
from organize.renamer import FileRenamer


@pytest.fixture
def temp_files(tmp_path):
    """Create temporary test files"""
    files = []
    for i in range(5):
        file_path = tmp_path / f"test_file_{i}.txt"
        file_path.write_text(f"Content {i}")
        files.append(file_path)
    return files


def test_rename_numeric(temp_files):
    """Test numeric renaming strategy"""
    renamer = FileRenamer(temp_files)
    changes = renamer.rename_numeric(start=1, padding=3, prefix="doc_", suffix="")
    
    assert len(changes) == 5
    assert changes[0]['new_name'] == "doc_001.txt"
    assert changes[4]['new_name'] == "doc_005.txt"


def test_rename_numeric_custom_padding(temp_files):
    """Test numeric renaming with custom padding"""
    renamer = FileRenamer(temp_files)
    changes = renamer.rename_numeric(start=10, padding=5, prefix="", suffix="")
    
    assert changes[0]['new_name'] == "00010.txt"
    assert changes[4]['new_name'] == "00014.txt"


def test_rename_alphabetical(temp_files):
    """Test alphabetical renaming strategy"""
    renamer = FileRenamer(temp_files)
    changes = renamer.rename_alphabetical(reverse=False, prefix="alpha_", suffix="")
    
    assert len(changes) == 5
    # All files should have prefix
    for change in changes:
        assert change['new_name'].startswith("alpha_")


def test_rename_alphabetical_reverse(temp_files):
    """Test alphabetical renaming in reverse"""
    renamer = FileRenamer(temp_files)
    changes_normal = renamer.rename_alphabetical(reverse=False)
    changes_reverse = renamer.rename_alphabetical(reverse=True)
    
    # First item in reverse should be last in normal
    assert changes_normal[-1]['old_path'] == changes_reverse[0]['old_path']


def test_rename_by_creation_date(temp_files):
    """Test renaming by creation date"""
    renamer = FileRenamer(temp_files)
    changes = renamer.rename_by_creation_date(date_format='%Y%m%d', prefix="", suffix="")
    
    assert len(changes) == 5
    # All new names should contain 8 digits (YYYYMMDD)
    for change in changes:
        name_without_ext = change['new_name'].rsplit('.', 1)[0]
        assert any(c.isdigit() for c in name_without_ext)


def test_rename_by_modification_date(temp_files):
    """Test renaming by modification date"""
    renamer = FileRenamer(temp_files)
    changes = renamer.rename_by_modification_date(date_format='%Y-%m-%d', prefix="mod_", suffix="")
    
    assert len(changes) == 5
    for change in changes:
        assert change['new_name'].startswith("mod_")


def test_rename_by_size(temp_files):
    """Test renaming by size"""
    renamer = FileRenamer(temp_files)
    changes = renamer.rename_by_size(ascending=True, prefix="", suffix="")
    
    assert len(changes) == 5
    # Names should contain size information
    for change in changes:
        assert 'B' in change['new_name'] or 'KB' in change['new_name']


def test_rename_by_extension(temp_files):
    """Test renaming by extension"""
    renamer = FileRenamer(temp_files)
    changes = renamer.rename_by_extension(prefix="ext_", suffix="", keep_original=True)
    
    assert len(changes) == 5
    for change in changes:
        assert change['new_name'].startswith("ext_")


def test_custom_prefix_suffix(temp_files):
    """Test custom prefix/suffix application"""
    renamer = FileRenamer(temp_files)
    changes = renamer.apply_custom_prefix_suffix(prefix="PREFIX_", suffix="_SUFFIX")
    
    assert len(changes) == 5
    for change in changes:
        assert change['new_name'].startswith("PREFIX_")
        assert "_SUFFIX.txt" in change['new_name']


def test_collision_resolution(tmp_path):
    """Test that naming collisions are resolved"""
    # Create files that would collide after rename
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    existing = tmp_path / "doc_001.txt"
    
    file1.write_text("Content 1")
    file2.write_text("Content 2")
    existing.write_text("Existing")
    
    renamer = FileRenamer([file1, file2])
    changes = renamer.rename_numeric(start=1, padding=3, prefix="doc_", suffix="")
    
    # Second file should have collision resolution
    assert changes[0]['new_name'] == "doc_001 (1).txt"  # Collision with existing
    assert changes[1]['new_name'] == "doc_002.txt"


def test_empty_file_list():
    """Test renaming with empty file list"""
    renamer = FileRenamer([])
    changes = renamer.rename_numeric()
    
    assert len(changes) == 0



