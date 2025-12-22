"""Git command runner with error handling.

This module provides utilities for running git commands with proper error
handling and output capturing, matching the TypeScript implementation.
"""

import subprocess
from typing import Literal

from charcoal.lib.errors import CommandFailedError


def run_git_command(
    args: list[str],
    on_error: Literal["throw", "ignore"] = "throw",
    resource: str | None = None,
    no_trim: bool = False,
    cwd: str | None = None,
) -> str:
    """Run a git command synchronously.

    Args:
        args: List of git command arguments (e.g., ['status', '--porcelain'])
        on_error: Whether to throw an exception or return empty string on error
        resource: Optional resource name for tracing (currently unused)
        no_trim: If True, don't strip whitespace from output
        cwd: Optional working directory for the command

    Returns:
        Command output as a string (trimmed by default)

    Raises:
        CommandFailedError: If the command fails and on_error is 'throw'
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
            # 1GB max buffer to match TypeScript implementation
            timeout=None,
        )

        output = result.stdout
        if not no_trim:
            output = output.strip()

        return output

    except subprocess.CalledProcessError as e:
        if on_error == "ignore":
            return ""

        # Format error message similar to TypeScript implementation
        error_msg_parts = [
            f"Command failed with exit code {e.returncode}:",
            " ".join(["git"] + args),
        ]
        if e.stdout:
            error_msg_parts.append(e.stdout)
        if e.stderr:
            error_msg_parts.append(e.stderr)

        raise CommandFailedError(
            command="git " + " ".join(args),
            message="\n".join(error_msg_parts),
            returncode=e.returncode,
        ) from e

    except FileNotFoundError as e:
        # Git executable not found
        if on_error == "ignore":
            return ""

        raise CommandFailedError(
            command="git",
            message="Git executable not found. Please ensure git is installed and in PATH.",
            returncode=127,
        ) from e


def run_git_command_and_split_lines(
    args: list[str],
    on_error: Literal["throw", "ignore"] = "throw",
    resource: str | None = None,
    cwd: str | None = None,
) -> list[str]:
    """Run a git command and split the output into non-empty lines.

    Args:
        args: List of git command arguments
        on_error: Whether to throw an exception or return empty list on error
        resource: Optional resource name for tracing
        cwd: Optional working directory for the command

    Returns:
        List of non-empty output lines
    """
    output = run_git_command(args=args, on_error=on_error, resource=resource, cwd=cwd)
    return [line for line in output.split("\n") if line]
