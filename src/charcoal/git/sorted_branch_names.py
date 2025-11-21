"""Git branch listing and revision operations.

This module provides functions for listing git branches along with their
revision SHAs, sorted by commit date.
"""

from charcoal.git.runner import run_git_command_and_split_lines


def get_branch_names_and_revisions() -> dict[str, str]:
    """Get all local branches with their revision SHAs.

    Returns a dictionary mapping branch names to their commit SHAs,
    sorted by committer date (most recent first).

    Returns:
        Dictionary mapping branch names to their commit SHAs.
        Empty dictionary if not in a git repository or if there are no branches.

    Example:
        >>> get_branch_names_and_revisions()
        {'main': 'abc123...', 'feature-branch': 'def456...'}
    """
    branches: dict[str, str] = {}

    lines = run_git_command_and_split_lines(
        args=[
            "for-each-ref",
            "--format=%(refname:short):%(objectname)",
            "--sort=-committerdate",
            "refs/heads/",
        ],
        on_error="throw",
        resource="getBranchNamesAndRevisions",
    )

    for line in lines:
        parts = line.split(":", 1)
        # Only process lines that have exactly 2 non-empty parts
        if len(parts) == 2 and parts[0] and parts[1]:
            branch_name, sha = parts
            branches[branch_name] = sha

    return branches
