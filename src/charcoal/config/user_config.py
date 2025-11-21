"""User configuration management.

This module provides the UserConfig Pydantic model and associated functions for
managing user-specific preferences such as branch naming, editor, pager, and
GitHub API server settings.
"""

import os
import subprocess
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from charcoal.config.base import (
    determine_config_path,
    load_config,
    save_config,
)
from charcoal.errors import CommandFailedError
from charcoal.git.git_editor import get_git_editor, get_git_pager


class GtiConfig(BaseModel):
    """GTI (Graphite Terminal Interface) configuration item."""

    key: str
    value: str


class AlternativeProfile(BaseModel):
    """Alternative Graphite API profile configuration."""

    name: str
    hostPrefix: str


class UserConfig(BaseModel):
    """User configuration model.

    Attributes:
        branchPrefix: Prefix for newly created branches.
        branchDate: Whether to include date in branch names.
        branchReplacement: Character to replace spaces in branch names.
        tips: Whether to show tips.
        editor: Preferred editor command.
        pager: Preferred pager command.
        restackCommitterDateIsAuthorDate: Use author date as committer date on restack.
        submitIncludeCommitMessages: Include commit messages in PR submissions.
        connectCliToLocalServer: Connect CLI to local development server.
        gtiConfigs: GTI-specific configuration items.
        alternativeProfiles: Alternative Graphite API profiles.
    """

    branchPrefix: str | None = None
    branchDate: bool | None = None
    branchReplacement: Literal["_", "-", ""] | None = None
    tips: bool | None = None
    editor: str | None = None
    pager: str | None = None
    restackCommitterDateIsAuthorDate: bool | None = None
    submitIncludeCommitMessages: bool | None = None
    connectCliToLocalServer: bool | None = None
    gtiConfigs: list[GtiConfig] | None = None
    alternativeProfiles: list[AlternativeProfile] | None = None

    # Default location for user config
    DEFAULT_LOCATIONS: list[tuple[str, str]] = [
        (".graphite_user_config", "USER_HOME"),
    ]

    # Default API and app server URLs
    DEFAULT_GRAPHITE_API_SERVER: str = "https://api.graphite.dev/v1"
    DEFAULT_GRAPHITE_APP_SERVER: str = "https://app.graphite.dev"

    @classmethod
    def load(cls, path_override: str | None = None) -> "UserConfigInstance":
        """Load user config from file or create with defaults.

        Args:
            path_override: Optional explicit path to config file.

        Returns:
            UserConfigInstance with loaded data and helper methods.
        """
        path = determine_config_path(cls.DEFAULT_LOCATIONS, path_override)
        config = load_config(cls, path, remove_if_invalid=False, initialize={})
        return UserConfigInstance(config=config, path=path)

    @classmethod
    def load_if_exists(cls, path_override: str | None = None) -> "UserConfigInstance | None":
        """Load user config only if file exists.

        Args:
            path_override: Optional explicit path to config file.

        Returns:
            UserConfigInstance if file exists, None otherwise.
        """
        path = determine_config_path(cls.DEFAULT_LOCATIONS, path_override)
        if not path.exists():
            return None
        config = load_config(cls, path, remove_if_invalid=False, initialize={})
        return UserConfigInstance(config=config, path=path)


