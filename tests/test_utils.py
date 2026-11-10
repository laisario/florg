"""Tests for the utils module"""

import pytest
from pathlib import Path
from organize.utils import sanitize_filename
from organize.renamer import FileRenamer


def test_sanitize_preserves_leading_dot():
    """Dotfiles must keep their leading dot (stripping it un-hides them)"""
    assert sanitize_filename(".gitignore") == ".gitignore"
    assert sanitize_filename(".env") == ".env"


def test_sanitize_strips_trailing_dots_and_spaces():
    """Trailing dots/spaces stay stripped (unsafe on Windows filesystems)"""
    assert sanitize_filename("report. ") == "report"
    assert sanitize_filename("notes...") == "notes"


def test_rename_alphabetical_preserves_dotfile(tmp_path):
    """A no-op alphabetical rename must not rename a dotfile"""
    dotfile = tmp_path / ".gitignore"
    dotfile.write_text("node_modules\n")

    renamer = FileRenamer([dotfile])
    changes = renamer.rename_alphabetical(prefix="", suffix="")

    assert len(changes) == 1
    assert changes[0]['new_name'] == ".gitignore"
    assert changes[0]['new_path'] == dotfile
