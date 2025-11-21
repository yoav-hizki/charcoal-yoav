"""Logging utilities for Charcoal CLI.

This module provides the Splog interface, matching the TypeScript implementation
from apps/cli/src/lib/utils/splog.ts. It uses the rich library for colored output
and supports quiet mode, debug mode, tips, and paging functionality.
"""

import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Protocol

from rich.console import Console


class Splog(Protocol):
    """Protocol defining the Splog interface.

    This matches the TSplog type from the TypeScript implementation.
    """

    def newline(self) -> None:
        """Print a blank line."""
        ...

    def info(self, msg: str) -> None:
        """Print an info message."""
        ...

    def debug(self, msg: str) -> None:
        """Print a debug message with timestamp."""
        ...

    def error(self, msg: str) -> None:
        """Print an error message in red."""
        ...

    def warn(self, msg: str) -> None:
        """Print a warning message in yellow."""
        ...

    def message(self, msg: str) -> None:
        """Print a message in yellow with extra newlines."""
        ...

    def tip(self, msg: str) -> None:
        """Print a tip message in gray."""
        ...

    def page(self, msg: str) -> None:
        """Send output through a pager or print directly."""
        ...


class SplogImpl:
    """Implementation of the Splog interface.

    This class provides logging functionality with support for:
    - Quiet mode (suppresses most output)
    - Debug mode (shows timestamped debug messages)
    - Tips (shows helpful tips to users)
    - Paging (sends output through an external pager like less)
    """

    def __init__(
        self,
        quiet: bool = False,
        output_debug_logs: bool = False,
        tips: bool = True,
        pager: str | None = None,
    ):
        """Initialize Splog with configuration options.

        Args:
            quiet: If True, suppress info and newline output
            output_debug_logs: If True, enable debug logging with timestamps
            tips: If True, show tips to the user
            pager: Command to use for paging output (e.g., "less")
        """
        self.quiet = quiet
        self.output_debug_logs = output_debug_logs
        self.tips = tips
        self.pager = pager
        self.console = Console(file=sys.stdout, highlight=False)

    def newline(self) -> None:
        """Print a blank line (suppressed in quiet mode)."""
        if not self.quiet:
            print()

    def info(self, msg: str) -> None:
        """Print an info message (suppressed in quiet mode)."""
        if not self.quiet:
            print(msg)

    def debug(self, msg: str) -> None:
        """Print a debug message with timestamp (only if debug enabled)."""
        if self.output_debug_logs:
            timestamp = datetime.now(timezone.utc).isoformat()
            # Use rich to print dimmed text with bold timestamp
            self.console.print(f"[bold]{timestamp}:[/bold] {msg}", style="dim")

    def error(self, msg: str) -> None:
        """Print an error message in red."""
        self.console.print(f"ERROR: {msg}", style="bright_red")

    def warn(self, msg: str) -> None:
        """Print a warning message in yellow."""
        self.console.print(f"WARNING: {msg}", style="yellow")

    def message(self, msg: str) -> None:
        """Print a message in yellow with extra newlines."""
        self.console.print(f"{msg}\n\n", style="yellow")

    def tip(self, msg: str) -> None:
        """Print a tip message in gray (if tips enabled and not quiet)."""
        if self.tips and not self.quiet:
            tip_text = [
                "",
                f"[bold]tip[/bold]: {msg}",
                "[italic]Feeling expert? `gt user tips --disable`[/italic]",
                "",
            ]
            self.console.print("\n".join(tip_text), style="dim")

    def page(self, msg: str) -> None:
        """Send output through a pager or print directly.

        If a pager is configured, attempts to pipe the message through it.
        Falls back to regular printing if the pager fails or is not configured.

        Args:
            msg: The message to display
        """
        if not self.pager:
            print(msg)
            return

        try:
            # Set up environment variables for pager, matching git's behavior
            env = os.environ.copy()
            env["LESS"] = "FRX"
            env["LV"] = "-c"

            # Run the pager command
            result = subprocess.run(
                self.pager,
                input=msg,
                text=True,
                shell=True,
                env=env,
                check=False,
                capture_output=False,
                stdin=subprocess.PIPE,
            )

            # Handle non-zero exit codes (but allow SIGPIPE/141 which is normal)
            if result.returncode != 0 and result.returncode != 141:
                # Print the message directly as fallback
                print(msg)
                self.console.print(
                    f"\nNOTE: Tried to send output to your pager ([cyan]{self.pager}[/cyan]) "
                    f"but encountered an error.\n"
                    f"You can change your configured pager or disable paging: "
                    f"[cyan]gt user pager --help[/cyan]",
                    style="yellow",
                )
                # Import here to avoid circular dependency
                from charcoal.errors import CommandFailedError

                raise CommandFailedError(
                    command=self.pager,
                    returncode=result.returncode,
                    message=f"Pager command failed with exit code {result.returncode}",
                )

        except FileNotFoundError:
            # Pager command not found
            print(msg)
            self.console.print(
                f"\nNOTE: Pager command not found: [cyan]{self.pager}[/cyan]",
                style="yellow",
            )


def compose_splog(
    quiet: bool = False,
    output_debug_logs: bool = False,
    tips: bool = True,
    pager: str | None = None,
) -> Splog:
    """Create a Splog instance with the specified configuration.

    This is the Python equivalent of the TypeScript composeSplog function.

    Args:
        quiet: If True, suppress info and newline output
        output_debug_logs: If True, enable debug logging with timestamps
        tips: If True, show tips to the user
        pager: Command to use for paging output (e.g., "less")

    Returns:
        A Splog instance configured with the provided options

    Example:
        >>> splog = compose_splog(quiet=False, output_debug_logs=True)
        >>> splog.info("Starting operation...")
        >>> splog.debug("Debug information here")
        >>> splog.error("Something went wrong!")
    """
    return SplogImpl(
        quiet=quiet,
        output_debug_logs=output_debug_logs,
        tips=tips,
        pager=pager,
    )
