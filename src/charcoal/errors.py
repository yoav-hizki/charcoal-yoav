"""Custom exception classes for Charcoal.

This module defines the exception hierarchy used throughout the Charcoal
application. All custom exceptions inherit from CharcoalError for easy
catching and handling.
"""


class CharcoalError(Exception):
    """Base exception class for all Charcoal-specific errors.

    All custom exceptions in Charcoal should inherit from this class
    to allow for easy catching of Charcoal-specific errors.
    """
    pass


class ExitFailedError(CharcoalError):
    """Raised when a command exits with a failure status."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class NonInteractiveError(CharcoalError):
    """Raised when attempting an interactive operation in non-interactive mode."""

    def __init__(self) -> None:
        super().__init__("Cannot perform interactive operation in non-interactive mode.")


class RebaseConflictError(CharcoalError):
    """Raised when a rebase operation encounters a conflict."""

    def __init__(self) -> None:
        super().__init__("Hit a conflict during rebase.")


class PreconditionsFailedError(CharcoalError):
    """Raised when preconditions for an operation are not met."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ConcurrentExecutionError(CharcoalError):
    """Raised when attempting to run multiple Charcoal processes simultaneously."""

    def __init__(self) -> None:
        super().__init__("Cannot run more than one Charcoal process at once.")


class DetachedError(CharcoalError):
    """Raised when attempting an operation that requires a checked out branch.

    This error occurs when the repository is in a detached HEAD state.
    """

    def __init__(self, extra_msg: str | None = None) -> None:
        base_msg = "Cannot perform this operation without a branch checked out."
        if extra_msg:
            message = f"{base_msg}\n{extra_msg}"
        else:
            message = base_msg
        super().__init__(message)


class NoBranchError(CharcoalError):
    """Raised when a specified branch cannot be found.

    Attributes:
        branch_name: The name of the branch that could not be found.
    """

    def __init__(self, branch_name: str) -> None:
        self.branch_name = branch_name
        # Note: chalk.yellow will be replaced with colors module reference in Task 3
        super().__init__(f"Could not find branch {branch_name}.")


class UntrackedBranchError(CharcoalError):
    """Raised when attempting an operation on an untracked branch.

    Attributes:
        branch_name: The name of the untracked branch.
    """

    def __init__(self, branch_name: str) -> None:
        self.branch_name = branch_name
        message = (
            f"Cannot perform this operation on untracked branch {branch_name}.\n"
            "You can track it by specifying its parent with gt branch track."
        )
        super().__init__(message)


class BadTrunkOperationError(CharcoalError):
    """Raised when attempting an operation that is not allowed on the trunk branch."""

    def __init__(self) -> None:
        super().__init__("Cannot perform this operation on the trunk branch.")


class KilledError(CharcoalError):
    """Raised when Charcoal is terminated early by the user."""

    def __init__(self) -> None:
        super().__init__("Killed Charcoal early.")


class BlockedDuringRebaseError(CharcoalError):
    """Raised when attempting an operation that is blocked during a rebase."""

    def __init__(self) -> None:
        message = (
            "This operation is blocked during a rebase.\n"
            "You may still use git directly, and continue with gt continue."
        )
        super().__init__(message)


class NoGraphiteContinue(CharcoalError):
    """Raised when there is no Charcoal operation to continue.

    Attributes:
        did_you_mean: Optional suggestion for what the user might have meant.
    """

    def __init__(self, did_you_mean: str | None = None) -> None:
        self.did_you_mean = did_you_mean
        base_msg = "No Charcoal operation to continue."
        if did_you_mean:
            message = f"{base_msg}\nDid you mean {did_you_mean}?"
        else:
            message = base_msg
        super().__init__(message)


class CommandFailedError(CharcoalError):
    """Raised when a shell command fails.

    Attributes:
        command: The command that failed.
        args: The arguments passed to the command.
        status: The exit code of the failed command.
        stdout: The standard output of the command.
        stderr: The standard error output of the command.
        errno: Optional errno value.
        code: Optional error code string.
    """

    def __init__(
        self,
        command: str,
        args: list[str],
        status: int,
        stdout: str,
        stderr: str,
        errno: int | None = None,
        code: str | None = None,
    ) -> None:
        self.command = command
        self.args = args
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.errno = errno
        self.code = code

        # Build error message
        parts = []
        if errno and code:
            parts.append(f"Command failed with error {code} ({errno}), exit code {status}:")
        else:
            parts.append(f"Command failed with error exit code {status}:")
        parts.append(" ".join([command] + args))
        if stdout:
            parts.append(stdout)
        if stderr:
            parts.append(stderr)

        super().__init__("\n".join(parts))


class CommandKilledError(CharcoalError):
    """Raised when a shell command is killed by a signal.

    Attributes:
        command: The command that was killed.
        args: The arguments passed to the command.
        signal: The signal that killed the command.
        stdout: The standard output of the command.
        stderr: The standard error output of the command.
    """

    def __init__(
        self,
        command: str,
        args: list[str],
        signal: str,
        stdout: str,
        stderr: str,
    ) -> None:
        self.command = command
        self.args = args
        self.signal = signal
        self.stdout = stdout
        self.stderr = stderr

        # Build error message
        parts = [
            f"Command killed with signal {signal}:",
            " ".join([command] + args),
        ]
        if stdout:
            parts.append(stdout)
        if stderr:
            parts.append(stderr)

        super().__init__("\n".join(parts))
