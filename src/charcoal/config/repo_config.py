"""Repository configuration management.

This module provides the RepoConfig Pydantic model and associated functions for
managing repository-specific configuration such as trunk branch, remote settings,
and GitHub integration preferences.
"""

import re
from pathlib import Path
from typing import Self

from pydantic import BaseModel

from charcoal.errors import ExitFailedError
from charcoal.git.runner import run_git_command
from charcoal.config.base import (
    determine_config_path,
    load_config,
    save_config,
)


class RepoConfig(BaseModel):
    """Repository configuration model.

    Attributes:
        host: GitHub host (e.g., 'github.com' or enterprise host).
        owner: Repository owner/organization.
        name: Repository name.
        trunk: Trunk/main branch name.
        remote: Git remote name (defaults to 'origin').
        lastFetchedPRInfoMs: Timestamp of last PR info fetch (milliseconds).
        isGithubIntegrationEnabled: Whether GitHub integration is enabled.
    """

    host: str | None = None
    owner: str | None = None
    name: str | None = None
    trunk: str | None = None
    remote: str | None = None
    lastFetchedPRInfoMs: int | None = None
    isGithubIntegrationEnabled: bool | None = None

    # Default location for repo config
    DEFAULT_LOCATIONS: list[tuple[str, str]] = [
        (".graphite_repo_config", "REPO"),
    ]

    @classmethod
    def load(cls, path_override: str | None = None) -> "RepoConfigInstance":
        """Load repo config from file or create with defaults.

        Args:
            path_override: Optional explicit path to config file.

        Returns:
            RepoConfigInstance with loaded data and helper methods.
        """
        path = determine_config_path(cls.DEFAULT_LOCATIONS, path_override)
        config = load_config(cls, path, remove_if_invalid=False, initialize={})
        return RepoConfigInstance(config=config, path=path)

    @classmethod
    def load_if_exists(cls, path_override: str | None = None) -> "RepoConfigInstance | None":
        """Load repo config only if file exists.

        Args:
            path_override: Optional explicit path to config file.

        Returns:
            RepoConfigInstance if file exists, None otherwise.
        """
        path = determine_config_path(cls.DEFAULT_LOCATIONS, path_override)
        if not path.exists():
            return None
        config = load_config(cls, path, remove_if_invalid=False, initialize={})
        return RepoConfigInstance(config=config, path=path)

    def get_remote(self) -> str:
        """Get the remote name, defaulting to 'origin'."""
        return self.remote or "origin"

    def graphite_initialized(self) -> bool:
        """Check if Graphite/Charcoal is initialized (has trunk set)."""
        return self.trunk is not None

    def get_repo_host(self) -> str:
        """Get repository host, inferring from git remote if not configured.

        Returns:
            Repository host (e.g., 'github.com').

        Raises:
            ExitFailedError: If host cannot be determined.
        """
        if self.host:
            return self.host

        inferred = infer_repo_github_info(self.get_remote())
        if inferred:
            return inferred["repoHost"]

        raise ExitFailedError(
            "Could not determine the host of this repo (e.g. 'github.com' in the repo "
            "'https://github.com/danerwilliams/charcoal'). Please run "
            "`charcoal repo owner --set <owner>` to manually set the repo owner."
        )

    def get_repo_owner(self) -> str:
        """Get repository owner, inferring from git remote if not configured.

        Returns:
            Repository owner.

        Raises:
            ExitFailedError: If owner cannot be determined.
        """
        if self.owner:
            return self.owner

        inferred = infer_repo_github_info(self.get_remote())
        if inferred:
            return inferred["repoOwner"]

        raise ExitFailedError(
            "Could not determine the owner of this repo (e.g. 'charcoal' in the repo "
            "'danerwilliams/charcoal'). Please run `charcoal repo owner --set <owner>` "
            "to manually set the repo owner."
        )

    def get_repo_name(self) -> str:
        """Get repository name, inferring from git remote if not configured.

        Returns:
            Repository name.

        Raises:
            ExitFailedError: If name cannot be determined.
        """
        if self.name:
            return self.name

        inferred = infer_repo_github_info(self.get_remote())
        if inferred:
            return inferred["repoName"]

        raise ExitFailedError(
            "Could not determine the name of this repo (e.g. 'charcoal' in the repo "
            "'danerwilliams/charcoal'). Please run `charcoal repo name --set <name>` "
            "to manually set the repo name."
        )

    def get_is_github_integration_enabled(self) -> bool:
        """Check if GitHub integration is enabled, defaulting to True."""
        return self.isGithubIntegrationEnabled if self.isGithubIntegrationEnabled is not None else True


