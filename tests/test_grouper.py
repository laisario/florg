"""Tests for the grouper module"""

import pytest
from pathlib import Path
from organize.grouper import FileGrouper, apply_renaming_to_groups


@pytest.fixture
def temp_files(tmp_path):
    """Create temporary test files with different extensions"""
    files = []
    
    # Create some text files
    for i in range(3):
        file_path = tmp_path / f"document_{i}.txt"
        file_path.write_text(f"Text content {i}")
        files.append(file_path)
    
    # Create some image files
    for i in range(2):
        file_path = tmp_path / f"image_{i}.jpg"
        file_path.write_text(f"Image data {i}")
        files.append(file_path)
    
    return files


def test_group_by_extension(temp_files):
    """Test grouping files by extension"""
    grouper = FileGrouper(temp_files)
    groups = grouper.group_by_extension()
    
    # Should have 2 groups: txt and jpg
    assert len(groups) == 2
    
    # Find txt and jpg groups
    txt_group = next(g for g in groups if g['folder'] == 'txt')
    jpg_group = next(g for g in groups if g['folder'] == 'jpg')
    
    assert len(txt_group['files']) == 3
    assert len(jpg_group['files']) == 2


def test_group_by_creation_date(temp_files):
    """Test grouping files by creation date"""
    grouper = FileGrouper(temp_files)
    groups = grouper.group_by_creation_date(date_format='%Y-%m-%d')
    
    # All files created at same time should be in one group
    assert len(groups) >= 1
    
    # Total files should match
    total_files = sum(len(g['files']) for g in groups)
    assert total_files == 5


def test_group_by_modification_date(temp_files):
    """Test grouping files by modification date"""
    grouper = FileGrouper(temp_files)
    groups = grouper.group_by_modification_date(date_format='%Y-%m-%d')
    
    assert len(groups) >= 1
    total_files = sum(len(g['files']) for g in groups)
    assert total_files == 5


def test_group_by_size_range(temp_files):
    """Test grouping files by size range"""
    grouper = FileGrouper(temp_files)
    groups = grouper.group_by_size_range()
    
    # All test files are small, should be in one size category
    assert len(groups) >= 1
    
    # Check that folder names contain size ranges
    for group in groups:
        assert any(keyword in group['folder'] for keyword in ['Tiny', 'Small', 'Medium', 'Large', 'Huge'])


def test_group_operations_structure(temp_files):
    """Test that group operations have correct structure"""
    grouper = FileGrouper(temp_files)
    groups = grouper.group_by_extension()
    
    for group in groups:
        assert 'folder' in group
        assert 'files' in group
        assert 'moves' in group
        
        # Each move should have required fields
        for move in group['moves']:
            assert 'old_path' in move
            assert 'new_path' in move
            assert 'old_name' in move
            assert 'new_name' in move


def test_apply_renaming_to_groups(temp_files):
    """Test applying renaming to grouped files"""
    from organize.renamer import FileRenamer
    
    # Get rename changes
    renamer = FileRenamer(temp_files)
    rename_changes = renamer.rename_numeric(start=1, padding=3, prefix="file_", suffix="")
    
    # Get grouping
    grouper = FileGrouper(temp_files)
    groups = grouper.group_by_extension()
    
    # Apply renaming to groups
    updated_groups = apply_renaming_to_groups(groups, rename_changes)
    
    # Check that files have new names
    for group in updated_groups:
        for move in group['moves']:
            assert move['new_name'].startswith("file_")


def test_empty_file_list():
    """Test grouping with empty file list"""
    grouper = FileGrouper([])
    groups = grouper.group_by_extension()
    
    assert len(groups) == 0


def test_files_without_extension(tmp_path):
    """Test grouping files without extensions"""
    # Create files without extensions
    file1 = tmp_path / "README"
    file2 = tmp_path / "LICENSE"
    
    file1.write_text("Readme content")
    file2.write_text("License content")
    
    grouper = FileGrouper([file1, file2])
    groups = grouper.group_by_extension()
    
    # Should have a 'no_extension' group
    assert len(groups) == 1
    assert groups[0]['folder'] == 'no_extension'
    assert len(groups[0]['files']) == 2



