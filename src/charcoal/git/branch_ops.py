"""Git branch operations.

This module provides functions for common git branch operations including
getting the current branch name and other branch-related functionality.
"""

from charcoal.git.runner import run_git_command


def get_current_branch_name() -> str | None:
    """Get the name of the currently checked out branch.

    Returns:
        The name of the current branch, or None if in detached HEAD state
        or if not in a git repository.

    Example:
        >>> get_current_branch_name()
        'main'
        >>> # In detached HEAD state:
        >>> get_current_branch_name()
        None
    """
    branch_name = run_git_command(
        args=["branch", "--show-current"],
        on_error="ignore",
        resource="getCurrentBranchName",
    )

    return branch_name if len(branch_name) > 0 else None
