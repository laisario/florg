
import sys
from pathlib import Path
from typing import List, Optional
import click
import questionary
from questionary import Choice

from organize.filters import FileFilter, parse_extensions_string
from organize.renamer import FileRenamer
from organize.grouper import FileGrouper, apply_renaming_to_groups
from organize.preview import (
    display_rename_preview,
    display_group_preview,
    display_combined_preview,
    display_undo_preview,
    display_success,
    display_error,
    display_warning,
    display_info,
    display_extension_filter_prompt,
    confirm_changes,
    console
)
from organize.history import (
    save_operation,
    load_last_operation,
    revert_operation
)
from organize.utils import safe_move


@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--group', is_flag=True, help='Enable grouping mode')
@click.option('--undo', is_flag=True, help='Revert last operation')
@click.option('--no-preview', is_flag=True, help='Skip preview confirmation')
@click.option('--extensions', '-e', help='Filter by extensions (comma-separated, e.g., .txt,.pdf)')
def organize(directory: str, group: bool, undo: bool, no_preview: bool, extensions: Optional[str]):
    """
    Organize and rename files in a directory.
    
    DIRECTORY: Path to the directory to organize
    """
    directory_path = Path(directory).resolve()
    
    if undo:
        handle_undo(directory_path)
        return
    
    console.print("\n[bold cyan]════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]  florg - File Organizer By Command Line[/bold cyan]")
    console.print("[bold cyan]  by Laisarva[/bold cyan]")
    console.print("[bold cyan]════════════════════════════════════════[/bold cyan]\n")
    
    file_filter = FileFilter(directory_path)
    
    if extensions:
        ext_list = parse_extensions_string(extensions)
        files = file_filter.filter_by_extensions(ext_list)
        display_info(f"Filtering by extensions: {', '.join(ext_list)}")
    else:
        files = file_filter.get_all_files()
        
        if not files:
            display_error("No files found in directory")
            return
        
        ext_counts = file_filter.get_extension_counts()
        if len(ext_counts) > 1:
            display_extension_filter_prompt(ext_counts)
            display_info("Tip: Use --extensions to filter by specific file types (e.g., --extensions .pdf,.txt)")
    
    if not files:
        display_error("No files found matching the criteria")
        return
    
    display_info(f"Found {len(files)} file(s) to organize")
    
    rename_strategy = prompt_rename_strategy()
    
    if not rename_strategy:
        display_warning("Operation cancelled")
        return
    
    renamer = FileRenamer(files)
    rename_changes = get_rename_changes(renamer, rename_strategy)
    
    if not rename_changes:
        display_warning("No changes to apply")
        return
    
    if group:
        grouping_strategy = prompt_grouping_strategy()
        
        if grouping_strategy:
            grouper = FileGrouper(files)
            groups = get_grouping_operations(grouper, grouping_strategy)
            
            if groups:
                groups = apply_renaming_to_groups(groups, rename_changes)
                
                if not no_preview:
                    display_combined_preview(groups)
                    
                    if not confirm_changes():
                        display_warning("Operation cancelled")
                        return
                
                execute_grouped_operations(groups, directory_path)
                return
    
    if not no_preview:
        display_rename_preview(rename_changes)
        
        if not confirm_changes():
            display_warning("Operation cancelled")
            return
    
    execute_rename_operations(rename_changes, directory_path)


def prompt_rename_strategy() -> Optional[str]:
    """
    Prompt user to select renaming strategy.
    
    Returns:
        Selected strategy name or None if cancelled
    """
    choices = [
        Choice(title="Numeric increase (file001, file002, ...)", value="numeric"),
        Choice(title="Alphabetical order", value="alphabetical"),
        Choice(title="Creation date", value="creation_date"),
        Choice(title="Last modification date", value="modification_date"),
        Choice(title="File size", value="size"),
        Choice(title="File type / extension", value="extension"),
        Choice(title="Custom prefix/suffix", value="custom"),
    ]
    
    return questionary.select(
        "How would you like to organize files?",
        choices=choices
    ).ask()


def prompt_grouping_strategy() -> Optional[str]:
    """
    Prompt user to select grouping strategy.
    
    Returns:
        Selected strategy name or None if cancelled
    """
    choices = [
        Choice(title="Same creation date", value="creation_date"),
        Choice(title="Same modification date", value="modification_date"),
        Choice(title="Same size range", value="size_range"),
        Choice(title="Same file type", value="extension"),
    ]
    
    return questionary.select(
        "How would you like to group files?",
        choices=choices
    ).ask()


