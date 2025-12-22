"""Git preconditions and validation functions.

DEPRECATED: This module is maintained for backwards compatibility only.
New code should import from charcoal.lib.preconditions instead.
"""

# Re-export from new location for backwards compatibility
from charcoal.lib.preconditions import (  # noqa: F401
    current_git_repo_precondition,
    ensure_some_staged_changes_precondition,
    get_repo_root_path,
    get_repo_root_path_precondition,
    uncommitted_tracked_changes_precondition,
)

__all__ = [
    "get_repo_root_path_precondition",
    "current_git_repo_precondition",
    "uncommitted_tracked_changes_precondition",
    "ensure_some_staged_changes_precondition",
    "get_repo_root_path",
]
