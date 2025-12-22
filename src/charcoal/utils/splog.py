"""Logging and output utilities for the CLI.

This module provides the splog (special log) interface for consistent
CLI output, matching the TypeScript implementation. It supports different
output types (info, debug, error, warn, tip, page) with color formatting,
pagination, and quiet/debug modes.

Design Decision #5 - Logging and Output System Design:
-------------------------------------------------------
This implementation uses a custom splog class that closely mirrors the
TypeScript behavior, rather than using Python's standard logging module.
This approach was chosen because:

1. It maintains exact behavioral parity with the TypeScript CLI's splog utility
2. It provides simple, direct output control (quiet mode, debug mode, tips)
3. It uses Click's echo utilities combined with custom ANSI color codes
4. The output format exactly matches the TypeScript version for consistency

The Splog class is instantiated via compose_splog() factory function with
configuration options (quiet, output_debug_logs, tips, pager) that match
the TypeScript interface. This ensures that any command using splog will
produce output identical to the TypeScript CLI.
"""

import os
import subprocess
from datetime import datetime
from typing import Protocol

from charcoal.utils.colors import bold, cyan, dim, gray, italic, red, yellow


class TSplog(Protocol):
    """Protocol defining the splog interface."""

    def newline(self) -> None:
        """Print a blank line."""
        ...

    def info(self, msg: str) -> None:
        """Print an informational message."""
        ...

    def debug(self, msg: str) -> None:
        """Print a debug message (only if debug mode is enabled)."""
        ...

    def error(self, msg: str) -> None:
        """Print an error message in red."""
        ...

    def warn(self, msg: str) -> None:
        """Print a warning message in yellow."""
        ...

    def message(self, msg: str) -> None:
        """Print a yellow message with extra spacing."""
        ...

    def tip(self, msg: str) -> None:
        """Print a tip message (only if tips are enabled)."""
        ...

    def page(self, msg: str) -> None:
        """Send output through a pager if configured, or print directly."""
        ...


class Splog:
    """Implementation of the splog interface.

    This class provides formatted logging output for the CLI, with support
    for quiet mode, debug mode, tips, and pagination.
    """

    def __init__(
        self,
        quiet: bool = False,
        output_debug_logs: bool = False,
        tips: bool = False,
        pager: str | None = None,
    ) -> None:
        """Initialize the splog instance.

        Args:
            quiet: If True, suppress non-error output
            output_debug_logs: If True, show debug messages with timestamps
            tips: If True, show tip messages
            pager: Command to use for pagination (e.g., 'less')
        """
        self.quiet = quiet
        self.output_debug_logs = output_debug_logs
        self.tips = tips
        self.pager = pager

    def newline(self) -> None:
        """Print a blank line."""
        if not self.quiet:
            print()

    def info(self, msg: str) -> None:
        """Print an informational message."""
        if not self.quiet:
            print(msg)

    def debug(self, msg: str) -> None:
        """Print a debug message with timestamp if debug mode is enabled."""
        if self.output_debug_logs:
            timestamp = datetime.now().isoformat()
            formatted = dim(f"{bold(f'{timestamp}:')} {msg}")
            print(formatted)

    def error(self, msg: str) -> None:
        """Print an error message in red."""
        print(red(f"ERROR: {msg}"))

    def warn(self, msg: str) -> None:
        """Print a warning message in yellow."""
        print(yellow(f"WARNING: {msg}"))

    def message(self, msg: str) -> None:
        """Print a yellow message with extra spacing."""
        print(f"{yellow(msg)}\n\n")

    def tip(self, msg: str) -> None:
        """Print a tip message if tips are enabled.

        Tips are formatted in gray with a bold 'tip:' prefix and include
        a reminder about how to disable tips.
        """
        if self.tips and not self.quiet:
            lines = [
                "",
                f"{bold('tip')}: {msg}",
                italic("Feeling expert? `gt user tips --disable`"),
                "",
            ]
            print(gray("\n".join(lines)))

    def page(self, msg: str) -> None:
        """Send output through a pager if configured, otherwise print directly.

        If a pager is configured, attempts to pipe the output through it.
        Falls back to direct printing if the pager fails or is not configured.

        Handles EPIPE errors gracefully when the user quits the pager early.
        """
        if not self.pager:
            print(msg)
            return

        try:
            # Match git's pager environment variables
            # https://github.com/git/git/blob/master/Documentation/config/core.txt#L550
            env = {
                "LESS": "FRX",
                "LV": "-c",
                **os.environ,
            }

            subprocess.run(
                self.pager,
                input=msg.encode("utf-8"),
                shell=True,
                env=env,
                capture_output=False,
                stdin=subprocess.PIPE,
                stdout=None,
                stderr=None,
            )

            # Non-zero exit codes are OK - they often happen when user quits pager early
            # We silently accept them as this is expected behavior

        except BrokenPipeError:
            # EPIPE/BrokenPipeError happens when user quits pager early - this is OK
            # Silently ignore it as it's expected behavior
            pass

        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
            # If pager fails for real reasons, print directly and show a warning
            print(msg)
            print(
                yellow(
                    f"NOTE: Tried to send output to your pager ({cyan(self.pager)}) "
                    f"but encountered an error.\n"
                    f"You can change your configured pager or disable paging: "
                    f"{cyan('gt user pager --help')}"
                )
            )
            # Re-raise as a more specific error that can be caught by the runner
            from charcoal.lib.errors import CommandFailedError

            raise CommandFailedError(
                command=self.pager, message=str(e), returncode=getattr(e, "returncode", 1)
            ) from e


