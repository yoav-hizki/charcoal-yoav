"""Tests for the splog module."""

import io
from unittest.mock import patch

from charcoal.lib.utils.splog import Splog, compose_splog


def test_compose_splog() -> None:
    """Test creating a splog instance."""
    splog = compose_splog()
    assert isinstance(splog, Splog)
    assert splog.quiet is False
    assert splog.output_debug_logs is False
    assert splog.tips is False
    assert splog.pager is None


def test_compose_splog_with_options() -> None:
    """Test creating a splog instance with options."""
    splog = compose_splog(quiet=True, output_debug_logs=True, tips=True, pager="less")
    assert splog.quiet is True
    assert splog.output_debug_logs is True
    assert splog.tips is True
    assert splog.pager == "less"


def test_splog_info() -> None:
    """Test info output."""
    output = io.StringIO()
    splog = Splog()

    with patch("sys.stdout", output):
        splog.info("test message")

    assert output.getvalue() == "test message\n"


def test_splog_info_quiet_mode() -> None:
    """Test that info is suppressed in quiet mode."""
    output = io.StringIO()
    splog = Splog(quiet=True)

    with patch("sys.stdout", output):
        splog.info("test message")

    assert output.getvalue() == ""


def test_splog_error() -> None:
    """Test error output."""
    output = io.StringIO()
    splog = Splog()

    with patch("builtins.print") as mock_print:
        splog.error("test error")
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        assert "ERROR:" in call_args
        assert "test error" in call_args


def test_splog_warn() -> None:
    """Test warning output."""
    output = io.StringIO()
    splog = Splog()

    with patch("builtins.print") as mock_print:
        splog.warn("test warning")
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        assert "WARNING:" in call_args
        assert "test warning" in call_args


def test_splog_debug_disabled() -> None:
    """Test that debug messages are not shown by default."""
    output = io.StringIO()
    splog = Splog(output_debug_logs=False)

    with patch("sys.stdout", output):
        splog.debug("test debug")

    assert output.getvalue() == ""


def test_splog_debug_enabled() -> None:
    """Test that debug messages are shown when enabled."""
    output = io.StringIO()
    splog = Splog(output_debug_logs=True)

    with patch("builtins.print") as mock_print:
        splog.debug("test debug")
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        assert "test debug" in call_args


def test_splog_tip_disabled() -> None:
    """Test that tips are not shown when disabled."""
    output = io.StringIO()
    splog = Splog(tips=False)

    with patch("sys.stdout", output):
        splog.tip("test tip")

    assert output.getvalue() == ""


def test_splog_tip_enabled() -> None:
    """Test that tips are shown when enabled."""
    output = io.StringIO()
    splog = Splog(tips=True)

    with patch("builtins.print") as mock_print:
        splog.tip("test tip")
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        assert "tip" in call_args
        assert "test tip" in call_args
        assert "Feeling expert?" in call_args


def test_splog_tip_quiet_mode() -> None:
    """Test that tips are suppressed in quiet mode even when enabled."""
    output = io.StringIO()
    splog = Splog(tips=True, quiet=True)

    with patch("sys.stdout", output):
        splog.tip("test tip")

    assert output.getvalue() == ""


def test_splog_newline() -> None:
    """Test newline output."""
    output = io.StringIO()
    splog = Splog()

    with patch("sys.stdout", output):
        splog.newline()

    assert output.getvalue() == "\n"


def test_splog_newline_quiet_mode() -> None:
    """Test that newlines are suppressed in quiet mode."""
    output = io.StringIO()
    splog = Splog(quiet=True)

    with patch("sys.stdout", output):
        splog.newline()

    assert output.getvalue() == ""


def test_splog_message() -> None:
    """Test message output."""
    output = io.StringIO()
    splog = Splog()

    with patch("builtins.print") as mock_print:
        splog.message("test message")
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        assert "test message" in call_args


def test_splog_page_no_pager() -> None:
    """Test that page outputs directly when no pager is configured."""
    output = io.StringIO()
    splog = Splog(pager=None)

    with patch("sys.stdout", output):
        splog.page("test page content")

    assert output.getvalue() == "test page content\n"
