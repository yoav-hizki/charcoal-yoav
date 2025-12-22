"""Repository configuration system.

This module implements the repository configuration with Pydantic models and
helper functions, matching the TypeScript repo_config_spf.ts implementation.
"""

import re
import subprocess
from collections.abc import Callable

from pydantic import BaseModel

from charcoal.config.spiffy import SpiffyFactory, spiffy
from charcoal.lib.errors import ExitFailedError


class RepoConfig(BaseModel):
    """Repository configuration model matching TypeScript schema."""

    host: str | None = None
    owner: str | None = None
    name: str | None = None
    trunk: str | None = None
    remote: str | None = None
    lastFetchedPRInfoMs: int | None = None  # noqa: N815
    isGithubIntegrationEnabled: bool | None = None  # noqa: N815


class RepoConfigHelpers:
    """Helper functions for repository configuration."""

    def __init__(
        self, data: RepoConfig, update: Callable[[Callable[[RepoConfig], None]], None]
    ) -> None:
        """Initialize helpers with config data and update function."""
        self._data = data
        self._update = update

    def set_remote(self, remote: str) -> None:
        """Set the remote name."""
        def mutator(data: RepoConfig) -> None:
            data.remote = remote
        self._update(mutator)

    def get_remote(self) -> str:
        """Get the remote name, defaulting to 'origin'."""
        return self._data.remote or "origin"

    def set_trunk(self, trunk: str) -> None:
        """Set the trunk branch name."""
        def mutator(data: RepoConfig) -> None:
            data.trunk = trunk
        self._update(mutator)

    def get_trunk(self) -> str | None:
        """Get the trunk branch name."""
        return self._data.trunk

    def set_is_github_integration_enabled(self, is_enabled: bool) -> None:
        """Set whether GitHub integration is enabled."""
        def mutator(data: RepoConfig) -> None:
            data.isGithubIntegrationEnabled = is_enabled
        self._update(mutator)

    def get_is_github_integration_enabled(self) -> bool:
        """Get whether GitHub integration is enabled, defaulting to True."""
        if self._data.isGithubIntegrationEnabled is None:
            return True
        return self._data.isGithubIntegrationEnabled

    def graphite_initialized(self) -> bool:
        """Check if Graphite has been initialized (trunk is set)."""
        return bool(self._data.trunk)

    def get_repo_host(self) -> str:
        """Get the repository host (e.g., 'github.com').

        Returns:
            Repository host

        Raises:
            ExitFailedError: If host cannot be determined
        """
        if self._data.host:
            return self._data.host

        inferred_info = self._infer_repo_github_info()
        if inferred_info and inferred_info["repoHost"]:
            return inferred_info["repoHost"]

        raise ExitFailedError(
            "Could not determine the host of this repo (e.g. 'github.com' in the "
            "repo 'https://github.com/danerwilliams/charcoal'). Please run "
            "`gt repo owner --set <owner>` to manually set the repo owner."
        )

    def get_repo_owner(self) -> str:
        """Get the repository owner.

        Returns:
            Repository owner

        Raises:
            ExitFailedError: If owner cannot be determined
        """
        if self._data.owner:
            return self._data.owner

        inferred_info = self._infer_repo_github_info()
        if inferred_info and inferred_info["repoOwner"]:
            return inferred_info["repoOwner"]

        raise ExitFailedError(
            "Could not determine the owner of this repo (e.g. 'charcoal' in the "
            "repo 'danerwilliams/charcoal'). Please run "
            "`gt repo owner --set <owner>` to manually set the repo owner."
        )

    def get_repo_name(self) -> str:
        """Get the repository name.

        Returns:
            Repository name

        Raises:
            ExitFailedError: If name cannot be determined
        """
        if self._data.name:
            return self._data.name

        inferred_info = self._infer_repo_github_info()
        if inferred_info and inferred_info["repoName"]:
            return inferred_info["repoName"]

        raise ExitFailedError(
            "Could not determine the name of this repo (e.g. 'charcoal' in the "
            "repo 'danerwilliams/charcoal'). Please run "
            "`gt repo name --set <owner>` to manually set the repo name."
        )

    def _infer_repo_github_info(self) -> dict[str, str] | None:
        """Infer repository information from git remote URL.

        Returns:
            Dict with repoOwner, repoName, and repoHost, or None if cannot infer
        """
        remote = self.get_remote()

        # Get the remote URL
        try:
            result = subprocess.run(
                ["git", "config", "--get", f"remote.{remote}.url"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0 or not result.stdout.strip():
                return None

            url = result.stdout.strip()
        except Exception:
            return None

        # Parse the URL
        match = get_owner_and_name_from_url(url)
        if not match:
            return None

        return {
            "repoOwner": match["owner"],
            "repoName": match["name"],
            "repoHost": match["hostname"],
        }


def get_owner_and_name_from_url(url: str) -> dict[str, str] | None:
    """Extract repo info from a remote URL.

    Supports various formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - github.com:owner/repo.git
    - git@github.com:owner/repo.git
    - ssh:git@github.com:owner/repo.git
    - ssh://git@github.com/owner/repo.git
    - git+ssh:git@github.com:owner/repo.git

    Args:
        url: Git remote URL

    Returns:
        Dict with 'owner', 'name', and 'hostname', or None if cannot parse
    """
    # Pattern to match various git URL formats
    pattern = r"(?:https://(.*)\/|(?:git\+ssh:\/\/|ssh:\/\/)?(?:git@)?([^:/]*)[:/])([^/]+)\/(.+?)(?:\.git)?$"
    match = re.match(pattern, url)

    if not match:
        return None

    hostname1, hostname2, owner, repo = match.groups()
    hostname = hostname1 or hostname2

    return {"owner": owner, "name": repo, "hostname": hostname}


def _create_repo_config_helpers(
    data: RepoConfig,
    update: Callable[[Callable[[RepoConfig], None]], None],
) -> RepoConfigHelpers:
    """Factory function to create repo config helpers."""
    return RepoConfigHelpers(data, update)


# Create the repo config factory
repo_config_factory: SpiffyFactory[RepoConfig, RepoConfigHelpers] = spiffy(
    model_class=RepoConfig,
    default_locations=[(".graphite_repo_config", "REPO")],
    initialize=lambda: {},
    helper_factory=_create_repo_config_helpers,
)