def get_rename_changes(renamer: FileRenamer, strategy: str) -> List:
    """
    Get rename changes based on selected strategy.
    
    Args:
        renamer: FileRenamer instance
        strategy: Selected strategy name
        
    Returns:
        List of rename operations
    """
    if strategy == "numeric":
        start = questionary.text(
            "Starting number:",
            default="1"
        ).ask()
        
        padding = questionary.text(
            "Number of digits for padding:",
            default="3"
        ).ask()
        
        prefix = questionary.text(
            "Prefix (optional):",
            default=""
        ).ask()
        
        suffix = questionary.text(
            "Suffix (optional):",
            default=""
        ).ask()
        
        return renamer.rename_numeric(
            start=int(start),
            padding=int(padding),
            prefix=prefix,
            suffix=suffix
        )
    
    elif strategy == "alphabetical":
        reverse = questionary.confirm(
            "Reverse order?",
            default=False
        ).ask()
        
        prefix = questionary.text(
            "Prefix (optional):",
            default=""
        ).ask()
        
        suffix = questionary.text(
            "Suffix (optional):",
            default=""
        ).ask()
        
        return renamer.rename_alphabetical(
            reverse=reverse,
            prefix=prefix,
            suffix=suffix
        )
    
    elif strategy == "creation_date":
        date_format = questionary.text(
            "Date format:",
            default="%Y%m%d"
        ).ask()
        
        prefix = questionary.text(
            "Prefix (optional):",
            default=""
        ).ask()
        
        suffix = questionary.text(
            "Suffix (optional):",
            default=""
        ).ask()
        
        return renamer.rename_by_creation_date(
            date_format=date_format,
            prefix=prefix,
            suffix=suffix
        )
    
    elif strategy == "modification_date":
        date_format = questionary.text(
            "Date format:",
            default="%Y%m%d"
        ).ask()
        
        prefix = questionary.text(
            "Prefix (optional):",
            default=""
        ).ask()
        
        suffix = questionary.text(
            "Suffix (optional):",
            default=""
        ).ask()
        
        return renamer.rename_by_modification_date(
            date_format=date_format,
            prefix=prefix,
            suffix=suffix
        )
    
    elif strategy == "size":
        order = questionary.select(
            "Sort order:",
            choices=[
                Choice(title="Ascending (smallest first)", value=True),
                Choice(title="Descending (largest first)", value=False),
            ]
        ).ask()
        
        prefix = questionary.text(
            "Prefix (optional):",
            default=""
        ).ask()
        
        suffix = questionary.text(
            "Suffix (optional):",
            default=""
        ).ask()
        
        return renamer.rename_by_size(
            ascending=order,
            prefix=prefix,
            suffix=suffix
        )
    
    elif strategy == "extension":
        keep_original = questionary.confirm(
            "Keep original filenames?",
            default=True
        ).ask()
        
        prefix = questionary.text(
            "Prefix (optional):",
            default=""
        ).ask()
        
        suffix = questionary.text(
            "Suffix (optional):",
            default=""
        ).ask()
        
        return renamer.rename_by_extension(
            prefix=prefix,
            suffix=suffix,
            keep_original=keep_original
        )
    
    elif strategy == "custom":
        prefix = questionary.text(
            "Prefix:",
            default=""
        ).ask()
        
        suffix = questionary.text(
            "Suffix:",
            default=""
        ).ask()
        
        return renamer.apply_custom_prefix_suffix(
            prefix=prefix,
            suffix=suffix
        )
    
    return []


def get_grouping_operations(grouper: FileGrouper, strategy: str) -> List:
    """
    Get grouping operations based on selected strategy.
    
    Args:
        grouper: FileGrouper instance
        strategy: Selected strategy name
        
    Returns:
        List of grouping operations
    """
    if strategy == "creation_date":
        date_format = questionary.text(
            "Date format for folder names:",
            default="%Y-%m-%d"
        ).ask()
        
        return grouper.group_by_creation_date(date_format=date_format)
    
    elif strategy == "modification_date":
        date_format = questionary.text(
            "Date format for folder names:",
            default="%Y-%m-%d"
        ).ask()
        
        return grouper.group_by_modification_date(date_format=date_format)
    
    elif strategy == "size_range":
        return grouper.group_by_size_range()
    
    elif strategy == "extension":
        return grouper.group_by_extension()
    
    return []


def execute_rename_operations(changes: List, directory: Path) -> None:
    """
    Execute rename operations.
    
    Args:
        changes: List of rename operations
        directory: Directory path for history tracking
    """
    successful = 0
    failed = 0
    
    for change in changes:
        try:
            if safe_move(change['old_path'], change['new_path']):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            console.print(f"[red]Error renaming {change['old_name']}: {e}[/red]")
            failed += 1
    
    if successful > 0:
        save_operation(str(directory), 'rename', changes)
        display_success(f"Successfully renamed {successful} file(s)", successful)
    
    if failed > 0:
        display_warning(f"Failed to rename {failed} file(s)")


def execute_grouped_operations(groups: List, directory: Path) -> None:
    """
    Execute grouped operations (rename + move to folders).
    
    Args:
        groups: List of grouping operations
        directory: Directory path for history tracking
    """
    successful = 0
    failed = 0
    all_changes = []
    
    for group in groups:
        for move in group['moves']:
            try:
                if safe_move(move['old_path'], move['new_path']):
                    successful += 1
                    all_changes.append(move)
                else:
                    failed += 1
            except Exception as e:
                console.print(f"[red]Error moving {move['old_name']}: {e}[/red]")
                failed += 1
    
    if successful > 0:
        save_operation(str(directory), 'group', all_changes)
        display_success(f"Successfully organized {successful} file(s)", successful)
    
    if failed > 0:
        display_warning(f"Failed to organize {failed} file(s)")


def handle_undo(directory: Path) -> None:
    """
    Handle undo operation.
    
    Args:
        directory: Directory to undo operation in
    """
    operation = load_last_operation(str(directory))
    
    if not operation:
        display_warning("No operation found to undo for this directory")
        return
    
    display_undo_preview(operation)
    
    console.print("[bold yellow]Do you want to undo this operation?[/bold yellow]")
    response = console.input("[bold](Y/n):[/bold] ").strip().lower()
    
    if response not in ['', 'y', 'yes']:
        display_warning("Undo cancelled")
        return
    
    if revert_operation(operation):
        changes = operation.get('changes', [])
        display_success(f"Successfully reverted {len(changes)} file(s)", len(changes))
    else:
        display_error("Failed to undo operation")


if __name__ == '__main__':
    organize()


