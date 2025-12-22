"""Tests for splog message() quiet mode behavior."""

import io
from unittest.mock import patch

from charcoal.lib.utils.splog import compose_splog


def test_splog_message_respects_quiet_mode() -> None:
    """Test that message() is suppressed in quiet mode."""
    splog = compose_splog(quiet=True)

    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        splog.message("This should not appear")
        output = fake_stdout.getvalue()

    # In quiet mode, message should produce no output
    assert output == ""


def test_splog_message_without_quiet_mode() -> None:
    """Test that message() works normally when not in quiet mode."""
    splog = compose_splog(quiet=False)

    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        splog.message("This should appear")
        output = fake_stdout.getvalue()

    # Without quiet mode, message should produce output
    assert "This should appear" in output
    # Should have the extra newlines
    assert "\n\n" in output
