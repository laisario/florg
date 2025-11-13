# florg - File Organizer by Command line

A powerful CLI tool for batch file renaming and organizing with an intuitive interface, preview mode, and undo capability.

## Features

✨ **Multiple Renaming Strategies:**
- Numeric sequence (file001, file002, ...)
- Alphabetical order
- Creation date
- Last modification date
- File size
- File type/extension
- Custom prefix/suffix

📁 **Smart Grouping:**
- Group by creation date
- Group by modification date
- Group by size range
- Group by file type

🔍 **Preview Mode:**
- See changes before they happen
- Beautiful table display with Rich library
- Confirm before executing

↩️ **Undo Capability:**
- Revert the last operation
- Automatic history tracking
- Per-directory undo support

🎯 **Flexible Filtering:**
- Filter by file extensions
- Interactive extension selection
- Support for multiple extensions

## Installation

### From PyPI (Recommended)

Install florg directly from PyPI using pip:

```bash
pip install florg
```

That's it! The `organize` command will be available immediately.

### From Source

For development or the latest changes:

1. Clone the repository:
```bash
git clone https://github.com/laisario/florg.git
cd florg
```

2. Install in development mode:
```bash
pip install -e .
```

### Dependencies

florg automatically installs these dependencies:
- `click` - CLI framework
- `rich` - Beautiful terminal output
- `questionary` - Interactive prompts

## Usage

### Basic Usage

```bash
organize /path/to/directory
```

This will:
1. Show available files
2. Prompt you to choose an organization method
3. Display a preview of changes
4. Ask for confirmation
5. Execute the operation

### Command Line Options

```bash
organize [OPTIONS] DIRECTORY
```

**Options:**
- `--group` - Enable grouping mode (organize files into folders)
- `--undo` - Revert the last operation in this directory
- `--no-preview` - Skip preview and execute immediately
- `--extensions`, `-e` - Filter by file extensions (comma-separated)

### Examples

#### Basic Rename with Preview (Default)

```bash
organize ~/Documents/photos
```

The tool will interactively guide you through:
1. Choosing a renaming strategy
2. Setting parameters (prefix, suffix, etc.)
3. Showing a preview of all changes
4. Asking for confirmation

#### Rename Specific Extensions

```bash
organize ~/Downloads --extensions .pdf,.docx
```

Only process PDF and Word documents.

#### Skip Preview for Automation

```bash
organize ~/Music --no-preview
```

Execute immediately without confirmation (use with caution!).

#### Group Files into Folders

```bash
organize ~/Documents --group
```

After choosing a rename strategy, you'll be asked how to group files:
- By date (folders like "2025-11-04")
- By size range (folders like "Small (10 KB - 1 MB)")
- By file type (folders like "pdf", "jpg")

#### Combined: Filter and Group

```bash
organize ~/Downloads --group --extensions .jpg,.png,.gif
```

Filter for image files and organize them into folders.

#### Undo Last Operation

```bash
organize ~/Documents --undo
```

Revert the last batch operation performed in this directory.

## Renaming Strategies

### 1. Numeric Increase

Rename files with sequential numbers.

**Prompts:**
- Starting number (default: 1)
- Padding digits (default: 3)
- Prefix (optional)
- Suffix (optional)

**Example output:**
```
file001.txt
file002.txt
file003.txt
```

### 2. Alphabetical Order

Sort and optionally rename files alphabetically.

**Prompts:**
- Reverse order? (Y/n)
- Prefix (optional)
- Suffix (optional)

**Example output:**
```
document_a.txt
document_b.txt
document_c.txt
```

### 3. Creation Date

Rename based on file creation date.

**Prompts:**
- Date format (default: %Y%m%d)
- Prefix (optional)
- Suffix (optional)

**Example output:**
```
20251104_1.jpg
20251104_2.jpg
20251105_1.jpg
```

### 4. Modification Date

Rename based on last modification date.

**Prompts:**
- Date format (default: %Y%m%d)
- Prefix (optional)
- Suffix (optional)

**Example output:**
```
mod_20251104.pdf
mod_20251103.pdf
```

### 5. File Size

Rename files sorted by size.

**Prompts:**
- Sort order (ascending/descending)
- Prefix (optional)
- Suffix (optional)

**Example output:**
```
001_15.2KB.jpg
002_124.5KB.jpg
003_1.2MB.jpg
```

