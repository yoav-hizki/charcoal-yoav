"""Color definitions and utilities for CLI output.

This module provides the color palette used throughout the CLI,
matching the TypeScript implementation's GRAPHITE_COLORS.
"""


# RGB color values matching TypeScript GRAPHITE_COLORS
# These are used for colorizing output in various commands
GRAPHITE_COLORS: list[tuple[int, int, int]] = [
    (76, 203, 241),
    (77, 202, 125),
    (110, 173, 38),
    (245, 200, 0),
    (248, 144, 72),
    (244, 98, 81),
    (235, 130, 188),
    (159, 131, 228),
    (80, 132, 243),
]


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI escape code for 24-bit color.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        ANSI escape sequence for the RGB color
    """
    return f"\033[38;2;{r};{g};{b}m"


def get_graphite_color(index: int) -> str:
    """Get a Graphite color as an ANSI escape sequence.

    Args:
        index: Index into GRAPHITE_COLORS (wraps around if out of bounds)

    Returns:
        ANSI escape sequence for the color
    """
    color_index = index % len(GRAPHITE_COLORS)
    r, g, b = GRAPHITE_COLORS[color_index]
    return rgb_to_ansi(r, g, b)


# ANSI color codes for common colors used in the CLI
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GRAY = "\033[90m"


def red(text: str) -> str:
    """Format text in red."""
    return f"{RED}{text}{RESET}"


def yellow(text: str) -> str:
    """Format text in yellow."""
    return f"{YELLOW}{text}{RESET}"


def cyan(text: str) -> str:
    """Format text in cyan."""
    return f"{CYAN}{text}{RESET}"


def gray(text: str) -> str:
    """Format text in gray."""
    return f"{GRAY}{text}{RESET}"


def dim(text: str) -> str:
    """Format text with dim/faint styling."""
    return f"{DIM}{text}{RESET}"


def bold(text: str) -> str:
    """Format text in bold."""
    return f"{BOLD}{text}{RESET}"


def italic(text: str) -> str:
    """Format text in italic."""
    return f"{ITALIC}{text}{RESET}"
