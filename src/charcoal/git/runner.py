"""Git command execution infrastructure.

This module provides functions for executing git commands via subprocess,
with proper error handling and output capture. It implements the synchronous
GitRunner pattern with subprocess.run().

The runner supports:
- Synchronous command execution with captured output
- Error handling with CommandFailedError and CommandKilledError
- Configurable error behavior (throw or ignore)
- Output trimming control
- Large buffer sizes for git output (1GB)
- Future integration point for tracing (via resource parameter)
"""

import subprocess
from typing import Any, Literal

from charcoal.errors import CommandFailedError, CommandKilledError


def run_git_command_and_split_lines(
    args: list[str],
    *,
    options: dict[str, Any] | None = None,
    on_error: Literal["throw", "ignore"] = "throw",
    resource: str | None = None,
) -> list[str]:
    """Execute a git command and return output as a list of non-empty lines.

    Args:
        args: Git command arguments (without 'git' prefix).
        options: Optional subprocess options, including 'no_trim' boolean.
        on_error: Error handling behavior - 'throw' or 'ignore'.
        resource: Optional resource name for tracing (not yet implemented).

    Returns:
        List of non-empty lines from command output.

    Raises:
        CommandFailedError: If command fails and on_error is 'throw'.
        CommandKilledError: If command is killed by a signal.
    """
    output = run_git_command(args=args, options=options, on_error=on_error, resource=resource)
    return [line for line in output.split("\n") if len(line) > 0]


def run_git_command(
    args: list[str],
    *,
    options: dict[str, Any] | None = None,
    on_error: Literal["throw", "ignore"] = "throw",
    resource: str | None = None,
) -> str:
    """Execute a git command and return its output.

    This function uses subprocess.run() to execute git commands synchronously.
    It captures stdout and stderr, handles exit codes, and provides options
    for error handling and output trimming.

    The resource parameter is reserved for future tracing integration and is
    currently not used.

    Args:
        args: Git command arguments (without 'git' prefix).
        options: Optional subprocess options. Supported keys:
            - 'no_trim': If True, don't trim whitespace from output.
            - 'cwd': Working directory for the command.
            - 'env': Environment variables for the command.
        on_error: Error handling behavior:
            - 'throw': Raise exception on command failure (default).
            - 'ignore': Return empty string on command failure.
        resource: Optional resource name for tracing (reserved for future use).

    Returns:
        Command output as a string (trimmed by default unless no_trim is True).

    Raises:
        CommandFailedError: If command fails and on_error is 'throw'.
        CommandKilledError: If command is killed by a signal.
        OSError: If git command cannot be executed (system error).

    Example:
        >>> run_git_command(['--version'])
        'git version 2.39.1'
        >>> run_git_command(['status', '--short'], options={'cwd': '/path/to/repo'})
        ' M file.txt'
    """
    # TODO: Add tracing integration when tracer module is available
    # For now, resource parameter is accepted but not used
    return _run_git_command_internal(args=args, options=options, on_error=on_error)


def _run_git_command_internal(
    args: list[str],
    *,
    options: dict[str, Any] | None = None,
    on_error: Literal["throw", "ignore"] = "throw",
) -> str:
    """Internal implementation of git command execution.

    Args:
        args: Git command arguments (without 'git' prefix).
        options: Optional subprocess options.
        on_error: Error handling behavior - 'throw' or 'ignore'.

    Returns:
        Command output as a string.

    Raises:
        CommandFailedError: If command fails and on_error is 'throw'.
        CommandKilledError: If command is killed by a signal.
        OSError: If git command cannot be executed.
    """
    options = options or {}
    no_trim = options.get("no_trim", False)

    # Build subprocess kwargs
    subprocess_kwargs: dict[str, Any] = {
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
    }

    # Add cwd if provided
    if "cwd" in options:
        subprocess_kwargs["cwd"] = options["cwd"]

    # Add env if provided
    if "env" in options:
        subprocess_kwargs["env"] = options["env"]

    try:
        # Execute git command with 1GB buffer (effectively unlimited for git operations)
        # Note: Python's subprocess doesn't have a maxBuffer equivalent like Node.js,
        # but text mode handles output buffering automatically for reasonable sizes
        result = subprocess.run(
            ["git"] + args,
            **subprocess_kwargs,
            check=False,  # We handle returncode manually
        )
    except OSError as e:
        # This is a syscall failure (e.g., git not found), not a command failure
        raise e

    # Check if process was killed by a signal (negative returncode in Unix)
    # Note: In Python, signals are represented as negative returncodes
    if result.returncode < 0:
        signal_name = f"SIG{abs(result.returncode)}"
        raise CommandKilledError(
            command="git",
            args=args,
            signal=signal_name,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    # Command succeeded
    if result.returncode == 0:
        if no_trim:
            return result.stdout or ""
        return (result.stdout or "").strip()

    # Command failed but we ignore it
    if on_error == "ignore":
        return ""

    # Command failed and we should throw
    raise CommandFailedError(
        command="git",
        args=args,
        status=result.returncode,
        stdout=result.stdout or "",
        stderr=result.stderr or "",
    )
