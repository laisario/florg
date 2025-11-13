# Quick Start Guide

Get started with florg (File Organizer & Batch Renamer) in 5 minutes!

## Installation

### From PyPI (Recommended)

```bash
pip install florg
```

### From Source (Development)

```bash
git clone https://github.com/laisario/florg.git
cd florg
pip install -e .
```

## Test It Out

### 1. Create a Test Directory

```bash
mkdir ~/test_organize
cd ~/test_organize

# Create some test files
touch file1.txt file2.txt file3.txt
touch image1.jpg image2.jpg
touch document.pdf
```

### 2. Run Your First Organization

```bash
organize ~/test_organize
```

You'll be prompted to:
1. Choose how to organize (try "Numeric increase")
2. Set parameters (accept defaults by pressing Enter)
3. Review the preview
4. Confirm the changes (press Y)

### 3. Try Grouping

```bash
organize ~/test_organize --group
```

This time:
1. Choose a rename strategy
2. Choose a grouping strategy (try "Same file type")
3. Review how files will be organized into folders
4. Confirm

### 4. Undo Your Changes

```bash
organize ~/test_organize --undo
```

This will revert everything back!

## Common Use Cases

### Organize Photos by Date

```bash
# Your vacation photos folder
organize ~/Pictures/vacation --group

# Choose: "Creation date" for renaming
# Choose: "Same creation date" for grouping
```

### Clean Up Downloads

```bash
# Only organize PDFs
organize ~/Downloads --extensions .pdf

# Choose: "Alphabetical order"
```

### Batch Rename Documents

```bash
organize ~/Documents/reports

# Choose: "Numeric increase"
# Set prefix: "Report_"
# Files become: Report_001.pdf, Report_002.pdf, etc.
```

## Command Cheat Sheet

```bash
# Basic usage
organize /path/to/directory

# With extension filter
organize /path/to/directory --extensions .jpg,.png

# With grouping
organize /path/to/directory --group

# Skip preview (auto-accept)
organize /path/to/directory --no-preview

# Undo last operation
organize /path/to/directory --undo

# Combined
organize /path/to/directory --group --extensions .txt,.pdf
```

## Running Tests

For developers who installed from source:

```bash
# Navigate to the project directory
cd florg

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_renamer.py

# Run with coverage
pytest --cov=organize
```

## Tips

1. **Always use preview mode first** - Don't use `--no-preview` until you're confident
2. **Test with copies** - Try the tool on copies of important files first
3. **Undo is your friend** - If something goes wrong, use `--undo` immediately
4. **Extension filters** - Use `-e` to process only specific file types
5. **History is per-directory** - Each directory tracks its own undo history

## What Next?

- Read the full [README.md](README.md) for detailed documentation
- Check out all available [renaming strategies](README.md#renaming-strategies)
- Learn about [grouping options](README.md#grouping-strategies)
- Explore [advanced usage examples](README.md#examples)

## Need Help?

```bash
# Get help
organize --help

# Check version
pip show florg
```

Happy organizing! 🎉



