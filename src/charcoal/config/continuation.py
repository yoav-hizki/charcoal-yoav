"""Continuation/rebase state configuration management.

This module provides the ContinueConfig Pydantic model for persisting state
during interrupted rebase operations. After Charcoal is interrupted by a merge
conflict, this config tracks:

1. The original rebase operation to complete
2. Branches remaining to sync from remote
3. Branches remaining to restack
4. The current branch to restore after completion
5. The new parent branch revision after resolving conflicts
"""

from pathlib import Path

from pydantic import BaseModel

from charcoal.config.base import (
    determine_config_path,
    load_config,
    save_config,
)


class ContinueConfig(BaseModel):
    """Continue/rebase state configuration model.

    This config is used to persist state when a Charcoal operation is interrupted
    by a merge conflict. It tracks what operations remain to be completed after
    the user resolves the conflict and runs 'charcoal continue'.

    Attributes:
        branchesToSync: List of branch names remaining to sync from remote.
        branchesToRestack: List of branch names remaining to restack.
        currentBranchOverride: The branch to switch back to after completion.
        rebasedBranchBase: The new parent branch revision after conflict resolution.
    """

    branchesToSync: list[str] = []
    branchesToRestack: list[str] = []
    currentBranchOverride: str | None = None
    rebasedBranchBase: str | None = None

    # Default location for continue config
    DEFAULT_LOCATIONS: list[tuple[str, str]] = [
        (".gtcontinue", "REPO"),
    ]

    @classmethod
    def load(cls, path_override: str | None = None) -> "ContinueConfigInstance":
        """Load continue config from file or create with defaults.

        This config uses removeIfEmpty and removeIfInvalid options, meaning:
        - If the file is malformed, it will be removed and defaults loaded
        - When saved with empty data, the file will be removed

        Args:
            path_override: Optional explicit path to config file.

        Returns:
            ContinueConfigInstance with loaded data.
        """
        path = determine_config_path(cls.DEFAULT_LOCATIONS, path_override)
        config = load_config(cls, path, remove_if_invalid=True, initialize={})
        return ContinueConfigInstance(config=config, path=path)

    @classmethod
    def load_if_exists(cls, path_override: str | None = None) -> "ContinueConfigInstance | None":
        """Load continue config only if file exists.

        Args:
            path_override: Optional explicit path to config file.

        Returns:
            ContinueConfigInstance if file exists, None otherwise.
        """
        path = determine_config_path(cls.DEFAULT_LOCATIONS, path_override)
        if not path.exists():
            return None
        config = load_config(cls, path, remove_if_invalid=True, initialize={})
        return ContinueConfigInstance(config=config, path=path)


class ContinueConfigInstance:
    """Instance wrapper for ContinueConfig with path and update functionality.

    This class provides a mutable interface to continuation state with
    automatic file removal when state becomes empty.
    """

    def __init__(self, config: ContinueConfig, path: Path):
        """Initialize config instance.

        Args:
            config: The ContinueConfig model instance.
            path: Path to the config file.
        """
        self.data = config
        self.path = path

    def update(self, mutator: callable[[ContinueConfig], None]) -> None:
        """Update config data and save to file.

        If the config becomes empty (all lists empty, all optional fields None),
        the file will be automatically removed.

        Args:
            mutator: Function that modifies the config data in place.
        """
        mutator(self.data)
        # Use removeIfEmpty=True to automatically delete empty config
        save_config(self.data, self.path, remove_if_empty=True)

    def delete(self) -> None:
        """Delete the config file if it exists."""
        self.path.unlink(missing_ok=True)
