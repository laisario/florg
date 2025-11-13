"""Tests for the filters module"""

import pytest
from pathlib import Path
from organize.filters import FileFilter, parse_extensions_string


@pytest.fixture
def temp_directory(tmp_path):
    """Create temporary directory with various files"""
    # Create files with different extensions
    (tmp_path / "doc1.txt").write_text("Text 1")
    (tmp_path / "doc2.txt").write_text("Text 2")
    (tmp_path / "image1.jpg").write_text("Image 1")
    (tmp_path / "image2.png").write_text("Image 2")
    (tmp_path / "data.csv").write_text("Data")
    (tmp_path / "README").write_text("Readme")  # No extension
    
    # Create hidden file
    hidden = tmp_path / ".hidden"
    hidden.write_text("Hidden")
    
    return tmp_path


def test_get_all_files(temp_directory):
    """Test getting all files from directory"""
    file_filter = FileFilter(temp_directory)
    files = file_filter.get_all_files(exclude_hidden=True)
    
    # Should get 6 files (excluding .hidden)
    assert len(files) == 6


def test_get_all_files_include_hidden(temp_directory):
    """Test getting all files including hidden"""
    file_filter = FileFilter(temp_directory)
    files = file_filter.get_all_files(exclude_hidden=False)
    
    # Should get 7 files (including .hidden)
    assert len(files) == 7


def test_filter_by_extensions(temp_directory):
    """Test filtering by extensions"""
    file_filter = FileFilter(temp_directory)
    
    # Filter for text files
    txt_files = file_filter.filter_by_extensions(['.txt'])
    assert len(txt_files) == 2
    
    # Filter for image files
    img_files = file_filter.filter_by_extensions(['.jpg', '.png'])
    assert len(img_files) == 2


def test_filter_by_extensions_without_dot(temp_directory):
    """Test filtering by extensions without leading dot"""
    file_filter = FileFilter(temp_directory)
    
    # Should work without dot
    txt_files = file_filter.filter_by_extensions(['txt'])
    assert len(txt_files) == 2


def test_filter_by_extensions_case_insensitive(temp_directory):
    """Test that extension filtering is case insensitive"""
    # Create file with uppercase extension
    uppercase_file = temp_directory / "document.TXT"
    uppercase_file.write_text("Uppercase")
    
    file_filter = FileFilter(temp_directory)
    txt_files = file_filter.filter_by_extensions(['.txt'])
    
    # Should find both .txt and .TXT
    assert len(txt_files) == 3


def test_get_unique_extensions(temp_directory):
    """Test getting unique extensions"""
    file_filter = FileFilter(temp_directory)
    extensions = file_filter.get_unique_extensions()
    
    # Should have .txt, .jpg, .png, .csv
    assert '.txt' in extensions
    assert '.jpg' in extensions
    assert '.png' in extensions
    assert '.csv' in extensions
    assert len(extensions) == 4


def test_get_extension_counts(temp_directory):
    """Test getting extension counts"""
    file_filter = FileFilter(temp_directory)
    counts = file_filter.get_extension_counts()
    
    assert counts['.txt'] == 2
    assert counts['.jpg'] == 1
    assert counts['.png'] == 1
    assert counts['.csv'] == 1
    assert counts.get('(no extension)', 0) == 1


def test_filter_by_size(temp_directory):
    """Test filtering by file size"""
    # Create files of different sizes
    small = temp_directory / "small.txt"
    large = temp_directory / "large.txt"
    
    small.write_text("x" * 100)  # 100 bytes
    large.write_text("x" * 10000)  # 10000 bytes
    
    file_filter = FileFilter(temp_directory)
    
    # Filter for files larger than 1000 bytes
    large_files = file_filter.filter_by_size(min_size=1000)
    assert len(large_files) == 1
    assert large_files[0].name == "large.txt"
    
    # Filter for files smaller than 1000 bytes
    small_files = file_filter.filter_by_size(max_size=1000)
    assert len(small_files) >= 7  # All other files + small.txt


def test_parse_extensions_string():
    """Test parsing extension string"""
    # Test with dots
    result = parse_extensions_string(".txt,.pdf,.jpg")
    assert result == ['.txt', '.pdf', '.jpg']
    
    # Test without dots
    result = parse_extensions_string("txt,pdf,jpg")
    assert result == ['txt', 'pdf', 'jpg']
    
    # Test with spaces
    result = parse_extensions_string(" .txt , .pdf , .jpg ")
    assert result == ['.txt', '.pdf', '.jpg']
    
    # Test empty string
    result = parse_extensions_string("")
    assert result == []
    
    # Test with mixed format
    result = parse_extensions_string(".txt,pdf, .jpg")
    assert result == ['.txt', 'pdf', '.jpg']


def test_empty_directory(tmp_path):
    """Test filtering in empty directory"""
    file_filter = FileFilter(tmp_path)
    files = file_filter.get_all_files()
    
    assert len(files) == 0


def test_recursive_search(tmp_path):
    """Test recursive file search"""
    # Create subdirectories with files
    subdir1 = tmp_path / "subdir1"
    subdir2 = tmp_path / "subdir2"
    subdir1.mkdir()
    subdir2.mkdir()
    
    (tmp_path / "root.txt").write_text("Root")
    (subdir1 / "sub1.txt").write_text("Sub1")
    (subdir2 / "sub2.txt").write_text("Sub2")
    
    file_filter = FileFilter(tmp_path)
    
    # Non-recursive should find only root file
    files = file_filter.get_all_files(recursive=False)
    assert len(files) == 1
    
    # Recursive should find all files
    files = file_filter.get_all_files(recursive=True)
    assert len(files) == 3



