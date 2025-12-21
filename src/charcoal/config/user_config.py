"""User configuration system.

This module implements the user configuration with Pydantic models and helper
functions, matching the TypeScript user_config_spf.ts implementation.
"""

import os
import subprocess
from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, Field

from charcoal.config.spiffy import SpiffyFactory, spiffy
from charcoal.errors import CommandFailedError

# Constants
DEFAULT_GRAPHITE_API_SERVER = "https://api.graphite.dev/v1"
DEFAULT_GRAPHITE_APP_SERVER = "https://app.graphite.dev"


class GtiConfig(BaseModel):
    """GTI configuration key-value pair."""

    key: str
    value: str


class Profile(BaseModel):
    """Alternative profile configuration."""

    name: str
    hostPrefix: str = Field(alias="hostPrefix")  # noqa: N815


class UserConfig(BaseModel):
    """User configuration model matching TypeScript schema."""

    branchPrefix: str | None = None  # noqa: N815
    branchDate: bool | None = None  # noqa: N815
    branchReplacement: Literal["_", "-", ""] | None = None  # noqa: N815
    tips: bool | None = None
    editor: str | None = None
    pager: str | None = None
    restackCommitterDateIsAuthorDate: bool | None = None  # noqa: N815
    submitIncludeCommitMessages: bool | None = None  # noqa: N815
    connectCliToLocalServer: bool | None = None  # noqa: N815
    gtiConfigs: list[GtiConfig] | None = None  # noqa: N815
    alternativeProfiles: list[Profile] | None = None  # noqa: N815

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class UserConfigHelpers:
    """Helper functions for user configuration."""

    def __init__(self, data: UserConfig, update: Callable[[Callable[[UserConfig], None]], None]) -> None:
        """Initialize helpers with config data and update function."""
        self._data = data
        self._update = update

    def get_editor(self) -> str:
        """Get the editor to use, with fallback chain.

        Falls back through: GT_EDITOR → config.editor → git config →
        GIT_EDITOR → EDITOR → 'vi'
        """
        # Check environment variable override
        if os.environ.get("GT_EDITOR"):
            return os.environ["GT_EDITOR"]

        # Check config setting
        if self._data.editor:
            return self._data.editor

        # Check test override
        if os.environ.get("TEST_GT_EDITOR"):
            return os.environ["TEST_GT_EDITOR"]

        # Try to get from git config
        git_editor = self._get_git_editor()
        if git_editor:
            return git_editor

        # Check GIT_EDITOR env var
        if os.environ.get("GIT_EDITOR"):
            return os.environ["GIT_EDITOR"]

        # Check EDITOR env var
        if os.environ.get("EDITOR"):
            return os.environ["EDITOR"]

        # Final fallback
        return "vi"

    def get_pager(self) -> str | None:
        """Get the pager to use, with fallback chain.

        Falls back through: GT_PAGER → config.pager → git config →
        GIT_PAGER → PAGER → 'less'

        Returns None if pager is explicitly set to empty string.
        """
        # Check environment variable override
        if "GT_PAGER" in os.environ:
            pager = os.environ["GT_PAGER"]
            return None if pager == "" else pager

        # Check config setting
        if self._data.pager is not None:
            return None if self._data.pager == "" else self._data.pager

        # Check test override
        if "TEST_GT_PAGER" in os.environ:
            pager = os.environ["TEST_GT_PAGER"]
            return None if pager == "" else pager

        # Try to get from git config
        git_pager = self._get_git_pager()
        if git_pager:
            return None if git_pager == "" else git_pager

        # Check GIT_PAGER env var
        if "GIT_PAGER" in os.environ:
            pager = os.environ["GIT_PAGER"]
            return None if pager == "" else pager

        # Check PAGER env var
        if "PAGER" in os.environ:
            pager = os.environ["PAGER"]
            return None if pager == "" else pager

        # Final fallback
        return "less"

    def get_default_profile(self) -> Profile:
        """Get the default profile to use.

        Checks GRAPHITE_PROFILE environment variable first, then looks for
        a profile named 'default', otherwise returns a default profile.
        """
        alternative_profiles = self._data.alternativeProfiles or []

        # Check for profile override via environment variable
        if os.environ.get("GRAPHITE_PROFILE"):
            profile_name = os.environ["GRAPHITE_PROFILE"]
            for profile in alternative_profiles:
                if profile.name == profile_name:
                    return profile
            raise ValueError(f"Unknown profile {profile_name}")

        # Look for profile named 'default'
        for profile in alternative_profiles:
            if profile.name == "default":
                return profile

        # Return default profile
        return Profile(name="default", hostPrefix="")

    def get_api_server_url(self) -> str:
        """Get the API server URL based on configuration.

        Returns localhost URL if connectCliToLocalServer is enabled,
        otherwise returns profile-based URL.
        """
        if self._data.connectCliToLocalServer:
            # Note: In production, would also set NODE_TLS_REJECT_UNAUTHORIZED
            # but we can't do that safely in Python without affecting other code
            return "https://localhost:8000/v1"

        host_prefix = self.get_default_profile().hostPrefix
        if host_prefix:
            return f"https://api.{host_prefix}.graphite.dev/v1"

        return DEFAULT_GRAPHITE_API_SERVER

    def get_app_server_url(self) -> str:
        """Get the app server URL based on profile configuration."""
        host_prefix = self.get_default_profile().hostPrefix
        if host_prefix:
            return f"https://app.{host_prefix}.graphite.dev"

        return DEFAULT_GRAPHITE_APP_SERVER

    def exec_editor(self, edit_file_path: str) -> None:
        """Execute the configured editor on a file.

        Args:
            edit_file_path: Path to the file to edit

        Raises:
            CommandFailedError: If editor fails to execute
        """
        editor = self.get_editor()
        command = f"{editor} {edit_file_path}"

        try:
            subprocess.run(
                command,
                shell=True,
                check=True,
                stdin=None,
                stdout=None,
                stderr=None,
            )
        except subprocess.CalledProcessError as e:
            raise CommandFailedError(
                command=command,
                message=f"Editor failed: {e}",
                returncode=e.returncode,
            ) from e

    def _get_git_editor(self) -> str | None:
        """Get editor from git config."""
        try:
            result = subprocess.run(
                ["git", "config", "--global", "core.editor"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _get_git_pager(self) -> str | None:
        """Get pager from git config."""
        try:
            result = subprocess.run(
                ["git", "config", "--global", "core.pager"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return None


def _create_user_config_helpers(
    data: UserConfig,
    update: Callable[[Callable[[UserConfig], None]], None],
) -> UserConfigHelpers:
    """Factory function to create user config helpers."""
    return UserConfigHelpers(data, update)


# Create the user config factory
user_config_factory: SpiffyFactory[UserConfig, UserConfigHelpers] = spiffy(
    model_class=UserConfig,
    default_locations=[(".graphite_user_config", "USER_HOME")],
    initialize=lambda: {},
    helper_factory=_create_user_config_helpers,
)