class RepoConfigInstance:
    """Instance wrapper for RepoConfig with path and update functionality.

    This class provides a mutable interface to config data along with
    helper methods for common operations.
    """

    def __init__(self, config: RepoConfig, path: Path):
        """Initialize config instance.

        Args:
            config: The RepoConfig model instance.
            path: Path to the config file.
        """
        self.data = config
        self.path = path

    def update(self, mutator: callable[[RepoConfig], None]) -> None:
        """Update config data and save to file.

        Args:
            mutator: Function that modifies the config data in place.
        """
        mutator(self.data)
        save_config(self.data, self.path)

    def delete(self) -> None:
        """Delete the config file if it exists."""
        self.path.unlink(missing_ok=True)

    def set_remote(self, remote: str) -> None:
        """Set the git remote name."""
        self.update(lambda data: setattr(data, "remote", remote))

    def get_remote(self) -> str:
        """Get the remote name, defaulting to 'origin'."""
        return self.data.get_remote()

    def set_trunk(self, trunk: str) -> None:
        """Set the trunk branch name."""
        self.update(lambda data: setattr(data, "trunk", trunk))

    def set_is_github_integration_enabled(self, is_enabled: bool) -> None:
        """Set whether GitHub integration is enabled."""
        self.update(lambda data: setattr(data, "isGithubIntegrationEnabled", is_enabled))

    def get_is_github_integration_enabled(self) -> bool:
        """Check if GitHub integration is enabled."""
        return self.data.get_is_github_integration_enabled()

    def graphite_initialized(self) -> bool:
        """Check if Graphite/Charcoal is initialized."""
        return self.data.graphite_initialized()

    def get_repo_host(self) -> str:
        """Get repository host."""
        return self.data.get_repo_host()

    def get_repo_owner(self) -> str:
        """Get repository owner."""
        return self.data.get_repo_owner()

    def get_repo_name(self) -> str:
        """Get repository name."""
        return self.data.get_repo_name()


def infer_repo_github_info(remote: str) -> dict[str, str] | None:
    """Infer repository GitHub info from git remote configuration.

    Args:
        remote: Git remote name (e.g., 'origin').

    Returns:
        Dictionary with 'repoOwner', 'repoName', and 'repoHost' keys,
        or None if info cannot be inferred.

    Raises:
        ExitFailedError: If remote URL is invalid or cannot be parsed.
    """
    # Get remote URL from git config
    url = run_git_command(
        args=["config", "--get", f"remote.{remote}.url"],
        on_error="ignore",
        resource="inferRepoGitHubInfo",
    )

    if not url:
        raise ExitFailedError(
            f"Failed to infer the owner and name of this repo from remote {remote}. "
            "Please run `charcoal repo owner --set <owner>` and "
            "`charcoal repo name --set <name>` to manually set the repo owner/name. "
            "(e.g. in the repo 'danerwilliams/charcoal', 'danerwilliams' is the repo owner "
            "and 'charcoal' is the repo name)"
        )

    match = get_owner_and_name_from_url(url)
    if match is None:
        raise ExitFailedError(
            f"Failed to infer the owner and name of this repo from remote {remote} \"{url}\". "
            "Please run `charcoal repo owner --set <owner>` and "
            "`charcoal repo name --set <name>` to manually set the repo owner/name. "
            "(e.g. in the repo 'danerwilliams/charcoal', 'danerwilliams' is the repo owner "
            "and 'charcoal' is the repo name)"
        )

    return {
        "repoOwner": match["owner"],
        "repoName": match["name"],
        "repoHost": match["hostname"],
    }


def get_owner_and_name_from_url(url: str) -> dict[str, str] | None:
    """Extract repo info from a remote URL.

    Supports various GitHub URL formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - github.com:owner/repo.git
    - git@github.com:owner/repo.git
    - ssh:git@github.com:owner/repo.git
    - ssh://git@github.com/owner/repo.git
    - git+ssh:git@github.com:owner/repo.git

    Also supports GitHub Enterprise URLs with custom hostnames.

    Args:
        url: Git remote URL.

    Returns:
        Dictionary with 'name', 'owner', and 'hostname' keys,
        or None if URL format is not recognized.

    Example:
        >>> get_owner_and_name_from_url("https://github.com/user/repo.git")
        {'name': 'repo', 'owner': 'user', 'hostname': 'github.com'}
    """
    # Pattern explanation:
    # (?:https:\/\/(.*)\/|          - HTTPS URL with hostname in group 1
    # (?:(?:git\+)?ssh:\/\/)?       - Optional ssh:// or git+ssh:// prefix
    # (?:git@)?                     - Optional git@ user
    # ([^:/]*)[:/])                 - Hostname in group 2, followed by : or /
    # ([^/]+)\/                     - Owner in group 3
    # (.+?)                         - Repo name in group 4 (non-greedy)
    # (?:\.git)?$                   - Optional .git suffix
    pattern = r"(?:https:\/\/(.*)\/|(?:(?:git\+)?ssh:\/\/)?(?:git@)?([^:/]*)[:/])([^/]+)\/(.+?)(?:\.git)?$"

    match = re.search(pattern, url)
    if not match:
        return None

    hostname1, hostname2, owner, repo = match.groups()
    hostname = hostname1 or hostname2

    return {
        "owner": owner,
        "name": repo,
        "hostname": hostname,
    }
