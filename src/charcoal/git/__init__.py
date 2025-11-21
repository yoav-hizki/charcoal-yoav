"""Git operations module.

This module provides infrastructure for executing git commands and handling
git-related operations.
"""

from charcoal.git.runner import run_git_command, run_git_command_and_split_lines

__all__ = [
    "run_git_command",
    "run_git_command_and_split_lines",
]