class UserConfigInstance:
    """Instance wrapper for UserConfig with path and helper functionality.

    This class provides helper methods for editor, pager, and API server
    configuration with proper fallback logic.
    """

    def __init__(self, config: UserConfig, path: Path):
        """Initialize config instance.

        Args:
            config: The UserConfig model instance.
            path: Path to the config file.
        """
        self.data = config
        self.path = path

    def update(self, mutator: callable[[UserConfig], None]) -> None:
        """Update config data and save to file.

        Args:
            mutator: Function that modifies the config data in place.
        """
        mutator(self.data)
        save_config(self.data, self.path)

    def delete(self) -> None:
        """Delete the config file if it exists."""
        self.path.unlink(missing_ok=True)

    def get_default_profile(self) -> AlternativeProfile:
        """Get the default or selected alternative profile.

        Checks GRAPHITE_PROFILE environment variable to select a profile.
        Falls back to 'default' profile or empty host prefix.

        Returns:
            The selected profile.

        Raises:
            Exception: If GRAPHITE_PROFILE is set but profile not found.
        """
        alternative_profiles = self.data.alternativeProfiles or []

        # Check environment variable for profile selection
        env_profile = os.environ.get("GRAPHITE_PROFILE")
        if env_profile:
            for profile in alternative_profiles:
                if profile.name == env_profile:
                    return profile
            raise Exception(f"Unknown profile {env_profile}")

        # Look for default profile
        for profile in alternative_profiles:
            if profile.name == "default":
                return profile

        # Return default with empty prefix
        return AlternativeProfile(name="default", hostPrefix="")

    def get_api_server_url(self) -> str:
        """Get the Graphite API server URL.

        Returns local development server if connectCliToLocalServer is True,
        otherwise returns profile-specific or default API server.

        Returns:
            API server URL.
        """
        if self.data.connectCliToLocalServer:
            # Note: In production, this would need NODE_TLS_REJECT_UNAUTHORIZED equivalent
            # For Python, this would be handled in httpx client configuration
            return "https://localhost:8000/v1"

        host_prefix = self.get_default_profile().hostPrefix
        if host_prefix:
            return f"https://api.{host_prefix}.graphite.dev/v1"

        return UserConfig.DEFAULT_GRAPHITE_API_SERVER

    def get_app_server_url(self) -> str:
        """Get the Graphite app server URL.

        Returns profile-specific or default app server URL.

        Returns:
            App server URL.
        """
        host_prefix = self.get_default_profile().hostPrefix
        if host_prefix:
            return f"https://app.{host_prefix}.graphite.dev"

        return UserConfig.DEFAULT_GRAPHITE_APP_SERVER

    def get_editor(self) -> str:
        """Get the preferred editor with proper fallback chain.

        Checks in order:
        1. GT_EDITOR environment variable (single command override)
        2. User config editor field
        3. TEST_GT_EDITOR environment variable (for tests)
        4. Git global core.editor config
        5. GIT_EDITOR environment variable
        6. EDITOR environment variable
        7. 'vi' as final fallback

        Returns:
            Editor command to use.
        """
        # Check environment overrides
        if env_editor := os.environ.get("GT_EDITOR"):
            return env_editor

        # Check config
        if self.data.editor:
            return self.data.editor

        # Check test override
        if test_editor := os.environ.get("TEST_GT_EDITOR"):
            return test_editor

        # Check git config
        if git_editor := get_git_editor():
            return git_editor

        # Check standard environment variables
        if git_env_editor := os.environ.get("GIT_EDITOR"):
            return git_env_editor

        if editor := os.environ.get("EDITOR"):
            return editor

        # Final fallback
        return "vi"

    def get_pager(self) -> str | None:
        """Get the preferred pager with proper fallback chain.

        Checks in order:
        1. GT_PAGER environment variable (single command override)
        2. User config pager field
        3. TEST_GT_PAGER environment variable (for tests)
        4. Git global core.pager config
        5. GIT_PAGER environment variable
        6. PAGER environment variable
        7. 'less' as final fallback

        Returns:
            Pager command to use, or None if explicitly set to empty string.
        """
        # Check environment overrides
        if env_pager := os.environ.get("GT_PAGER"):
            pager = env_pager
        elif self.data.pager is not None:
            pager = self.data.pager
        elif test_pager := os.environ.get("TEST_GT_PAGER"):
            pager = test_pager
        elif git_pager := get_git_pager():
            pager = git_pager
        elif git_env_pager := os.environ.get("GIT_PAGER"):
            pager = git_env_pager
        elif env_pager := os.environ.get("PAGER"):
            pager = env_pager
        else:
            pager = "less"

        # Empty string means no pager
        return None if pager == "" else pager

    def exec_editor(self, edit_file_path: str) -> None:
        """Execute the configured editor on a file.

        Args:
            edit_file_path: Path to the file to edit.

        Raises:
            CommandFailedError: If editor execution fails.
        """
        editor = self.get_editor()
        command_parts = [editor, edit_file_path]

        try:
            subprocess.run(
                command_parts,
                check=True,
                stdin=subprocess.DEVNULL,
                # Inherit stdio to allow interactive editing
                stdout=None,
                stderr=None,
            )
        except subprocess.CalledProcessError as e:
            raise CommandFailedError(
                command=editor,
                args=[edit_file_path],
                status=e.returncode,
                stdout="",
                stderr=str(e),
            ) from e
        except OSError as e:
            raise CommandFailedError(
                command=editor,
                args=[edit_file_path],
                status=-1,
                stdout="",
                stderr=str(e),
            ) from e
