"""Utility modules for Charcoal CLI.

DEPRECATED: This module is maintained for backwards compatibility only.
New code should import from charcoal.lib.colors and charcoal.lib.utils.splog instead.
"""

# Re-export from new locations for backwards compatibility
from charcoal.lib import colors  # noqa: F401
from charcoal.lib.utils.splog import (  # noqa: F401
    Splog,
    compose_splog,
    get_default_splog,
    set_default_splog,
)

__all__ = [
    "colors",
    "Splog",
    "compose_splog",
    "get_default_splog",
    "set_default_splog",
]
