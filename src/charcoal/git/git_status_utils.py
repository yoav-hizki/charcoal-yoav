"""Git status checking utilities.

This module provides utilities for checking the status of the working tree,
including detecting unstaged and uncommitted changes.
"""

from charcoal.git.runner import run_git_command


def _do_changes_exist(args: list[str]) -> bool:
    """Check if git command returns any output (indicating changes exist).

    Args:
        args: Git command arguments

    Returns:
        True if there are changes, False otherwise
    """
    output = run_git_command(args=args, on_error="throw", resource="doChangesExist")
    return len(output) > 0


def unstaged_changes() -> bool:
    """Check if there are any untracked files in the working directory.

    Returns:
        True if there are untracked files, False otherwise
    """
    # List untracked files only
    return _do_changes_exist(["ls-files", "--others", "--exclude-standard"])


def tracked_uncommitted_changes() -> bool:
    """Check if there are any tracked uncommitted changes.

    This includes both staged and unstaged changes to tracked files.

    Returns:
        True if there are tracked uncommitted changes, False otherwise
    """
    # Check for tracked changes (staged or unstaged) but not untracked files
    return _do_changes_exist(["status", "-uno", "--porcelain=v1"])
