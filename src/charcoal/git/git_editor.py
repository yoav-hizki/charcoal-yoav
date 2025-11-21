"""Git editor and pager configuration utilities."""

from charcoal.git.runner import run_git_command


def get_git_editor() -> str | None:
    """Get the configured git editor from global config.

    Returns:
        The configured editor, or None if not set.
    """
    editor = run_git_command(
        args=["config", "--global", "core.editor"],
        on_error="ignore",
        resource="getGitEditor",
    )
    return editor if len(editor) > 0 else None


def get_git_pager() -> str | None:
    """Get the configured git pager from global config.

    Returns:
        The configured pager, or None if not set.
    """
    pager = run_git_command(
        args=["config", "--global", "core.pager"],
        on_error="ignore",
        resource="getGitPager",
    )
    return pager if len(pager) > 0 else None
