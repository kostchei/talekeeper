"""
Paladin Subclasses Package

Contains all Paladin sacred oath implementations.
"""

from .devotion import DevotionDefinition

# Registry of all paladin subclasses
PALADIN_SUBCLASSES = {
    'devotion': DevotionDefinition,
}

def get_paladin_subclass(subclass_name: str):
    """Get a paladin subclass definition by name."""
    return PALADIN_SUBCLASSES.get(subclass_name.lower())