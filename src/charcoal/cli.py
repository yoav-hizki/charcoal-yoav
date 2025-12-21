"""Main CLI entry point for Charcoal."""

import sys

import click

from charcoal import __version__


@click.group()
@click.version_option(version=__version__, prog_name="charcoal")
@click.option(
    "--interactive/--no-interactive",
    default=True,
    help="Prompt the user. Disable with --no-interactive.",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    default=False,
    help="Minimize output to the terminal.",
)
@click.option(
    "--verify/--no-verify",
    default=True,
    help="Run git hooks. Disable with --no-verify.",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Display debug output.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    interactive: bool,
    quiet: bool,
    verify: bool,
    debug: bool,
) -> None:
    """Charcoal is a command line tool that makes working with stacked changes fast & intuitive.

    https://docs.graphite.dev/guides/graphite-cli
    """
    # Store global options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["interactive"] = interactive
    ctx.obj["quiet"] = quiet
    ctx.obj["verify"] = verify
    ctx.obj["debug"] = debug


# Placeholder command groups to demonstrate structure
@cli.group(name="branch")
def branch_group() -> None:
    """Branch management commands."""
    pass


@cli.group(name="commit")
def commit_group() -> None:
    """Commit operations."""
    pass


@cli.group(name="stack")
def stack_group() -> None:
    """Stack operations."""
    pass


@cli.group(name="repo")
def repo_group() -> None:
    """Repository-level configuration and maintenance."""
    pass


# Add simple placeholder commands to demonstrate the structure
@branch_group.command(name="create")
@click.argument("branch_name", required=False)
@click.pass_context
def branch_create(ctx: click.Context, branch_name: str | None) -> None:
    """Create a new branch (not yet implemented)."""
    click.echo("Branch create command not yet implemented.")
    sys.exit(1)


@repo_group.command(name="init")
@click.pass_context
def repo_init(ctx: click.Context) -> None:
    """Initialize repository for Charcoal (not yet implemented)."""
    click.echo("Repository initialization not yet implemented.")
    sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\nInterrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
