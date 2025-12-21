"""Pytest configuration and shared fixtures."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def tmp_home(monkeypatch: pytest.MonkeyPatch) -> Generator[Path, None, None]:
    """Create a temporary HOME directory for isolated testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        home_path = Path(tmpdir)
        monkeypatch.setenv("HOME", str(home_path))
        yield home_path


@pytest.fixture
def tmp_git_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary git repository for testing.

    This fixture creates a basic git repository with initial configuration
    that can be used for testing git operations.
    """
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    os.chdir(repo_path)
    os.system("git init -q")
    os.system('git config user.name "Test User"')
    os.system('git config user.email "test@example.com"')

    # Create an initial commit
    (repo_path / "README.md").write_text("# Test Repository\n")
    os.system("git add README.md")
    os.system('git commit -q -m "Initial commit"')

    yield repo_path


@pytest.fixture
def git_user_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set git user configuration for commits in tests."""
    # This is handled by tmp_git_repo, but can be used standalone
    pass
