"""Tests for error classes."""

from charcoal.lib.errors import (
    BadTrunkOperationError,
    BlockedDuringRebaseError,
    ConcurrentExecutionError,
    DetachedError,
    ExitFailedError,
    GraphiteError,
    KilledError,
    NoBranchError,
    NoGraphiteContinue,
    NonInteractiveError,
    PreconditionsFailedError,
    RebaseConflictError,
    UntrackedBranchError,
)


def test_graphite_error_base_class() -> None:
    """Test that GraphiteError is the base class."""
    error = GraphiteError("test error")
    assert isinstance(error, Exception)
    assert str(error) == "test error"


def test_exit_failed_error() -> None:
    """Test ExitFailedError."""
    error = ExitFailedError("command failed")
    assert isinstance(error, GraphiteError)
    assert str(error) == "command failed"
    assert error.name == "ExitFailed"


def test_non_interactive_error() -> None:
    """Test NonInteractiveError."""
    error = NonInteractiveError()
    assert isinstance(error, GraphiteError)
    assert "Cannot perform interactive operation" in str(error)
    assert error.name == "NonInteractive"


def test_rebase_conflict_error() -> None:
    """Test RebaseConflictError."""
    error = RebaseConflictError()
    assert isinstance(error, GraphiteError)
    assert "conflict during rebase" in str(error)
    assert error.name == "RebaseConflict"


def test_preconditions_failed_error() -> None:
    """Test PreconditionsFailedError."""
    error = PreconditionsFailedError("uncommitted changes")
    assert isinstance(error, GraphiteError)
    assert str(error) == "uncommitted changes"
    assert error.name == "PreconditionsFailed"


def test_concurrent_execution_error() -> None:
    """Test ConcurrentExecutionError."""
    error = ConcurrentExecutionError()
    assert isinstance(error, GraphiteError)
    assert "more than one Charcoal process" in str(error)
    assert error.name == "ConcurrentExecutionError"


def test_detached_error() -> None:
    """Test DetachedError."""
    error = DetachedError()
    assert isinstance(error, GraphiteError)
    assert "without a branch checked out" in str(error)
    assert error.name == "DetachedError"


def test_detached_error_with_extra_message() -> None:
    """Test DetachedError with extra message."""
    error = DetachedError("Please checkout a branch")
    assert isinstance(error, GraphiteError)
    assert "without a branch checked out" in str(error)
    assert "Please checkout a branch" in str(error)


def test_no_branch_error() -> None:
    """Test NoBranchError."""
    error = NoBranchError("feature-branch")
    assert isinstance(error, GraphiteError)
    assert "feature-branch" in str(error)
    assert "Could not find branch" in str(error)
    assert error.name == "NoBranchError"
    assert error.branch_name == "feature-branch"


def test_untracked_branch_error() -> None:
    """Test UntrackedBranchError."""
    error = UntrackedBranchError("my-branch")
    assert isinstance(error, GraphiteError)
    assert "my-branch" in str(error)
    assert "untracked branch" in str(error)
    assert "gt branch track" in str(error)
    assert error.name == "UntrackedBranchError"
    assert error.branch_name == "my-branch"


def test_bad_trunk_operation_error() -> None:
    """Test BadTrunkOperationError."""
    error = BadTrunkOperationError()
    assert isinstance(error, GraphiteError)
    assert "trunk branch" in str(error)
    assert error.name == "BadTrunkOperationError"


def test_killed_error() -> None:
    """Test KilledError."""
    error = KilledError()
    assert isinstance(error, GraphiteError)
    assert "Killed Charcoal early" in str(error)
    assert error.name == "Killed"


def test_blocked_during_rebase_error() -> None:
    """Test BlockedDuringRebaseError."""
    error = BlockedDuringRebaseError()
    assert isinstance(error, GraphiteError)
    assert "blocked during a rebase" in str(error)
    assert "gt continue" in str(error)
    assert error.name == "BlockedDuringRebase"


def test_no_graphite_continue() -> None:
    """Test NoGraphiteContinue."""
    error = NoGraphiteContinue()
    assert isinstance(error, GraphiteError)
    assert "No Charcoal operation to continue" in str(error)
    assert error.name == "NoGraphiteContinue"


def test_no_graphite_continue_with_suggestion() -> None:
    """Test NoGraphiteContinue with suggestion."""
    error = NoGraphiteContinue("git rebase --continue")
    assert isinstance(error, GraphiteError)
    assert "No Charcoal operation to continue" in str(error)
    assert "Did you mean" in str(error)
    assert "git rebase --continue" in str(error)
