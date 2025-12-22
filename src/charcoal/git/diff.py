"""Git diff utilities for detecting and displaying changes."""

from charcoal.git.runner import run_git_command


def detect_staged_changes() -> bool:
    """Check if there are any staged changes ready to be committed.

    Returns:
        True if there are staged changes, False otherwise
    """
    output = run_git_command(
        args=["--no-pager", "diff", "--no-ext-diff", "--shortstat", "--cached"],
        on_error="throw",
        resource="detectStagedChanges",
    )
    return len(output) > 0


def get_unstaged_changes() -> str:
    """Get a stat summary of unstaged changes with color.

    Returns:
        Formatted diff stat output
    """
    return run_git_command(
        args=[
            "-c",
            "color.ui=always",
            "--no-pager",
            "diff",
            "--no-ext-diff",
            "--stat",
        ],
        on_error="throw",
        resource="getUnstagedChanges",
    )


def show_diff(left: str, right: str) -> str:
    """Show colored diff between two commits/refs.

    Args:
        left: Left side of the diff (commit/ref)
        right: Right side of the diff (commit/ref)

    Returns:
        Colored diff output
    """
    return run_git_command(
        args=[
            "-c",
            "color.ui=always",
            "--no-pager",
            "diff",
            "--no-ext-diff",
            left,
            right,
            "--",
        ],
        on_error="throw",
        resource="showDiff",
    )


def is_diff_empty(left: str, right: str) -> bool:
    """Check if the diff between two commits/refs is empty.

    Args:
        left: Left side of the diff (commit/ref)
        right: Right side of the diff (commit/ref)

    Returns:
        True if there are no differences, False otherwise
    """
    output = run_git_command(
        args=[
            "--no-pager",
            "diff",
            "--no-ext-diff",
            "--shortstat",
            left,
            right,
            "--",
        ],
        on_error="throw",
        resource="isDiffEmpty",
    )
    return len(output) == 0


def get_diff(left: str, right: str | None = None) -> str:
    """Get unified diff output without prefix.

    Args:
        left: Left side of the diff (commit/ref)
        right: Optional right side of the diff (defaults to working tree)

    Returns:
        Unified diff output
    """
    args = ["diff", left]
    if right:
        args.append(right)
    args.extend(["--no-prefix", "--unified"])

    return run_git_command(
        args=args,
        on_error="throw",
        resource="getDiff",
    )
