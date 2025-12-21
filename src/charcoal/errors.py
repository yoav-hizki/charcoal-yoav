"""Error classes for the CLI.

This module defines all custom exception types used throughout the CLI,
matching the TypeScript error classes for consistent error handling.
"""

from typing import Any

from charcoal.utils.colors import cyan, yellow


class GraphiteError(Exception):
    """Base class for all Charcoal/Graphite errors.

    This provides a common base for catching any CLI-specific error.
    """

    pass


class ExitFailedError(GraphiteError):
    """Raised when a command fails and should exit with an error code.

    This is used for general command failures that need to propagate
    up to the CLI runner for proper exit code handling.
    """

    def __init__(self, message: str) -> None:
        """Initialize the error.

        Args:
            message: Description of why the command failed
        """
        super().__init__(message)
        self.name = "ExitFailed"


class NonInteractiveError(GraphiteError):
    """Raised when an interactive operation is attempted in non-interactive mode.

    This error is raised when the CLI is running in non-interactive mode
    (e.g., in a CI environment) and a command requires user input.
    """

    def __init__(self) -> None:
        """Initialize the error with a standard message."""
        super().__init__("Cannot perform interactive operation in non-interactive mode.")
        self.name = "NonInteractive"


class RebaseConflictError(GraphiteError):
    """Raised when a rebase operation encounters merge conflicts.

    This signals that the rebase has stopped due to conflicts and the user
    needs to resolve them manually.
    """

    def __init__(self) -> None:
        """Initialize the error with a standard message."""
        super().__init__("Hit a conflict during rebase.")
        self.name = "RebaseConflict"


class PreconditionsFailedError(GraphiteError):
    """Raised when command preconditions are not met.

    This is used for various validation failures such as uncommitted changes,
    invalid branch states, or other requirements that must be satisfied
    before a command can execute.
    """

    def __init__(self, message: str) -> None:
        """Initialize the error.

        Args:
            message: Description of which precondition failed
        """
        super().__init__(message)
        self.name = "PreconditionsFailed"


class ConcurrentExecutionError(GraphiteError):
    """Raised when multiple Charcoal processes try to run simultaneously.

    This prevents race conditions by ensuring only one CLI process can
    modify the repository state at a time.
    """

    def __init__(self) -> None:
        """Initialize the error with a standard message."""
        super().__init__("Cannot run more than one Charcoal process at once.")
        self.name = "ConcurrentExecutionError"


class DetachedError(GraphiteError):
    """Raised when an operation requires a branch but HEAD is detached.

    This occurs when the repository is in detached HEAD state and a command
    needs to work with a branch.
    """

    def __init__(self, extra_msg: str | None = None) -> None:
        """Initialize the error.

        Args:
            extra_msg: Optional additional context to append to the message
        """
        base_msg = "Cannot perform this operation without a branch checked out."
        message = f"{base_msg}\n{extra_msg}" if extra_msg else base_msg
        super().__init__(message)
        self.name = "DetachedError"


class NoBranchError(GraphiteError):
    """Raised when a specified branch cannot be found.

    This indicates that a branch name was provided but doesn't exist
    in the repository.
    """

    def __init__(self, branch_name: str) -> None:
        """Initialize the error.

        Args:
            branch_name: Name of the branch that wasn't found
        """
        super().__init__(f"Could not find branch {yellow(branch_name)}.")
        self.name = "NoBranchError"
        self.branch_name = branch_name


class UntrackedBranchError(GraphiteError):
    """Raised when an operation requires a tracked branch but the branch is untracked.

    Untracked branches are not part of a Graphite stack and need to be
    explicitly tracked with a parent branch before certain operations.
    """

    def __init__(self, branch_name: str) -> None:
        """Initialize the error.

        Args:
            branch_name: Name of the untracked branch
        """
        message = (
            f"Cannot perform this operation on untracked branch {yellow(branch_name)}.\n"
            f"You can track it by specifying its parent with {cyan('gt branch track')}."
        )
        super().__init__(message)
        self.name = "UntrackedBranchError"
        self.branch_name = branch_name


class BadTrunkOperationError(GraphiteError):
    """Raised when an operation that cannot be performed on trunk is attempted.

    Some operations (like deletion, rebasing, etc.) cannot be performed
    on the trunk/main branch.
    """

    def __init__(self) -> None:
        """Initialize the error with a standard message."""
        super().__init__("Cannot perform this operation on the trunk branch.")
        self.name = "BadTrunkOperationError"


class KilledError(GraphiteError):
    """Raised when a command is interrupted/killed by the user.

    This is typically triggered by Ctrl+C or other interrupt signals.
    """

    def __init__(self) -> None:
        """Initialize the error with a standard message."""
        super().__init__("Killed Charcoal early.")
        self.name = "Killed"


class BlockedDuringRebaseError(GraphiteError):
    """Raised when an operation is blocked because a rebase is in progress.

    Some commands cannot run while a git rebase is in progress and must
    wait for the rebase to be completed or aborted.
    """

    def __init__(self) -> None:
        """Initialize the error with instructions."""
        message = (
            "This operation is blocked during a rebase.\n"
            f"You may still use git directly, and continue with {cyan('gt continue')}."
        )
        super().__init__(message)
        self.name = "BlockedDuringRebase"


class NoGraphiteContinue(GraphiteError):  # noqa: N818
    """Raised when 'gt continue' is called but there's no operation to continue.

    This happens when the user runs 'gt continue' but there's no pending
    Graphite operation that needs continuation.

    Note: Name matches TypeScript implementation without 'Error' suffix.
    """

    def __init__(self, did_you_mean: str | None = None) -> None:
        """Initialize the error.

        Args:
            did_you_mean: Optional suggestion for what command the user might have meant
        """
        base_msg = "No Charcoal operation to continue."
        if did_you_mean:
            message = f"{base_msg}\nDid you mean {cyan(did_you_mean)}?"
        else:
            message = base_msg
        super().__init__(message)
        self.name = "NoGraphiteContinue"


class CommandFailedError(GraphiteError):
    """Raised when a subprocess command fails.

    This is used for git commands and other subprocess calls that exit
    with non-zero status codes.
    """

    def __init__(
        self,
        command: str,
        message: str | None = None,
        returncode: int = 1,
        **kwargs: Any,
    ) -> None:
        """Initialize the error.

        Args:
            command: The command that failed
            message: Optional error message
            returncode: The exit code of the failed command
            **kwargs: Additional context about the failure
        """
        error_msg = message or f"Command failed: {command}"
        super().__init__(error_msg)
        self.name = "CommandFailed"
        self.command = command
        self.returncode = returncode
        self.context = kwargs
