"""Tests for the colors module."""

from charcoal.lib import colors


def test_graphite_colors_palette() -> None:
    """Test that GRAPHITE_COLORS has the correct number of colors."""
    assert len(colors.GRAPHITE_COLORS) == 9


def test_graphite_colors_values() -> None:
    """Test that GRAPHITE_COLORS has the correct RGB values."""
    # First color should be cyan-ish (76, 203, 241)
    assert colors.GRAPHITE_COLORS[0] == (76, 203, 241)
    # Last color should be blue-ish (80, 132, 243)
    assert colors.GRAPHITE_COLORS[8] == (80, 132, 243)


def test_rgb_to_ansi() -> None:
    """Test RGB to ANSI conversion."""
    result = colors.rgb_to_ansi(255, 0, 0)
    assert result == "\033[38;2;255;0;0m"


def test_get_graphite_color() -> None:
    """Test getting a color from the palette."""
    # Test first color
    color = colors.get_graphite_color(0)
    assert color.startswith("\033[38;2;")

    # Test wrapping around
    color_9 = colors.get_graphite_color(9)
    color_0 = colors.get_graphite_color(0)
    assert color_9 == color_0


def test_color_functions() -> None:
    """Test basic color functions."""
    text = "test"

    # Test that functions return strings with ANSI codes
    assert colors.red(text) == f"{colors.RED}{text}{colors.RESET}"
    assert colors.yellow(text) == f"{colors.YELLOW}{text}{colors.RESET}"
    assert colors.cyan(text) == f"{colors.CYAN}{text}{colors.RESET}"
    assert colors.gray(text) == f"{colors.GRAY}{text}{colors.RESET}"
    assert colors.bold(text) == f"{colors.BOLD}{text}{colors.RESET}"
    assert colors.dim(text) == f"{colors.DIM}{text}{colors.RESET}"
    assert colors.italic(text) == f"{colors.ITALIC}{text}{colors.RESET}"


def test_color_functions_are_not_empty() -> None:
    """Test that color functions actually modify the text."""
    text = "test"
    assert colors.red(text) != text
    assert colors.yellow(text) != text
    assert len(colors.red(text)) > len(text)
