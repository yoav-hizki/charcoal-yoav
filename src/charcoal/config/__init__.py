"""Configuration management for Charcoal.

This module provides Pydantic-based configuration models for:
- RepoConfig: Repository-specific settings (trunk, remote, GitHub info)
- UserConfig: User preferences (editor, pager, branch naming, API servers)
- ContinueConfig: Continuation state for interrupted rebase operations

Each config type supports:
- Loading from JSON files with validation
- Saving with secure file permissions (0o600)
- Path resolution relative to USER_HOME or REPO root
- Helper methods for common operations
"""

from charcoal.config.continuation import ContinueConfig, ContinueConfigInstance
from charcoal.config.repo_config import (
    RepoConfig,
    RepoConfigInstance,
    get_owner_and_name_from_url,
    infer_repo_github_info,
)
from charcoal.config.user_config import (
    AlternativeProfile,
    GtiConfig,
    UserConfig,
    UserConfigInstance,
)

__all__ = [
    # RepoConfig exports
    "RepoConfig",
    "RepoConfigInstance",
    "get_owner_and_name_from_url",
    "infer_repo_github_info",
    # UserConfig exports
    "UserConfig",
    "UserConfigInstance",
    "AlternativeProfile",
    "GtiConfig",
    # ContinueConfig exports
    "ContinueConfig",
    "ContinueConfigInstance",
]
