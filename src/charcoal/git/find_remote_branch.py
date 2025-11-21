"""Git remote branch discovery.

This module provides functions for finding branches that track a given remote.
"""

from charcoal.git.runner import run_git_command_and_split_lines


def find_remote_branch(remote: str) -> str | None:
    """Find a branch that tracks the specified remote.

    Uses git config to find branches configured to track the given remote.
    For example, if a branch 'main' is configured with 'branch.main.remote origin',
    this function will return 'main' when called with remote='origin'.

    Args:
        remote: The name of the remote to search for (e.g., 'origin').

    Returns:
        The name of the first branch tracking the remote, or None if no such
        branch exists.

    Example:
        >>> find_remote_branch('origin')
        'main'
        >>> find_remote_branch('upstream')
        None
    """
    # Search for git config entries matching pattern: branch.<name>.remote <remote>
    # The regex pattern matches 'remote$' (ends with 'remote') and value '^<remote>$'
    lines = run_git_command_and_split_lines(
        args=["config", "--get-regexp", "remote$", f"^{remote}$"],
        on_error="ignore",
        resource="findRemoteBranch",
    )

    if not lines:
        return None

    # Take the first matching line
    # Format is: branch.<branchName>.remote <remoteName>
    # Extract the branch name from between 'branch.' and '.remote'
    first_line = lines[0]
    parts = first_line.split(".")

    # We expect at least 3 parts: ['branch', '<branchName>', 'remote ...']
    if len(parts) >= 3:
        return parts[1]

    return None
