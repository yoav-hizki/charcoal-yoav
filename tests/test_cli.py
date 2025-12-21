"""Smoke tests for CLI entry point."""

from click.testing import CliRunner

from charcoal.cli import cli


def test_cli_help() -> None:
    """Test that the CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Charcoal is a command line tool" in result.output


def test_cli_version() -> None:
    """Test that the CLI version command works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.2.4" in result.output


def test_branch_group_exists() -> None:
    """Test that the branch command group exists."""
    runner = CliRunner()
    result = runner.invoke(cli, ["branch", "--help"])
    assert result.exit_code == 0
    assert "Branch management commands" in result.output


def test_repo_group_exists() -> None:
    """Test that the repo command group exists."""
    runner = CliRunner()
    result = runner.invoke(cli, ["repo", "--help"])
    assert result.exit_code == 0
    assert "Repository-level configuration" in result.output