def compose_splog(
    quiet: bool = False,
    output_debug_logs: bool = False,
    tips: bool = False,
    pager: str | None = None,
) -> Splog:
    """Create a configured splog instance.

    This function matches the TypeScript composeSplog interface and provides
    a convenient way to create a logger with specific options.

    Args:
        quiet: If True, suppress non-error output
        output_debug_logs: If True, show debug messages with timestamps
        tips: If True, show tip messages
        pager: Command to use for pagination (e.g., 'less')

    Returns:
        A configured Splog instance
    """
    return Splog(
        quiet=quiet,
        output_debug_logs=output_debug_logs,
        tips=tips,
        pager=pager,
    )


# Create a default global splog instance for convenience
# This can be reconfigured by calling compose_splog() with different options
_default_splog: Splog | None = None


def get_default_splog() -> Splog:
    """Get the default global splog instance.

    Returns:
        The default Splog instance (creates one if it doesn't exist)
    """
    global _default_splog
    if _default_splog is None:
        _default_splog = compose_splog()
    return _default_splog


def set_default_splog(splog: Splog) -> None:
    """Set the default global splog instance.

    Args:
        splog: The Splog instance to use as the default
    """
    global _default_splog
    _default_splog = splog


# Convenience functions that use the default splog instance
def newline() -> None:
    """Print a blank line using the default splog."""
    get_default_splog().newline()


def info(msg: str) -> None:
    """Print an informational message using the default splog."""
    get_default_splog().info(msg)


def debug(msg: str) -> None:
    """Print a debug message using the default splog."""
    get_default_splog().debug(msg)


def error(msg: str) -> None:
    """Print an error message using the default splog."""
    get_default_splog().error(msg)


def warn(msg: str) -> None:
    """Print a warning message using the default splog."""
    get_default_splog().warn(msg)


def message(msg: str) -> None:
    """Print a message using the default splog."""
    get_default_splog().message(msg)


def tip(msg: str) -> None:
    """Print a tip message using the default splog."""
    get_default_splog().tip(msg)


def page(msg: str) -> None:
    """Send output through a pager using the default splog."""
    get_default_splog().page(msg)
