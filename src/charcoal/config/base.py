"""Base configuration utilities for file I/O operations.

This module provides shared utilities for loading and saving configuration files
with proper JSON serialization, file permissions, and error handling.
"""

import json
import os
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from charcoal.errors import ExitFailedError
from charcoal.preconditions import current_git_repo_precondition

T = TypeVar("T", bound=BaseModel)


def resolve_config_path(relative_path: str, relative_to: str) -> Path:
    """Resolve a configuration file path relative to USER_HOME or REPO root.

    Args:
        relative_path: The relative path to the config file.
        relative_to: Either 'USER_HOME' or 'REPO' to determine the base path.

    Returns:
        Absolute Path to the configuration file.

    Raises:
        ExitFailedError: If relative_to is 'REPO' but not in a git repository.
    """
    if relative_to == "USER_HOME":
        return Path.home() / relative_path
    elif relative_to == "REPO":
        repo_root = current_git_repo_precondition()
        return Path(repo_root) / relative_path
    else:
        raise ValueError(f"Invalid relative_to value: {relative_to}")


def load_config(
    model_class: type[T],
    path: Path,
    *,
    remove_if_invalid: bool = False,
    initialize: dict[str, Any] | None = None,
) -> T:
    """Load a configuration file and validate it against a Pydantic model.

    Args:
        model_class: The Pydantic model class to validate against.
        path: Path to the configuration file.
        remove_if_invalid: If True, remove invalid config and return initialized data.
        initialize: Default data to use if file doesn't exist or is invalid.

    Returns:
        Validated configuration data as a Pydantic model instance.

    Raises:
        ExitFailedError: If config file is malformed and remove_if_invalid is False.
    """
    if initialize is None:
        initialize = {}

    # If file doesn't exist, return initialized data
    if not path.exists():
        return model_class(**initialize)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return model_class(**data)
    except (json.JSONDecodeError, ValidationError, ValueError) as e:
        if remove_if_invalid:
            # Remove the invalid file and return initialized data
            path.unlink(missing_ok=True)
            return model_class(**initialize)
        else:
            raise ExitFailedError(f"Malformed data at {path}") from e


def save_config(
    config: BaseModel,
    path: Path,
    *,
    remove_if_empty: bool = False,
) -> None:
    """Save a configuration object to a JSON file.

    Args:
        config: The Pydantic model instance to save.
        path: Path where the configuration should be saved.
        remove_if_empty: If True, remove file if config is empty (all fields None/default).

    The file is written with mode 0o600 for security (owner read/write only).
    """
    # Convert to dict, excluding unset fields
    config_dict = config.model_dump(mode="json", exclude_unset=False, exclude_none=True)

    # Check if empty and should be removed
    if remove_if_empty and len(config_dict) == 0:
        path.unlink(missing_ok=True)
        return

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write with pretty formatting and secure permissions
    json_str = json.dumps(config_dict, indent=2, ensure_ascii=False)

    # Write to temp file first, then rename for atomicity
    temp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(json_str)
            f.write("\n")  # Add trailing newline like TypeScript version

        # Set secure permissions (owner read/write only)
        os.chmod(temp_path, 0o600)

        # Atomic rename
        temp_path.replace(path)
    except Exception:
        # Clean up temp file if something goes wrong
        temp_path.unlink(missing_ok=True)
        raise


def find_existing_config_path(locations: list[tuple[str, str]]) -> Path | None:
    """Find the first existing config file from a list of possible locations.

    Args:
        locations: List of tuples (relative_path, relative_to) to check.

    Returns:
        Path to the first existing config file, or None if none exist.
    """
    for relative_path, relative_to in locations:
        try:
            path = resolve_config_path(relative_path, relative_to)
            if path.exists():
                return path
        except ExitFailedError:
            # If we can't resolve (e.g., not in a repo), skip this location
            continue
    return None


def determine_config_path(
    locations: list[tuple[str, str]],
    path_override: str | None = None,
) -> Path:
    """Determine the config file path, preferring existing files or override.

    Args:
        locations: List of tuples (relative_path, relative_to) for default locations.
        path_override: Optional explicit path to use instead of default locations.

    Returns:
        Path to use for the config file.

    If path_override is provided, it's used directly.
    Otherwise, returns the first existing config file from locations.
    If no existing file is found, returns the first location.
    """
    if path_override:
        return Path(path_override)

    # Check for existing config
    existing = find_existing_config_path(locations)
    if existing:
        return existing

    # Return first location as default
    relative_path, relative_to = locations[0]
    return resolve_config_path(relative_path, relative_to)
