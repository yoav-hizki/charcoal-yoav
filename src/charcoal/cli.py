"""Main CLI entry point for Charcoal.

This module defines the main Typer application and sets up the command structure.
Commands are organized into subcommands (e.g., 'charcoal repo init', 'charcoal branch create').
"""

import sys

import typer
from rich.console import Console

from charcoal import __version__

# Initialize Typer app with rich markup support
app = typer.Typer(
    name="charcoal",
    help="A command line tool that makes working with stacked changes fast & intuitive.",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Console for rich output
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"charcoal version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    Charcoal CLI - A tool for working with stacked changes.

    Use 'charcoal COMMAND --help' for more information on a specific command.
    """
    pass


# Placeholder commands to demonstrate the subcommand structure
# These will be replaced with actual command implementations in future tasks


@app.command()
def demo() -> None:
    """Demo command to verify CLI installation."""
    console.print("[green]✓[/green] Charcoal CLI is working!")
    console.print("\nThis is a demo command to verify installation.")
    console.print(f"Version: {__version__}")


# Entry point for console_scripts
def cli_entry() -> None:
    """Entry point for the charcoal command."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_entry()
