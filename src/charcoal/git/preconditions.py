"""Git preconditions and validation functions."""

import subprocess


def get_repo_root_path() -> str:
    """Get the root path of the current git repository.

    Returns:
        Absolute path to the repository root

    Raises:
        Exception: If not in a git repository
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception("Not in a git repository") from e
