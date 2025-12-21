"""Configuration system for Charcoal CLI.

This module provides user and repository configuration with Pydantic models,
file I/O, and helper functions.
"""

from charcoal.config.repo_config import (
    RepoConfig,
    RepoConfigHelpers,
    get_owner_and_name_from_url,
    repo_config_factory,
)
from charcoal.config.spiffy import SpiffyFactory, SpiffyInstance, spiffy
from charcoal.config.user_config import (
    GtiConfig,
    Profile,
    UserConfig,
    UserConfigHelpers,
    user_config_factory,
)

__all__ = [
    # Spiffy base
    "spiffy",
    "SpiffyFactory",
    "SpiffyInstance",
    # User config
    "UserConfig",
    "UserConfigHelpers",
    "GtiConfig",
    "Profile",
    "user_config_factory",
    # Repo config
    "RepoConfig",
    "RepoConfigHelpers",
    "repo_config_factory",
    "get_owner_and_name_from_url",
]
