"""Preview display functionality using Rich library"""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box


console = Console()


def display_rename_preview(changes: List[Dict]) -> None:
    """
    Display preview of file rename operations.
    
    Args:
        changes: List of rename operations with old/new paths
    """
    if not changes:
        console.print("[yellow]No files to rename.[/yellow]")
        return
    
    # Create table
    table = Table(
        title="Rename Preview",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("#", style="dim", width=4)
    table.add_column("Current Name", style="red")
    table.add_column("→", justify="center", width=3)
    table.add_column("New Name", style="green")
    
    # Add rows
    for idx, change in enumerate(changes, 1):
        table.add_row(
            str(idx),
            change['old_name'],
            "→",
            change['new_name']
        )
    
    console.print()
    console.print(table)
    console.print()
    console.print(f"[bold]Total files to rename: {len(changes)}[/bold]")
    console.print()


def display_group_preview(groups: List[Dict]) -> None:
    """
    Display preview of file grouping operations.
    
    Args:
        groups: List of grouping operations with folders and moves
    """
    if not groups:
        console.print("[yellow]No files to group.[/yellow]")
        return
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Grouping Preview[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    total_files = 0
    
    # Create tree for each group
    for group in groups:
        folder_name = group['folder']
        moves = group['moves']
        
        if not moves:
            continue
        
        # Create tree for this folder
        tree = Tree(
            f"[bold blue]📁 {folder_name}/[/bold blue] ([cyan]{len(moves)} files[/cyan])",
            guide_style="dim"
        )
        
        # Add files to tree
        for move in moves[:10]:  # Show first 10 files
            file_icon = "📄"
            tree.add(f"{file_icon} [green]{move['new_name']}[/green]")
        
        # Show "and X more" if there are more files
        if len(moves) > 10:
            tree.add(f"[dim]... and {len(moves) - 10} more files[/dim]")
        
        console.print(tree)
        console.print()
        
        total_files += len(moves)
    
    console.print(f"[bold]Total folders to create: {len(groups)}[/bold]")
    console.print(f"[bold]Total files to organize: {total_files}[/bold]")
    console.print()


def display_combined_preview(groups: List[Dict]) -> None:
    """
    Display preview for combined rename + group operations.
    
    Args:
        groups: List of grouping operations with renamed files
    """
    if not groups:
        console.print("[yellow]No files to organize.[/yellow]")
        return
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Organize Preview (Rename + Group)[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    total_files = 0
    
    for group in groups:
        folder_name = group['folder']
        moves = group['moves']
        
        if not moves:
            continue
        
        # Create table for this group
        table = Table(
            title=f"📁 {folder_name}/",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Current Name", style="red")
        table.add_column("→", justify="center", width=3)
        table.add_column("New Name", style="green")
        table.add_column("New Location", style="blue", overflow="fold")
        
        # Show first 5 files
        for move in moves[:5]:
            table.add_row(
                move['old_name'],
                "→",
                move['new_name'],
                str(move['new_path'].parent)
            )
        
        if len(moves) > 5:
            table.add_row(
                "[dim]...[/dim]",
                "",
                f"[dim]+ {len(moves) - 5} more[/dim]",
                ""
            )
        
        console.print(table)
        console.print()
        
        total_files += len(moves)
    
    console.print(f"[bold]Total folders: {len(groups)} | Total files: {total_files}[/bold]")
    console.print()


def confirm_changes() -> bool:
    """
    Ask user to confirm changes.
    
    Returns:
        True if user confirms, False otherwise
    """
    console.print("[bold yellow]Do you want to proceed with these changes?[/bold yellow]")
    response = console.input("[bold](Y/n):[/bold] ").strip().lower()
    
    return response in ['', 'y', 'yes']


def display_success(message: str, count: int = 0) -> None:
    """
    Display success message.
    
    Args:
        message: Success message
        count: Number of items affected (optional)
    """
    if count > 0:
        full_message = f"{message} ({count} files)"
    else:
        full_message = message
    
    console.print()
    console.print(Panel.fit(
        f"[bold green]✓ {full_message}[/bold green]",
        border_style="green"
    ))
    console.print()


def display_error(message: str, details: str = None) -> None:
    """
    Display error message.
    
    Args:
        message: Error message
        details: Additional error details (optional)
    """
    error_text = f"[bold red]✗ {message}[/bold red]"
    if details:
        error_text += f"\n\n[yellow]{details}[/yellow]"
    
    console.print()
    console.print(Panel.fit(
        error_text,
        border_style="red",
        title="Error"
    ))
    console.print()


def display_warning(message: str) -> None:
    """
    Display warning message.
    
    Args:
        message: Warning message
    """
    console.print()
    console.print(Panel.fit(
        f"[bold yellow]⚠ {message}[/bold yellow]",
        border_style="yellow",
        title="Warning"
    ))
    console.print()


def display_info(message: str) -> None:
    """
    Display informational message.
    
    Args:
        message: Info message
    """
    console.print()
    console.print(f"[bold blue]ℹ {message}[/bold blue]")
    console.print()


def display_undo_preview(operation: Dict) -> None:
    """
    Display preview of undo operation.
    
    Args:
        operation: Operation to be undone
    """
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Undo Preview[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    console.print(f"[bold]Operation Type:[/bold] {operation.get('operation_type', 'unknown')}")
    console.print(f"[bold]Directory:[/bold] {operation.get('directory', 'unknown')}")
    console.print(f"[bold]Timestamp:[/bold] {operation.get('timestamp', 'unknown')}")
    console.print()
    
    changes = operation.get('changes', [])
    
    if not changes:
        console.print("[yellow]No changes to undo.[/yellow]")
        return
    
    # Create table
    table = Table(
        title="Files to Revert",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("#", style="dim", width=4)
    table.add_column("Current Location", style="green")
    table.add_column("→", justify="center", width=3)
    table.add_column("Original Location", style="red")
    
    # Show first 10 changes
    for idx, change in enumerate(changes[:10], 1):
        table.add_row(
            str(idx),
            str(change.get('new', '')),
            "→",
            str(change.get('old', ''))
        )
    
    if len(changes) > 10:
        table.add_row(
            "...",
            f"[dim]+ {len(changes) - 10} more files[/dim]",
            "",
            ""
        )
    
    console.print(table)
    console.print()
    console.print(f"[bold]Total files to revert: {len(changes)}[/bold]")
    console.print()


def display_extension_filter_prompt(extensions: dict) -> None:
    """
    Display available extensions with counts.
    
    Args:
        extensions: Dictionary mapping extensions to file counts
    """
    console.print()
    console.print("[bold cyan]Available file extensions:[/bold cyan]")
    console.print()
    
    for ext, count in sorted(extensions.items()):
        console.print(f"  [green]{ext}[/green]: {count} file(s)")
    
    console.print()


