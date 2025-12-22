"""Tests for the git runner module."""

import pytest

from charcoal.git.runner import run_git_command, run_git_command_and_split_lines
from charcoal.lib.errors import CommandFailedError


def test_run_git_command_success() -> None:
    """Test running a successful git command."""
    # This should work in any environment with git installed
    result = run_git_command(args=["--version"], on_error="throw")
    assert "git version" in result
    assert result.strip() == result  # Should be trimmed by default


def test_run_git_command_no_trim() -> None:
    """Test running a git command without trimming output."""
    result = run_git_command(args=["--version"], on_error="throw", no_trim=True)
    # Output might have trailing newline when not trimmed
    assert "git version" in result


def test_run_git_command_failure_throw() -> None:
    """Test that a failing git command raises an exception."""
    with pytest.raises(CommandFailedError) as exc_info:
        run_git_command(args=["invalid-command-xyz"], on_error="throw")

    assert exc_info.value.command == "git invalid-command-xyz"
    assert exc_info.value.returncode != 0


def test_run_git_command_failure_ignore() -> None:
    """Test that a failing git command returns empty string when ignored."""
    result = run_git_command(args=["invalid-command-xyz"], on_error="ignore")
    assert result == ""


def test_run_git_command_and_split_lines() -> None:
    """Test splitting git command output into lines."""
    # Run a command that produces multiple lines (git help commands list)
    result = run_git_command_and_split_lines(
        args=["help", "--all"], on_error="throw"
    )

    # Should be a list
    assert isinstance(result, list)
    # Should have multiple lines
    assert len(result) > 0
    # Lines should be non-empty
    assert all(line for line in result)


def test_run_git_command_and_split_lines_empty() -> None:
    """Test splitting empty output."""
    # Use a command that returns no output on failure but doesn't error
    result = run_git_command_and_split_lines(
        args=["invalid-command-xyz"], on_error="ignore"
    )

    assert result == []
