"""Precondition checks for Charcoal operations.

This module provides functions to validate that necessary preconditions
are met before performing git operations. These checks ensure operations
are only attempted in valid git repositories.
"""

from charcoal.errors import PreconditionsFailedError
from charcoal.git.runner import run_git_command


def get_repo_root_path_precondition() -> str:
    """Get the git repository root path, raising an error if not in a git repo.

    This function uses 'git rev-parse --git-common-dir' to find the .git
    directory location, which works in both normal repositories and worktrees.

    Returns:
        The path to the .git directory (or git common directory for worktrees).

    Raises:
        PreconditionsFailedError: If not currently in a git repository.

    Example:
        >>> get_repo_root_path_precondition()
        '/home/user/my-project/.git'
    """
    repo_root_path = run_git_command(
        args=["rev-parse", "--git-common-dir"],
        on_error="ignore",
        resource="getRepoRootPathPrecondition",
    )

    if not repo_root_path:
        raise PreconditionsFailedError("No .git repository found.")

    return repo_root_path


def current_git_repo_precondition() -> str:
    """Get the git repository working tree root, raising an error if not in a git repo.

    This function uses 'git rev-parse --show-toplevel' to find the root
    directory of the working tree.

    Returns:
        The path to the repository root directory.

    Raises:
        PreconditionsFailedError: If not currently in a git repository.

    Example:
        >>> current_git_repo_precondition()
        '/home/user/my-project'
    """
    repo_root_path = run_git_command(
        args=["rev-parse", "--show-toplevel"],
        on_error="ignore",
        resource="currentGitRepoPrecondition",
    )

    if not repo_root_path:
        raise PreconditionsFailedError("No .git repository found.")

    return repo_root_path