### 6. File Type/Extension

Organize by file type with sequential numbering.

**Prompts:**
- Keep original names? (Y/n)
- Prefix (optional)
- Suffix (optional)

**Example output:**
```
jpg_001.jpg
jpg_002.jpg
pdf_001.pdf
```

### 7. Custom Prefix/Suffix

Simply add prefix and/or suffix to existing names.

**Prompts:**
- Prefix text
- Suffix text

**Example output:**
```
PREFIX_original_name_SUFFIX.txt
```

## Grouping Strategies

### Same Creation Date

Groups files into folders based on creation date.

**Folder names:** `2025-11-04/`, `2025-11-03/`

### Same Modification Date

Groups files into folders based on modification date.

**Folder names:** `2025-11-04/`, `2025-11-03/`

### Same Size Range

Groups files into predefined size categories.

**Folder names:**
- `Tiny (< 10 KB)/`
- `Small (10 KB - 1 MB)/`
- `Medium (1 MB - 10 MB)/`
- `Large (10 MB - 100 MB)/`
- `Huge (> 100 MB)/`

### Same File Type

Groups files by extension.

**Folder names:** `txt/`, `jpg/`, `pdf/`

## Preview Mode

By default, the tool shows a beautiful preview of all changes before executing:

```
┌─────────────── Rename Preview ───────────────┐
│ #   Current Name     →  New Name             │
├─────────────────────────────────────────────┤
│ 1   image.jpg        →  photo_001.jpg        │
│ 2   document.txt     →  photo_002.txt        │
│ 3   file.pdf         →  photo_003.pdf        │
└─────────────────────────────────────────────┘

Total files to rename: 3

Do you want to proceed with these changes? (Y/n):
```

## Undo Feature

Every operation is automatically saved to history. You can undo the last operation:

```bash
organize ~/Documents --undo
```

This will:
1. Load the last operation for that directory
2. Show what will be reverted
3. Ask for confirmation
4. Move all files back to original locations
5. Remove empty folders (for group operations)

**History Location:** `~/.florg_history.json`

## Error Handling

The tool handles various error scenarios:

- ✓ Permission errors - Shows clear error messages
- ✓ Name collisions - Automatically appends (1), (2), etc.
- ✓ Invalid characters - Sanitizes filenames
- ✓ Missing files - Gracefully skips
- ✓ Interrupted operations - Partial operations are tracked

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=organize --cov-report=html
```

## Project Structure

```
florg/
├── organize/
│   ├── __init__.py
│   ├── cli.py          # Main CLI entry point
│   ├── renamer.py      # Renaming strategies
│   ├── grouper.py      # Grouping logic
│   ├── history.py      # Undo functionality
│   ├── preview.py      # Preview display
│   ├── filters.py      # File filtering
│   └── utils.py        # Utility functions
├── tests/
│   ├── test_renamer.py
│   ├── test_grouper.py
│   ├── test_history.py
│   └── test_filters.py
├── setup.py
├── requirements.txt
└── README.md
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/laisario/florg.git
cd florg

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Style

The project uses `black` for code formatting:

```bash
black organize/ tests/
```

## Future Enhancements

Potential features for future versions:

- 🔄 Recursive mode for subdirectories
- 📝 Configuration file support
- 🔍 Regex pattern support
- 📊 Duplicate file detection
- 🏷️ EXIF/metadata-based renaming
- 🌐 Web interface
- 🔌 Plugin system for custom strategies
- 📅 Scheduled/automated organization
- 🌍 Multi-language support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Command not found after installation

Make sure your Python scripts directory is in your PATH:

```bash
# On Linux/Mac
export PATH="$HOME/.local/bin:$PATH"

# On Windows (PowerShell)
$env:Path += ";$HOME\AppData\Local\Programs\Python\Python3X\Scripts"
```

### Permission denied errors

Ensure you have write permissions in the target directory:

```bash
chmod u+w /path/to/directory
```

### Undo not working

Check if the history file exists:

```bash
cat ~/.florg_history.json
```

If corrupted, you can reset it:

```bash
rm ~/.florg_history.json
```

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/laisario/florg/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI handling
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful output
- Interactive prompts powered by [Questionary](https://questionary.readthedocs.io/)

---

Made with ❤️



