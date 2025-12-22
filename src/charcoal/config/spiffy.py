"""Spiffy - Schema-validated Persisted Files system.

This module provides a base abstraction for configuration file I/O with
Pydantic validation, matching the TypeScript Spiffy implementation.
"""

import json
import os
from collections.abc import Callable
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from charcoal.lib.errors import ExitFailedError

# Type variables for generic spiffy instances
TModel = TypeVar("TModel", bound=BaseModel)
THelpers = TypeVar("THelpers")


class SpiffyInstance(Generic[TModel, THelpers]):
    """A loaded Spiffy configuration file instance with data and helper methods."""

    def __init__(
        self,
        data: TModel,
        file_path: str,
        model_class: type[TModel],
        helper_factory: Callable[[TModel, Callable[[Callable[[TModel], None]], None]], THelpers],
        remove_if_empty: bool = False,
    ) -> None:
        """Initialize a Spiffy instance.

        Args:
            data: The validated configuration data
            file_path: Absolute path to the configuration file
            model_class: The Pydantic model class for validation
            helper_factory: Function to create helper methods
            remove_if_empty: Whether to remove the file if data becomes empty
        """
        self._data = data
        self._file_path = file_path
        self._model_class = model_class
        self._remove_if_empty = remove_if_empty

        # Create the update function that will be passed to helper_factory
        def update(mutator: Callable[[TModel], None]) -> None:
            """Update the configuration data and persist to disk."""
            mutator(self._data)

            # Check if we should remove the file because it's empty
            if self._remove_if_empty and self._is_empty():
                if os.path.exists(self._file_path):
                    os.remove(self._file_path)
            else:
                self._save()

        self._update = update
        self._helpers = helper_factory(self._data, update)

    @property
    def data(self) -> TModel:
        """Get the configuration data."""
        return self._data

    @property
    def path(self) -> str:
        """Get the file path."""
        return self._file_path

    def update(self, mutator: Callable[[TModel], None]) -> None:
        """Update the configuration using a mutator function."""
        self._update(mutator)

    def delete(self) -> None:
        """Delete the configuration file."""
        if os.path.exists(self._file_path):
            os.remove(self._file_path)

    def get_helpers(self) -> THelpers:
        """Get the helper methods for this configuration."""
        return self._helpers

    def _save(self) -> None:
        """Save the configuration data to disk with proper permissions."""
        # Ensure parent directory exists
        parent_dir = os.path.dirname(self._file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        # Write with pretty-printing (2-space indentation like TypeScript)
        json_str = json.dumps(
            self._data.model_dump(exclude_none=True, mode="json"),
            indent=2,
            ensure_ascii=False,
        )

        # Set permissions to 0o600 (owner read/write only)
        with open(self._file_path, "w", encoding="utf-8") as f:
            f.write(json_str)
            f.write("\n")  # Add trailing newline

        os.chmod(self._file_path, 0o600)

    def _is_empty(self) -> bool:
        """Check if the configuration data is empty (all fields are None/default)."""
        data_dict = self._data.model_dump(exclude_none=True)
        return len(data_dict) == 0


class SpiffyFactory(Generic[TModel, THelpers]):
    """Factory for creating and loading Spiffy configuration instances."""

    def __init__(
        self,
        model_class: type[TModel],
        default_locations: list[tuple[str, str]],
        initialize: Callable[[], dict[str, Any]],
        helper_factory: Callable[[TModel, Callable[[Callable[[TModel], None]], None]], THelpers],
        remove_if_empty: bool = False,
        remove_if_invalid: bool = False,
    ) -> None:
        """Initialize a Spiffy factory.

        Args:
            model_class: The Pydantic model class to validate against
            default_locations: List of (relative_path, relative_to) tuples
                where relative_to is either 'USER_HOME' or 'REPO'
            initialize: Function to create default data for new files
            helper_factory: Function to create helper methods
            remove_if_empty: Whether to remove files that become empty
            remove_if_invalid: Whether to remove files with invalid data
        """
        self._model_class = model_class
        self._default_locations = default_locations
        self._initialize = initialize
        self._helper_factory = helper_factory
        self._remove_if_empty = remove_if_empty
        self._remove_if_invalid = remove_if_invalid

    def _determine_path(self, default_path_override: str | None = None) -> str:
        """Determine the absolute file path to use.

        Args:
            default_path_override: Optional path override (takes precedence)

        Returns:
            Absolute file path to use
        """
        if default_path_override:
            return os.path.abspath(default_path_override)

        # Check if GRAPHITE_USER_CONFIG_PATH env var is set (for user config)
        env_override = os.environ.get("GRAPHITE_USER_CONFIG_PATH")
        if env_override:
            paths = [os.path.expanduser(env_override)]
        else:
            paths = self._get_absolute_paths()

        # Return first existing path, or first path if none exist
        for path in paths:
            if os.path.exists(path):
                return path

        return paths[0] if paths else ""

    def _get_absolute_paths(self) -> list[str]:
        """Get absolute paths for all default locations."""
        from charcoal.git.preconditions import get_repo_root_path

        paths = []
        for relative_path, relative_to in self._default_locations:
            if relative_to == "USER_HOME":
                base = os.path.expanduser("~")
            elif relative_to == "REPO":
                try:
                    base = os.path.join(get_repo_root_path(), ".git")
                except Exception:
                    # If not in a repo, skip this location
                    continue
            else:
                continue

            paths.append(os.path.join(base, relative_path))

        return paths

    def _read_or_init(self, file_path: str) -> TModel:
        """Read configuration from file or initialize with defaults.

        Args:
            file_path: Path to the configuration file

        Returns:
            Validated configuration data

        Raises:
            ExitFailedError: If file contains malformed data and remove_if_invalid is False
        """
        file_exists = os.path.exists(file_path)

        try:
            if file_exists:
                with open(file_path, encoding="utf-8") as f:
                    data_dict = json.load(f)
            else:
                data_dict = self._initialize()

            # Validate with Pydantic
            return self._model_class.model_validate(data_dict)

        except (json.JSONDecodeError, ValidationError) as e:
            if self._remove_if_invalid and file_exists:
                os.remove(file_path)
                return self._model_class.model_validate(self._initialize())
            else:
                raise ExitFailedError(f"Malformed data at {file_path}: {e}") from e

    def load(self, default_path_override: str | None = None) -> SpiffyInstance[TModel, THelpers]:
        """Load a configuration file, creating it with defaults if it doesn't exist.

        Args:
            default_path_override: Optional path override

        Returns:
            SpiffyInstance with the loaded configuration
        """
        file_path = self._determine_path(default_path_override)
        data = self._read_or_init(file_path)

        return SpiffyInstance(
            data=data,
            file_path=file_path,
            model_class=self._model_class,
            helper_factory=self._helper_factory,
            remove_if_empty=self._remove_if_empty,
        )

    def load_if_exists(
        self, default_path_override: str | None = None
    ) -> SpiffyInstance[TModel, THelpers] | None:
        """Load a configuration file only if it exists.

        Args:
            default_path_override: Optional path override

        Returns:
            SpiffyInstance if file exists, None otherwise
        """
        file_path = self._determine_path(default_path_override)

        if not os.path.exists(file_path):
            return None

        return self.load(default_path_override)


def spiffy(
    model_class: type[TModel],
    default_locations: list[tuple[str, str]],
    initialize: Callable[[], dict[str, Any]],
    helper_factory: Callable[[TModel, Callable[[Callable[[TModel], None]], None]], THelpers],
    remove_if_empty: bool = False,
    remove_if_invalid: bool = False,
) -> SpiffyFactory[TModel, THelpers]:
    """Create a Spiffy factory for a configuration file.

    Args:
        model_class: The Pydantic model class to validate against
        default_locations: List of (relative_path, relative_to) tuples
        initialize: Function to create default data
        helper_factory: Function to create helper methods
        remove_if_empty: Whether to remove files that become empty
        remove_if_invalid: Whether to remove files with invalid data

    Returns:
        SpiffyFactory instance
    """
    return SpiffyFactory(
        model_class=model_class,
        default_locations=default_locations,
        initialize=initialize,
        helper_factory=helper_factory,
        remove_if_empty=remove_if_empty,
        remove_if_invalid=remove_if_invalid,
    )
